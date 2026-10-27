#!/bin/bash
cd ~/cs683
TR=~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so
J="java -XX:+UseSerialGC -cp bin/java MatrixMult"
for w in "jw0 0" "jw1 300000000"; do set -- $w
  ( $PIN_ROOT/pin -t $TR -o traces/long_$1.champsimtrace -s $2 -t 40000000 -- $J > /tmp/$1.log 2>&1
    ./finish.sh long_$1 $1 >> /tmp/$1.log 2>&1 ) &
done
wait
