#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reproduce Phase 4D GPIO20 duration and relative-tone decisions from CF32 IQ."""

import argparse
from pathlib import Path

import numpy as np

RATE = 192000
WINDOW = RATE // 200  # 5 ms
WSPR_SYMBOLS = np.asarray([
    int(value) for value in
    "132000023020111000302321113000022230012300222012112033210003103022"
    "213010303230030032332021321030223220203223221310310213010221110002"
    "210302110200222310303320011002"
])
WSPR_SECONDS = 110.592
WSPR_SPACING = 12000.0 / 8192.0


def samples(path: Path) -> np.ndarray:
    return np.fromfile(path, dtype=np.complex64)


def active_windows(iq: np.ndarray) -> np.ndarray:
    count = len(iq) // WINDOW
    rms = np.sqrt(np.mean(np.abs(iq[: count * WINDOW].reshape(count, WINDOW)) ** 2, axis=1))
    # Readiness confirms streaming, not a fixed pre-burst delay. Select the
    # quiet distribution across the capture so an early burst cannot poison
    # the noise-floor estimate.
    baseline = np.percentile(rms, 20)
    raw = rms >= baseline * (10.0 ** (12.0 / 20.0))
    return np.convolve(raw.astype(int), np.ones(3, dtype=int), mode="same") >= 3


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    edges = np.diff(np.pad(mask.astype(int), (1, 1)))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def peak(iq: np.ndarray, first: int, last: int) -> float:
    segment = iq[first * WINDOW:last * WINDOW]
    spectrum = np.fft.fftshift(np.fft.fft(segment * np.hanning(len(segment)), 1 << 19))
    frequencies = np.fft.fftshift(np.fft.fftfreq(len(spectrum), 1.0 / RATE))
    return float(frequencies[np.argmax(np.abs(spectrum))])


def wspr_frequency(segment: np.ndarray) -> float:
    """Estimate one symbol spectrally within the proven conducted-carrier band."""
    margin = len(segment) // 10
    active = segment[margin:-margin]
    size = 1 << 18
    spectrum = np.fft.fft(active * np.hanning(len(active)), size)
    frequencies = np.fft.fftfreq(size, 1.0 / RATE)
    allowed = np.flatnonzero((frequencies >= 4500.0) & (frequencies <= 5500.0))
    index = int(allowed[np.argmax(np.abs(spectrum[allowed]))])
    magnitude = np.log(np.maximum(np.abs(spectrum[index - 1:index + 2]), 1e-30))
    correction = 0.5 * (magnitude[0] - magnitude[2]) / \
        (magnitude[0] - 2.0 * magnitude[1] + magnitude[2])
    return float((index + correction) * RATE / size)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    root = args.directory

    durations = []
    for path in sorted(root.glob("qrss-??.cf32")):
        detected = runs(active_windows(samples(path)))
        if len(detected) != 1:
            raise SystemExit(f"{path.name}: expected one run, got {detected}")
        durations.append((detected[0][1] - detected[0][0]) / 200.0)
    if len(durations) != 10:
        raise SystemExit(f"expected 10 QRSS captures, got {len(durations)}")
    print("QRSS durations", durations)
    print("QRSS median", np.median(durations), "p95", np.percentile(durations, 95),
          "max_error", max(abs(np.asarray(durations) - 1.0)),
          "stddev", np.std(durations), "ptp", np.ptp(durations))
    if max(abs(np.asarray(durations) - 1.0)) > 0.050 or np.std(durations) > 0.025 or np.ptp(durations) > 0.075:
        raise SystemExit("QRSS limits failed")

    for name, expected_runs in (("fskcw", 1), ("dfcw", 4), ("cancel", 1)):
        iq = samples(root / f"{name}.cf32")
        detected = runs(active_windows(iq))
        if len(detected) != expected_runs:
            raise SystemExit(f"{name}: expected {expected_runs} runs, got {detected}")
        durations = [(last - first) / 200.0 for first, last in detected]
        print(name.upper(), "runs", detected, "durations", durations)
        if name == "fskcw":
            start = detected[0][0]
            seconds = [(start + i * 200, start + (i + 1) * 200) for i in range(6)]
            peaks = [peak(iq, first, last) for first, last in seconds]
            spacing = np.diff(peaks)
            print("FSKCW peaks", peaks, "spacing", spacing.tolist())
            if any(abs(abs(value) - 20.0) > 3.0 for value in spacing):
                raise SystemExit("FSKCW spacing failed")
        elif name == "dfcw":
            peaks = [peak(iq, first, last) for first, last in detected]
            spacing = np.diff(peaks)
            gaps = [(detected[i + 1][0] - detected[i][1]) / 200.0 for i in range(3)]
            print("DFCW peaks", peaks, "spacing", spacing.tolist(), "gaps", gaps)
            if any(abs(abs(value) - 20.0) > 3.0 for value in spacing):
                raise SystemExit("DFCW spacing failed")
            if any(abs(value - 0.5) > 0.050 for value in gaps):
                raise SystemExit("DFCW gap failed")
        elif durations[0] > 1.15:
            raise SystemExit("cancellation drain failed")

    wspr_iq = samples(root / "wspr.cf32")
    count = len(wspr_iq) // WINDOW
    rms = np.sqrt(np.mean(np.abs(wspr_iq[: count * WINDOW].reshape(count, WINDOW)) ** 2, axis=1))
    baseline = np.percentile(rms, 2)
    wspr_mask = np.convolve(
        (rms >= baseline * (10.0 ** (12.0 / 20.0))).astype(int),
        np.ones(3, dtype=int), mode="same") >= 3
    detected = runs(wspr_mask)
    if len(detected) != 1:
        raise SystemExit(f"WSPR: expected one continuous run, got {detected}")
    first, last = detected[0]
    duration = (last - first) / 200.0
    print("WSPR run", detected[0], "duration", duration)
    if abs(duration - WSPR_SECONDS) > 0.100:
        raise SystemExit("WSPR frame duration failed")

    start = first * WINDOW
    symbol_samples = WSPR_SECONDS * RATE / len(WSPR_SYMBOLS)
    observed = []
    for index in range(len(WSPR_SYMBOLS)):
        left = start + int(round(index * symbol_samples))
        right = start + int(round((index + 1) * symbol_samples))
        observed.append(wspr_frequency(wspr_iq[left:right]))
    observed = np.asarray(observed)
    time_axis = np.arange(len(observed), dtype=float)
    design = np.column_stack((np.ones(len(observed)), WSPR_SYMBOLS, time_axis))
    base, spacing, drift = np.linalg.lstsq(design, observed, rcond=None)[0]
    fitted = design @ np.asarray((base, spacing, drift))
    residual = observed - fitted
    classified = np.rint((observed - base - drift * time_axis) / spacing).astype(int)
    errors = int(np.count_nonzero(classified != WSPR_SYMBOLS))
    print("WSPR base", base, "spacing", spacing, "drift_per_symbol", drift,
          "max_residual", float(np.max(np.abs(residual))),
          "symbol_errors", errors)
    if abs(abs(spacing) - WSPR_SPACING) > 0.30:
        raise SystemExit("WSPR tone spacing failed")
    if errors or np.max(np.abs(residual)) > abs(spacing) / 2.0:
        raise SystemExit("WSPR symbol sequence failed")

    print("PHASE4D_ANALYSIS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
