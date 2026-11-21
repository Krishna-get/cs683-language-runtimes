#!/bin/bash
# usage: 02b_sweep.sh <binary> <tag> [prefix ...]   (no prefixes = all 12)
BIN=~/ChampSim/bin/$1; TAG=$2; shift 2; WANT="$*"
cd ~/cs683; mkdir -p checkpoint2/results
mapfile -t L < <(grep -v '^#' checkpoint2/workloads.tsv)
for ln in "${L[@]}"; do
  IFS=$'\t' read -r lang algo win trace pfx <<< "$ln"
  [ -n "$WANT" ] && [[ " $WANT " != *" $pfx "* ]] && continue
  T=traces/$trace.champsimtrace.xz
  [ -f "$T" ] || { echo "MISSING: $T"; continue; }
  echo "launch $pfx ($lang $algo w$win)"
  $BIN --warmup-instructions 10000000 --simulation-instructions 30000000 \
    --hide-heartbeat "$T" > checkpoint2/results/${pfx}_${TAG}.txt 2>&1 &
  while [ "$(jobs -rp | wc -l)" -ge 4 ]; do wait -n; done
done
wait
echo "=== $TAG done ==="
grep -H "cumulative IPC:" checkpoint2/results/*_${TAG}.txt
