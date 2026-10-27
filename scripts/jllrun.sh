#!/bin/bash
cd ~/cs683
TR=~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so
J="java -XX:+UseSerialGC -Xms512m -Xmn256m -Xbatch -cp bin/java LinkedList 300"
N=$($PIN_ROOT/pin -t $TR -o /tmp/$1_probe.champsimtrace -s 99999999999 -t 40000000 -- $J 2>&1 | sed -n 's/.*instructions seen: \([0-9]*\).*/\1/p')
echo "N=$N"
SKIP=$((N - $2))
$PIN_ROOT/pin -t $TR -o traces/long_$1.champsimtrace -s $SKIP -t 40000000 -- $J
./finish.sh long_$1 $1
