#!/bin/bash
cd ~/cs683
IC=$PIN_ROOT/source/tools/ManualExamples/obj-intel64/inscount0.so
$PIN_ROOT/pin -t $IC -o counts/count_pll_p0.txt -- python3 src/python/linked_list.py 0
$PIN_ROOT/pin -t $IC -o counts/count_pll_p4.txt -- python3 src/python/linked_list.py 4
B=$(awk '{print $2}' counts/count_pll_p0.txt)
T=$(awk '{print $2}' counts/count_pll_p4.txt)
C=$(( (T - B) / 4 ))
SKIP=$(( B + 2 * C ))
echo "build=$B total=$T pass=$C skip=$SKIP"
$PIN_ROOT/pin -t ~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so -o traces/long_pll2.champsimtrace \
  -app_thread 0 -s $SKIP -t 40000000 -- python3 src/python/linked_list.py 4
./finish.sh long_pll2 pll2
