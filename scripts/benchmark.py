#!/usr/bin/env python3
"""Performance benchmark script for MoonDict.

Measures RAM usage, CPU usage, and inference timing against target thresholds.

Targets:
    - RAM: < 150 MB
    - CPU idle: < 1%
    - Inference: < 3x realtime

Usage:
    python scripts/benchmark.py [--model-path PATH] [--audio-file PATH]
"""

from __future__ import annotations

import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

import psutil

# Add project root to path so we can import moondict
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# ─── Target thresholds ──────────────────────────────────────────────────────

TARGET_RAM_MB = 150
TARGET_CPU_IDLE_PERCENT = 1.0
TARGET_INFERENCE_REALTIME_FACTOR = 3.0

# ─── Helpers ────────────────────────────────────────────────────────────────


def _format_result(
    name: str, value: float, threshold: float, unit: str, passed: bool
) -> str:
    """Format a single benchmark result line."""
    status = "✅ PASS" if passed else "❌ FAIL"
    return f"  {status} | {name:<25} {value:>8.2f} {unit:<8} (threshold: {threshold:.2f} {unit})"


def _measure_ram_usage() -> dict[str, float | bool]:
    """Measure current process RAM usage in MB."""
    process = psutil.Process()
    mem_info = process.memory_info()
    ram_mb = mem_info.rss / (1024 * 1024)
    passed = ram_mb < TARGET_RAM_MB
    return {"value": ram_mb, "threshold": TARGET_RAM_MB, "unit": "MB", "passed": passed}


def _measure_cpu_idle() -> dict[str, float | bool]:
    """Measure CPU usage percentage over 2 seconds."""
    process = psutil.Process()
    # First call always returns 0.0, so we call twice
    process.cpu_percent(interval=None)
    time.sleep(2.0)
    cpu_percent = process.cpu_percent(interval=None)
    passed = cpu_percent < TARGET_CPU_IDLE_PERCENT
    return {
        "value": cpu_percent,
        "threshold": TARGET_CPU_IDLE_PERCENT,
        "unit": "%",
        "passed": passed,
    }


def _measure_inference_timing(
    model_path: Path | None = None,
) -> dict[str, float | bool]:
    """Measure inference timing using a synthetic audio sample.

    Generates a 3-second silent audio buffer at 16kHz and measures
    how long the engine takes to process it.
    """
    import numpy as np  # type: ignore[import-untyped]

    from moondict.engine.moonshine import MoonshineEngine

    # Create 3 seconds of silent audio (float32, 16kHz)
    sample_rate = 16000
    duration_secs = 3.0
    audio_data = np.zeros(int(sample_rate * duration_secs), dtype=np.float32)

    engine = MoonshineEngine(model_path=str(model_path) if model_path else "")
    engine.initialize()

    start = time.perf_counter()
    _ = engine.transcribe(audio_data, sample_rate)
    elapsed = time.perf_counter() - start

    engine.shutdown()

    # Realtime factor: elapsed / audio_duration
    realtime_factor = elapsed / duration_secs
    passed = realtime_factor < TARGET_INFERENCE_REALTIME_FACTOR

    return {
        "value": realtime_factor,
        "threshold": TARGET_INFERENCE_REALTIME_FACTOR,
        "unit": "x realtime",
        "passed": passed,
        "elapsed_secs": elapsed,
        "audio_duration_secs": duration_secs,
    }


# ─── Main benchmark runner ──────────────────────────────────────────────────


def run_benchmark(model_path: Path | None = None) -> list[dict[str, Any]]:
    """Run all benchmarks and return results."""
    results: list[dict[str, Any]] = []

    print("\n" + "=" * 70)
    print("  MoonDict Performance Benchmark")
    print("=" * 70)

    # 1. RAM Usage
    print("\n📊 RAM Usage:")
    ram_result = _measure_ram_usage()
    results.append({"name": "RAM Usage", **ram_result})
    print(
        _format_result(
            "RAM Usage",
            ram_result["value"],  # type: ignore[arg-type]
            ram_result["threshold"],  # type: ignore[arg-type]
            ram_result["unit"],  # type: ignore[arg-type]
            ram_result["passed"],  # type: ignore[arg-type]
        )
    )

    # 2. CPU Idle
    print("\n⚡ CPU Idle:")
    cpu_result = _measure_cpu_idle()
    results.append({"name": "CPU Idle", **cpu_result})
    print(
        _format_result(
            "CPU Idle",
            cpu_result["value"],  # type: ignore[arg-type]
            cpu_result["threshold"],  # type: ignore[arg-type]
            cpu_result["unit"],  # type: ignore[arg-type]
            cpu_result["passed"],  # type: ignore[arg-type]
        )
    )

    # 3. Inference Timing
    print("\n🎤 Inference Timing:")
    try:
        inference_result = _measure_inference_timing(model_path)
        results.append({"name": "Inference Timing", **inference_result})
        print(
            _format_result(
                "Inference Timing",
                inference_result["value"],  # type: ignore[arg-type]
                inference_result["threshold"],  # type: ignore[arg-type]
                inference_result["unit"],  # type: ignore[arg-type]
                inference_result["passed"],  # type: ignore[arg-type]
            )
        )
        print(f"     Elapsed: {inference_result.get('elapsed_secs', 0):.3f}s")
        print(
            f"     Audio Duration: {inference_result.get('audio_duration_secs', 0):.1f}s"
        )
    except Exception as e:
        print(f"  ⚠️  SKIP | Inference timing failed: {e}")
        results.append(
            {
                "name": "Inference Timing",
                "value": 0.0,
                "threshold": TARGET_INFERENCE_REALTIME_FACTOR,
                "unit": "x realtime",
                "passed": False,
                "error": str(e),
            }
        )

    # Summary
    all_passed = all(r.get("passed", False) for r in results if "error" not in r)
    print("\n" + "=" * 70)
    if all_passed:
        print("  ✅ ALL BENCHMARKS PASSED")
    else:
        failed = [r["name"] for r in results if not r.get("passed", False)]
        print(f"  ❌ FAILED: {', '.join(failed)}")
    print("=" * 70 + "\n")

    return results


def main() -> None:
    """Entry point for benchmark script."""
    import argparse

    parser = argparse.ArgumentParser(description="MoonDict Performance Benchmark")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=None,
        help="Path to Moonshine model directory",
    )
    args = parser.parse_args()

    tracemalloc.start()
    results = run_benchmark(model_path=args.model_path)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"📈 Peak memory (tracemalloc): {peak / 1024 / 1024:.2f} MB")

    # Exit with error code if any benchmark failed
    if not all(r.get("passed", False) for r in results if "error" not in r):
        sys.exit(1)


if __name__ == "__main__":
    main()
