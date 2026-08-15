#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reproduce Phase 4B GPIO4 duration and relative-tone decisions from CF32 IQ."""

import argparse
from pathlib import Path

import numpy as np

RATE = 192000
WINDOW = RATE // 200  # 5 ms


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

    print("PHASE4B_ANALYSIS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
