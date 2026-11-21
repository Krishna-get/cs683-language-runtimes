#!/bin/bash
# Run one binary over all 12 traces. usage: ./02_sweep.sh <binary> <tag>
set -e
BIN=~/ChampSim/bin/$1
TAG=$2
cd ~/cs683
mkdir -p checkpoint2/results
grep -v '^#' checkpoint2/workloads.tsv | while IFS=$'\t' read -r lang algo win trace pfx; do
  T=traces/$trace.champsimtrace.xz
  [ -f "$T" ] || { echo "MISSING TRACE: $T"; continue; }
  echo "== $pfx ($lang $algo w$win)"
  $BIN --warmup-instructions 10000000 --simulation-instructions 30000000 \
    --hide-heartbeat "$T" > checkpoint2/results/${pfx}_${TAG}.txt 2>&1 &
  while [ $(jobs -rp | wc -l) -ge 4 ]; do wait -n; done
done
wait
grep -H "cumulative IPC" checkpoint2/results/*_${TAG}.txt
