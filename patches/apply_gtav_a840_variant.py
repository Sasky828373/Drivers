#!/usr/bin/env python3
"""
GTAV/A840 variant: performance-oriented Turnip autotune without forcing KGSL
PWR_MAX or disabling the governor.

Keeps normal Android/KGSL power management and all WinNative compatibility
patches. The first experiment changes only the GMEM autotuner policy so an A/B
test against Balanced measures driver scheduling/render-mode policy rather than
forced clocks.
"""
import sys

AUTOTUNE_FILE = "src/freedreno/vulkan/tu_autotune.cc"

with open(AUTOTUNE_FILE, "r") as f:
    content = f.read()

changed = False

# Match WN Performance's drawcall threshold, but deliberately do not apply any
# of apply_perf_variant.py's KGSL power-constraint changes.
old_dc = "if (cmd_buffer->state.rp.drawcall_count > 5)"
new_dc = "if (cmd_buffer->state.rp.drawcall_count > 10)"
if new_dc in content:
    print(f"  {AUTOTUNE_FILE}: GTAV drawcall threshold already at 10")
elif old_dc in content:
    content = content.replace(old_dc, new_dc, 1)
    changed = True
    print(f"  {AUTOTUNE_FILE}: GTAV drawcall threshold 5 -> 10")
else:
    print(f"  WARNING: {AUTOTUNE_FILE}: drawcall threshold anchor absent", file=sys.stderr)

# V2: Prefer Mesa's measured render-pass profiler for GTA V. An explicit
# TU_AUTOTUNE_ALGO environment setting still overrides this default.
old_algo = "algorithm algo = algorithm::DEFAULT;"
new_algo = "algorithm algo = algorithm::PROFILED;"
if new_algo in content:
    print(f"  {AUTOTUNE_FILE}: GTAV default algorithm already PROFILED")
elif old_algo in content:
    content = content.replace(old_algo, new_algo, 1)
    changed = True
    print(f"  {AUTOTUNE_FILE}: GTAV default algorithm DEFAULT -> PROFILED")
else:
    print(f"  WARNING: {AUTOTUNE_FILE}: default algorithm anchor absent", file=sys.stderr)

# Keep WN's reduced historical weighting so the autotuner reacts faster to the
# current render pass workload.
old_bw = "gmem_bandwidth = (gmem_bandwidth * 11 + total_draw_call_bandwidth) / 10;"
new_bw = "gmem_bandwidth = (gmem_bandwidth * 10 + total_draw_call_bandwidth) / 10;"
if old_bw in content:
    content = content.replace(old_bw, new_bw, 1)
    changed = True
    print(f"  {AUTOTUNE_FILE}: GTAV bandwidth history 11 -> 10")
elif "* 10 + total_draw_call_bandwidth" in content:
    print(f"  {AUTOTUNE_FILE}: GTAV bandwidth history already 10")
else:
    print(f"  WARNING: {AUTOTUNE_FILE}: bandwidth anchor absent", file=sys.stderr)

if changed:
    with open(AUTOTUNE_FILE, "w") as f:
        f.write(content)

print("apply_gtav_a840_variant.py: V2 done (PROFILED + bandwidth tuning, no PWR_MAX)")
