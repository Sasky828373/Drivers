#!/usr/bin/env python3
"""GTAV/A840 V5: V4 baseline plus conservative KGSL submit syscall optimization.
Keep GMEM10 + PREFER_SYSMEM. Add EINTR fast retry behavior only; no clocks,
no PWR_MAX, no submit thread, no synchronization removal.
"""
import sys
p="src/freedreno/vulkan/tu_knl_kgsl.cc"
with open(p) as f: s=f.read()
# Inspectable source marker: replace safe_ioctl loop only when exact Mesa form exists.
old="""static int
safe_ioctl(int fd, unsigned long request, void *arg)
{
   int ret;
   do {
      ret = ioctl(fd, request, arg);
   } while (ret == -1 && (errno == EINTR || errno == EAGAIN));
   return ret;
}"""
new="""static int
safe_ioctl(int fd, unsigned long request, void *arg)
{
   int ret;
   do {
      ret = ioctl(fd, request, arg);
   } while (ret == -1 && errno == EINTR);
   return ret;
}"""
if new in s:
    print("  KGSL safe_ioctl EAGAIN retry already removed")
elif old in s:
    s=s.replace(old,new,1)
    with open(p,"w") as f:f.write(s)
    print("  KGSL safe_ioctl: retry EINTR only; EAGAIN returned to caller")
else:
    print("ERROR: exact safe_ioctl anchor absent; refusing unsafe patch",file=sys.stderr)
    pos=s.find("safe_ioctl")
    if pos >= 0:
        lo=max(0,pos-400); hi=min(len(s),pos+1400)
        print("----- ACTUAL safe_ioctl CONTEXT -----",file=sys.stderr)
        print(s[lo:hi],file=sys.stderr)
        print("----- END CONTEXT -----",file=sys.stderr)
    sys.exit(2)
print("GTAV A840 V5 KGSL patch applied")
