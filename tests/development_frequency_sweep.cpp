// SPDX-License-Identifier: MIT
#include <SoapySDR/Device.hpp>
#include <SoapySDR/Formats.hpp>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <chrono>
#include <cmath>
#include <complex>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <linux/rp1_gpclk.h>

namespace {
constexpr long double kNominalParentHz = 50000000.0L;
constexpr uint32_t kDitherPeriod = 66792U;
constexpr double kMinimumHz = 135700.0;
constexpr double kMaximumHz = 148000000.0;
constexpr unsigned kDefaultPoints = 16;
constexpr double kSampleRate = 250000.0;
constexpr double kTuneOffsetHz = 100000.0;
constexpr uint64_t kToneDurationNs = 2000000000ULL;
constexpr size_t kFftSize = 262144;

struct Options {
	bool live = false;
	unsigned points = kDefaultPoints;
	unsigned repeats = 1;
	long double source_ppm = 0.0L;
	long double receiver_ppm = 0.0L;
	std::string output = "-";
};
struct Plan {
	double requested_hz;
	double fundamental_hz;
	unsigned harmonic;
	double planned_fundamental_hz;
	double planned_rf_hz;
	rp1_gpclk_tone_v1 tone;
};
struct Measurement { double raw_hz; double level_dbfs; size_t samples; };

[[noreturn]] void usage(const char *program, const std::string &error = {})
{
	if (!error.empty()) fprintf(stderr, "%s\n", error.c_str());
	fprintf(stderr, "usage: %s [--render-only|--live] [--points 2..101] "
		"[--repeats N] [--source-rate-ppm PPM] [--receiver-ppm PPM] "
		"[--output PATH|-]\n", program);
	exit(error.empty() ? 0 : 2);
}
long double number(const char *text, const char *label)
{
	char *end = nullptr;
	const long double value = strtold(text, &end);
	if (!end || *end || !std::isfinite(value))
		throw std::runtime_error(std::string("invalid ") + label);
	return value;
}
unsigned whole(const char *text, const char *label)
{
	char *end = nullptr;
	const unsigned long value = strtoul(text, &end, 10);
	if (!end || *end || value > UINT32_MAX)
		throw std::runtime_error(std::string("invalid ") + label);
	return static_cast<unsigned>(value);
}
Options options(int argc, char **argv)
{
	Options out;
	for (int i = 1; i < argc; ++i) {
		const std::string arg = argv[i];
		auto next = [&](const char *label) {
			if (++i >= argc) usage(argv[0], std::string("missing ") + label);
			return argv[i];
		};
		if (arg == "--render-only") out.live = false;
		else if (arg == "--live") out.live = true;
		else if (arg == "--points") out.points = whole(next("points"), "points");
		else if (arg == "--repeats") out.repeats = whole(next("repeats"), "repeats");
		else if (arg == "--source-rate-ppm") out.source_ppm = number(next("source PPM"), "source PPM");
		else if (arg == "--receiver-ppm") out.receiver_ppm = number(next("receiver PPM"), "receiver PPM");
		else if (arg == "--output") out.output = next("output");
		else if (arg == "--help") usage(argv[0]);
		else usage(argv[0], "unknown option: " + arg);
	}
	if (out.points < 2 || out.points > 101) usage(argv[0], "points must be 2..101");
	if (!out.repeats || out.repeats > 100) usage(argv[0], "repeats must be 1..100");
	if (fabsl(out.source_ppm) > 200 || fabsl(out.receiver_ppm) > 200)
		usage(argv[0], "PPM values must be within +/-200");
	return out;
}
void set_header(rp1_gpclk_uapi_header &header, size_t size, uint16_t version)
{
	header.size = static_cast<uint16_t>(size);
	header.version = version;
}
Plan plan(double requested, long double parent)
{
	Plan out{};
	out.requested_hz = requested;
	out.harmonic = requested > static_cast<double>(kNominalParentHz) ? 3U : 1U;
	out.fundamental_hz = requested / out.harmonic;
	const long double ideal = parent * 65536.0L / out.fundamental_hz;
	if (ideal < 65536.0L || ideal > 4294967295.0L)
		throw std::runtime_error("divider outside GPCLK0 Q16 field");
	const uint64_t lower = static_cast<uint64_t>(floorl(ideal));
	if (lower == 0xffffffffULL || (lower >> 16) != ((lower + 1) >> 16))
		throw std::runtime_error("adjacent divider crosses integer field");
	const long double low_hz = parent * 65536.0L / lower;
	const long double high_div_hz = parent * 65536.0L / (lower + 1);
	const long double ratio = (out.fundamental_hz - high_div_hz) /
		(low_hz - high_div_hz);
	out.tone.lower_divider_q16 = lower;
	out.tone.upper_divider_q16 = lower + 1;
	out.tone.lower_count = static_cast<uint32_t>(llroundl(ratio * kDitherPeriod));
	if (!out.tone.lower_count) out.tone.lower_count = 1;
	if (out.tone.lower_count >= kDitherPeriod) out.tone.lower_count = kDitherPeriod - 1;
	out.tone.upper_count = kDitherPeriod - out.tone.lower_count;
	out.planned_fundamental_hz = static_cast<double>((low_hz * out.tone.lower_count +
		high_div_hz * out.tone.upper_count) / kDitherPeriod);
	out.planned_rf_hz = out.planned_fundamental_hz * out.harmonic;
	return out;
}
void checked_ioctl(int fd, unsigned long command, void *value, const char *name)
{
	if (ioctl(fd, command, value))
		throw std::runtime_error(std::string(name) + ": " + strerror(errno));
}
class Endpoint {
public:
	Endpoint() : fd_(open("/dev/rp1-gpclk", O_RDONLY | O_CLOEXEC))
	{
		if (fd_ < 0) throw std::runtime_error(std::string("open: ") + strerror(errno));
	}
	~Endpoint() { if (fd_ >= 0) close(fd_); }
	void transmit(const rp1_gpclk_tone_v1 &tone, double requested)
	{
		rp1_gpclk_query_v2 query{};
		rp1_gpclk_acquire_v4 acquire{};
		rp1_gpclk_submit_tone_v2 submit{};
		rp1_gpclk_state_v1 state{};
		rp1_gpclk_release_v2 release{};
		set_header(query.header, sizeof(query), RP1_GPCLK_UAPI_ABI_V2);
		checked_ioctl(fd_, RP1_GPCLK_IOC_QUERY_V2, &query, "QUERY_V2");
		if (query.route != RP1_GPCLK_ROUTE_GPIO20 || !query.build_id[0] ||
		    !query.compatibility_id[0])
			throw std::runtime_error("GPIO20 development identity unavailable");
		set_header(acquire.header, sizeof(acquire), RP1_GPCLK_UAPI_ABI_V4);
		acquire.expected_route = RP1_GPCLK_ROUTE_GPIO20;
		acquire.authorization_flags = RP1_GPCLK_ACQUIRE_V4_F_AUTHORIZE_LIVE;
		acquire.required_capabilities = RP1_GPCLK_CAP_LIVE_ELIGIBLE |
			RP1_GPCLK_CAP_OPERATION_LIVE_GATE | RP1_GPCLK_CAP_TONE_FINITE;
		for (size_t i = 0; i < sizeof(acquire.authorization_digest); ++i)
			acquire.authorization_digest[i] = static_cast<uint8_t>(0x5aU ^ i ^
				static_cast<uint64_t>(llround(requested)));
		checked_ioctl(fd_, RP1_GPCLK_IOC_ACQUIRE_V4, &acquire, "ACQUIRE_V4");
		set_header(submit.header, sizeof(submit), RP1_GPCLK_UAPI_ABI_V2);
		submit.lease_id = acquire.lease_id;
		submit.tone = tone;
		submit.duration_ns = kToneDurationNs;
		submit.operation = RP1_GPCLK_TONE_OPERATION_FINITE;
		submit.expected_route = RP1_GPCLK_ROUTE_GPIO20;
		submit.fractional_bits = RP1_GPCLK_FRACTIONAL_BITS;
		submit.tick_divider = RP1_GPCLK_TICK_DIVIDER;
		submit.drive_ma = RP1_GPCLK_DRIVE_MA_2;
		checked_ioctl(fd_, RP1_GPCLK_IOC_SUBMIT_TONE_V2, &submit, "TONE_V2");
		for (;;) {
			std::this_thread::sleep_for(std::chrono::milliseconds(10));
			state = {};
			set_header(state.header, sizeof(state), RP1_GPCLK_UAPI_ABI_V1);
			state.lease_id = acquire.lease_id;
			state.generation = submit.generation;
			checked_ioctl(fd_, RP1_GPCLK_IOC_GET_STATE, &state, "GET_STATE");
			if (state.state == RP1_GPCLK_STATE_COMPLETE || state.state == RP1_GPCLK_STATE_FAILED) break;
		}
		if (state.state != RP1_GPCLK_STATE_COMPLETE || state.cleanup_fault ||
		    state.terminal_reason != RP1_GPCLK_REASON_COMPLETE)
			throw std::runtime_error("finite tone did not complete cleanly");
		set_header(release.header, sizeof(release), RP1_GPCLK_UAPI_ABI_V2);
		release.lease_id = acquire.lease_id;
		release.generation = submit.generation;
		for (unsigned attempt = 0;; ++attempt) {
			if (!ioctl(fd_, RP1_GPCLK_IOC_RELEASE_V2, &release))
				break;
			if (errno != EALREADY || attempt == 49)
				throw std::runtime_error(std::string("RELEASE_V2: ") +
					strerror(errno));
			std::this_thread::sleep_for(std::chrono::milliseconds(10));
		}
	}
private: int fd_;
};
void fft(std::vector<std::complex<double>> &v)
{
	for (size_t i = 1, j = 0; i < v.size(); ++i) {
		size_t bit = v.size() >> 1;
		for (; j & bit; bit >>= 1) j ^= bit;
		j ^= bit;
		if (i < j) std::swap(v[i], v[j]);
	}
	for (size_t len = 2; len <= v.size(); len <<= 1) {
		const auto step = std::polar(1.0, -2.0 * M_PI / len);
		for (size_t start = 0; start < v.size(); start += len) {
			std::complex<double> phase(1, 0);
			for (size_t off = 0; off < len / 2; ++off) {
				const auto even = v[start + off];
				const auto odd = v[start + off + len / 2] * phase;
				v[start + off] = even + odd;
				v[start + off + len / 2] = even - odd;
				phase *= step;
			}
		}
	}
}
Measurement capture(SoapySDR::Device *sdr, Endpoint &endpoint, const Plan &p)
{
	const double center = p.requested_hz > kTuneOffsetHz + kSampleRate / 2 ?
		p.requested_hz - kTuneOffsetHz : p.requested_hz + kTuneOffsetHz;
	const double expected = p.requested_hz - center;
	std::vector<std::complex<float>> buffer(16384);
	std::vector<std::complex<double>> samples;
	long double power = 0;
	size_t accepted = 0;
	std::exception_ptr tx_error;
	samples.reserve(kFftSize);
	sdr->setSampleRate(SOAPY_SDR_RX, 0, kSampleRate);
	sdr->setBandwidth(SOAPY_SDR_RX, 0, 200000);
	sdr->setFrequency(SOAPY_SDR_RX, 0, center);
	sdr->setGainMode(SOAPY_SDR_RX, 0, false);
	sdr->setGain(SOAPY_SDR_RX, 0, 0);
	auto *stream = sdr->setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32);
	sdr->activateStream(stream);
	std::thread tx([&]() { try { std::this_thread::sleep_for(std::chrono::milliseconds(250));
		endpoint.transmit(p.tone, p.requested_hz); } catch (...) { tx_error = std::current_exception(); } });
	try {
		const size_t discard = static_cast<size_t>(kSampleRate * .45);
		size_t received = 0;
		while (accepted < kFftSize) {
			void *buffers[] = {buffer.data()}; int flags = 0; long long time_ns = 0;
			const int count = sdr->readStream(stream, buffers, buffer.size(), flags, time_ns, 1000000);
			if (count < 0) throw std::runtime_error("SDR read failed: " + std::to_string(count));
			for (int i = 0; i < count && accepted < kFftSize; ++i, ++received) {
				if (received < discard) continue;
				const auto s = buffer[static_cast<size_t>(i)];
				samples.emplace_back(s.real(), s.imag()); power += std::norm(s); ++accepted;
			}
		}
		tx.join(); if (tx_error) std::rethrow_exception(tx_error);
	} catch (...) { if (tx.joinable()) tx.join(); sdr->deactivateStream(stream); sdr->closeStream(stream); throw; }
	sdr->deactivateStream(stream); sdr->closeStream(stream);
	for (size_t i = 0; i < samples.size(); ++i)
		samples[i] *= .5 - .5 * cos(2 * M_PI * i / (samples.size() - 1));
	fft(samples);
	const long expected_signed = lround(expected * kFftSize / kSampleRate);
	const size_t expected_bin = expected_signed >= 0 ? static_cast<size_t>(expected_signed) :
		static_cast<size_t>(static_cast<long>(kFftSize) + expected_signed);
	const size_t search = static_cast<size_t>(20000 * kFftSize / kSampleRate);
	size_t peak = expected_bin; double peak_power = 0;
	for (long off = -static_cast<long>(search); off <= static_cast<long>(search); ++off) {
		const size_t bin = (expected_bin + kFftSize + off) % kFftSize;
		if (std::norm(samples[bin]) > peak_power) { peak_power = std::norm(samples[bin]); peak = bin; }
	}
	const long signed_bin = peak <= kFftSize / 2 ? static_cast<long>(peak) : static_cast<long>(peak) - kFftSize;
	const double left = std::norm(samples[(peak + kFftSize - 1) % kFftSize]);
	const double mid = std::norm(samples[peak]); const double right = std::norm(samples[(peak + 1) % kFftSize]);
	const double denom = left - 2 * mid + right;
	const double frac = denom == 0 ? 0 : .5 * (left - right) / denom;
	return {center + (signed_bin + frac) * kSampleRate / kFftSize,
		10 * log10(static_cast<double>(power / accepted)), accepted};
}
void header(FILE *out)
{
	fprintf(out, "repeat,index,requested_rf_hz,fundamental_hz,harmonic,planned_fundamental_hz,planned_rf_hz,lower_divider_q16,upper_divider_q16,lower_count,upper_count,raw_sdr_hz,corrected_sdr_hz,error_hz,error_ppm,level_dbfs,samples,status\n");
}
}
int main(int argc, char **argv)
{
	try {
		const Options o = options(argc, argv);
		const long double parent = kNominalParentHz * (1 + o.source_ppm * 1e-6L);
		FILE *out = o.output == "-" ? stdout : fopen(o.output.c_str(), "w");
		if (!out) throw std::runtime_error("cannot open output");
		SoapySDR::Device *sdr = nullptr;
		if (o.live) { SoapySDR::Kwargs a; a["driver"] = "sdrplay"; a["serial"] = "2404058C60";
			sdr = SoapySDR::Device::make(a); if (!sdr) throw std::runtime_error("SDRplay unavailable"); }
		header(out);
		for (unsigned repeat = 1; repeat <= o.repeats; ++repeat) for (unsigned index = 0; index < o.points; ++index) {
			const double requested = kMinimumHz + (kMaximumHz - kMinimumHz) * index / (o.points - 1);
			try {
				const Plan p = plan(requested, parent);
				if (!o.live) fprintf(out, "%u,%u,%.6f,%.6f,%u,%.9f,%.9f,%llu,%llu,%u,%u,,,,,,,planned\n", repeat, index, p.requested_hz, p.fundamental_hz, p.harmonic, p.planned_fundamental_hz, p.planned_rf_hz, static_cast<unsigned long long>(p.tone.lower_divider_q16), static_cast<unsigned long long>(p.tone.upper_divider_q16), p.tone.lower_count, p.tone.upper_count);
				else { Endpoint endpoint; const Measurement m = capture(sdr, endpoint, p); const double corrected = m.raw_hz / (1 + static_cast<double>(o.receiver_ppm) * 1e-6); const double error = corrected - requested;
					fprintf(out, "%u,%u,%.6f,%.6f,%u,%.9f,%.9f,%llu,%llu,%u,%u,%.9f,%.9f,%.9f,%.9f,%.2f,%zu,measured\n", repeat, index, p.requested_hz, p.fundamental_hz, p.harmonic, p.planned_fundamental_hz, p.planned_rf_hz, static_cast<unsigned long long>(p.tone.lower_divider_q16), static_cast<unsigned long long>(p.tone.upper_divider_q16), p.tone.lower_count, p.tone.upper_count, m.raw_hz, corrected, error, error * 1e6 / requested, m.level_dbfs, m.samples); }
			} catch (const std::exception &e) { fprintf(out, "%u,%u,%.6f,,,,,,,,,,,,,,,,rejected:%s\n", repeat, index, requested, e.what()); }
			fflush(out);
		}
		if (sdr) SoapySDR::Device::unmake(sdr);
		if (out != stdout && fclose(out)) throw std::runtime_error("cannot close output");
	} catch (const std::exception &e) { fprintf(stderr, "frequency sweep failed: %s\n", e.what()); return 1; }
	return 0;
}
