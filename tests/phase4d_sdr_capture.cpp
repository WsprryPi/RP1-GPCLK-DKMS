// SPDX-License-Identifier: MIT

#include <SoapySDR/Device.hpp>
#include <SoapySDR/Formats.hpp>
#include <SoapySDR/Logger.hpp>
#include <SoapySDR/Time.hpp>
#include <chrono>
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char **argv)
{
    if (argc != 3 && argc != 4) {
        std::cerr << "usage: " << argv[0] << " OUTPUT.cf32 SECONDS [READY]\n";
        return EXIT_FAILURE;
    }
    const double seconds = std::stod(argv[2]);
    if (!(seconds > 0.0 && seconds <= 120.0)) return EXIT_FAILURE;
    SoapySDR::Kwargs args;
    args["driver"] = "remote";
    args["remote"] = "tcp://127.0.0.1:55132";
    args["remote:driver"] = "sdrplay";
    args["serial"] = "2404058C60";
    SoapySDR::Device *device = nullptr;
    SoapySDR::Stream *stream = nullptr;
    try {
        device = SoapySDR::Device::make(args);
        if (!device) throw std::runtime_error("RSP1B open failed");
        device->setSampleRate(SOAPY_SDR_RX, 0, 192000.0);
        device->setFrequency(SOAPY_SDR_RX, 0, 10135200.0);
        device->setBandwidth(SOAPY_SDR_RX, 0, 200000.0);
        device->setGainMode(SOAPY_SDR_RX, 0, false);
        device->setGain(SOAPY_SDR_RX, 0, 0.0);
        stream = device->setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32);
        device->activateStream(stream);
        if (argc == 4) {
            std::ofstream ready(argv[3], std::ios::trunc);
            if (!ready) throw std::runtime_error("ready marker open failed");
            ready << "ready\n";
        }
        const std::size_t wanted = static_cast<std::size_t>(seconds * 192000.0);
        std::vector<std::complex<float>> block(8192);
        std::ofstream output(argv[1], std::ios::binary | std::ios::trunc);
        if (!output) throw std::runtime_error("capture output open failed");
        std::size_t received = 0;
        const auto started = std::chrono::steady_clock::now();
        while (received < wanted) {
            void *buffers[] = { block.data() };
            int flags = 0;
            long long time_ns = 0;
            const auto count = std::min(block.size(), wanted - received);
            const int got = device->readStream(stream, buffers, count, flags,
                                               time_ns, 1000000L);
            if (got == SOAPY_SDR_TIMEOUT) continue;
            if (got < 0) throw std::runtime_error(
                "SoapySDR read error " + std::to_string(got));
            output.write(reinterpret_cast<const char *>(block.data()),
                         got * sizeof(block[0]));
            received += static_cast<std::size_t>(got);
        }
        const auto finished = std::chrono::steady_clock::now();
        device->deactivateStream(stream);
        device->closeStream(stream);
        stream = nullptr;
        std::cout << "samples=" << received << " rate=192000 center=10135200"
                  << " gain=0 agc=off bandwidth=200000 elapsed_ns="
                  << std::chrono::duration_cast<std::chrono::nanoseconds>(
                         finished - started).count() << "\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        if (stream) { device->deactivateStream(stream); device->closeStream(stream); }
        if (device) SoapySDR::Device::unmake(device);
        return EXIT_FAILURE;
    }
    SoapySDR::Device::unmake(device);
    return EXIT_SUCCESS;
}
