#!/bin/bash
# Waits for Phase 2 to finish, then runs the Phase 3 ablation by rebuilding
# one variant at a time (same binary name, so variants MUST be sequential).
set -u
CS=~/ChampSim; MOD=$CS/prefetcher/spp_dev_gated; R=~/cs683/checkpoint2
mkdir -p $R/notes $R/results
exec >> $R/notes/overnight.log 2>&1
echo "================ overnight start $(date) ================"

wait_sims () { while pgrep -f 'bin/champsim' >/dev/null; do
  echo "$(date +%H:%M) waiting: $(pgrep -cf 'bin/champsim') sims alive"; sleep 120; done; }

echo "--- phase 2 / control stragglers ---"; wait_sims
echo "--- phase 2 complete $(date) ---"
$R/scripts/03_collect.py control gated

cp $MOD/spp_dev_gated.h $R/notes/spp_dev_gated.h.pristine
run_variant () {   # $1=tag  $2=sed-expr  $3...=prefixes
  local tag=$1 expr=$2; shift 2
  echo "=== variant $tag  ($expr)  $(date) ==="
  cp $R/notes/spp_dev_gated.h.pristine $MOD/spp_dev_gated.h
  sed -i "$expr" $MOD/spp_dev_gated.h
  grep -E "GATE_MAX_LEVEL|GATE_WASTE_HIGH|GATE_WASTE_LOW|GATE_EPOCH" $MOD/spp_dev_gated.h \
    | tee $R/results/${tag}_config.txt
  ( cd $CS && ./config.sh configs/spp_dev_gated_lru.json >/dev/null \
    && make -j"$(nproc)" >/dev/null 2>&1 ) || { echo "BUILD FAILED for $tag"; return 1; }
  echo "built ok, sweeping: $*"
  $R/scripts/02_sweep.sh champsim_spp_dev_gated_lru "$tag" "$@"
  wait_sims
}

run_variant cap1   's/GATE_MAX_LEVEL = [0-9]*/GATE_MAX_LEVEL = 1/'   jll4 jll5 pmm pmmb
run_variant cap2   's/GATE_MAX_LEVEL = [0-9]*/GATE_MAX_LEVEL = 2/'   jll4 jll5 pmm pmmb
run_variant wh100  's/GATE_WASTE_HIGH = [0-9]*/GATE_WASTE_HIGH = 100/'  jll4 pmm
run_variant wh2000 's/GATE_WASTE_HIGH = [0-9]*/GATE_WASTE_HIGH = 2000/' jll4 pmm

echo "--- restoring pristine gate + rebuild ---"
cp $R/notes/spp_dev_gated.h.pristine $MOD/spp_dev_gated.h
( cd $CS && ./config.sh configs/spp_dev_gated_lru.json >/dev/null && make -j"$(nproc)" >/dev/null 2>&1 )

echo "--- final collect ---"
$R/scripts/03_collect.py control gated cap1 cap2 wh100 wh2000
echo "================ overnight DONE $(date) ================"
