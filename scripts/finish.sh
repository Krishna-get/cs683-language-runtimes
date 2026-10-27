#!/bin/bash
# usage: ./finish.sh <trace_name> <result_prefix>
cd ~/cs683
f=traces/$1.champsimtrace
[ "$(stat -c %s $f)" = 2560000000 ] || { echo "BAD TRACE SIZE: $(stat -c %s $f)"; exit 1; }
xz -T0 -f $f
echo "== check $1"; flock /tmp/check.lock ./check_trace.sh $1
for pf in no ip_stride spp_dev; do
  ~/ChampSim/bin/champsim_${pf}_lru --warmup-instructions 10000000 --simulation-instructions 30000000 \
    --hide-heartbeat traces/$1.champsimtrace.xz > results/$2_$pf.txt &
done
wait
grep -H "CPU 0 cumulative IPC" results/$2_*.txt
