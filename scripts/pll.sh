#!/bin/bash
cd ~/cs683
$PIN_ROOT/pin -t $PIN_ROOT/source/tools/ManualExamples/obj-intel64/inscount0.so -o counts/count_pll.txt -- python3 src/python/linked_list.py 4
T=$(awk '{print $2}' counts/count_pll.txt)
SKIP=$((T - 250000000))
echo "T=$T SKIP=$SKIP"
$PIN_ROOT/pin -t ~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so -o traces/long_pll.champsimtrace \
  -app_thread 0 -s $SKIP -t 40000000 -- python3 src/python/linked_list.py 4
./finish.sh long_pll pll
