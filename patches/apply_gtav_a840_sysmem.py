#!/usr/bin/env python3
"""GTAV/A840 A/B: proven GMEM history 10 + prefer SYSMEM autotune.
No PWR_MAX, no governor override, no PROFILED, no hard TU_DEBUG=sysmem.
"""
import sys
p = "src/freedreno/vulkan/tu_autotune.cc"
with open(p, "r") as f:
    s = f.read()
changed = False

old_algo = "algorithm algo = algorithm::DEFAULT;"
new_algo = "algorithm algo = algorithm::PREFER_SYSMEM;"
if new_algo in s:
    print("  tu_autotune.cc: PREFER_SYSMEM already active")
elif old_algo in s:
    s = s.replace(old_algo, new_algo, 1)
    changed = True
    print("  tu_autotune.cc: DEFAULT -> PREFER_SYSMEM")
else:
    print("ERROR: autotune algorithm anchor absent", file=sys.stderr)
    sys.exit(2)

old_bw = "gmem_bandwidth = (gmem_bandwidth * 11 + total_draw_call_bandwidth) / 10;"
new_bw = "gmem_bandwidth = (gmem_bandwidth * 10 + total_draw_call_bandwidth) / 10;"
if old_bw in s:
    s = s.replace(old_bw, new_bw, 1)
    changed = True
    print("  tu_autotune.cc: bandwidth history 11 -> 10")
elif "* 10 + total_draw_call_bandwidth" in s:
    print("  tu_autotune.cc: bandwidth history already 10")
else:
    print("ERROR: GMEM-10 anchor absent", file=sys.stderr)
    sys.exit(3)

if changed:
    with open(p, "w") as f:
        f.write(s)
print("GTAV A840: GMEM10 + PREFER_SYSMEM applied; no PWR_MAX")
