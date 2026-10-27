#!/bin/bash
cd ~/cs683
TR=~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so
run() { name=$1; pre=$2; skip=$3; shift 3
  $PIN_ROOT/pin -t $TR -o traces/$name.champsimtrace -app_thread 0 -s $skip -t 40000000 -- "$@" > /tmp/$pre.log 2>&1
  ./finish.sh $name $pre >> /tmp/$pre.log 2>&1; }
run long_cmm_b cmmb 406150499 bin/matrix_mult_512_v2 &
run long_cll_b cllb 170564411 bin/linked_list 80 &
run long_pmm_b pmmb 4436628767 python3 src/python/matrix_mult.py &
run long_pll_b pllb 6652792584 python3 src/python/linked_list.py 4 &
wait
