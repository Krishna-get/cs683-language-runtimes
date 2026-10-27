#!/bin/bash
cd ~/cs683
T=$(awk '{print $2}' counts/count_py_total.txt)
[ -n "$T" ] || { echo "count_py_total.txt is still empty: wait for the Python count to finish"; exit 1; }
ROW=$(( (T - 972027113) / 512 ))
SKIP=$(( 972027113 + 3 * ROW ))
echo "T=$T ROW=$ROW SKIP=$SKIP"
$PIN_ROOT/pin -t ~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so -o traces/long_pmm.champsimtrace \
  -app_thread 0 -s $SKIP -t 40000000 -- python3 src/python/matrix_mult.py
./finish.sh long_pmm pmm
