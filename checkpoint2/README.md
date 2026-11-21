# Checkpoint II — SPP-AG: a cumulative accuracy gate for SPP

Stock `spp_dev` computes `GHR.global_accuracy` but consumes it only to scale
*lookahead* confidence (`spp_dev.cc:360`). At depth 0 that term is bypassed, so
SPP never reduces its issue rate however badly it is doing. On a JVM linked-list
walk this costs 2.88% / 4.44% IPC and inflates LLC traffic by 47% / 74% for
2 useful prefetches out of 6.2 million.

SPP-AG adds the missing feedback: cumulative waste = prefetches issued / (1 +
demand hits on prefetched lines), evaluated every 16,384 L2 accesses. Above
100,000 it escalates a throttle; below 20,000 it relaxes.

## Result (Java list, both windows)

| | none | spp_dev | spp_dev_gated |
|---|---|---|---|
| IPC w1 | 0.1145 | 0.1113 (−2.88%) | 0.1144 (−0.09%) |
| IPC w2 | 0.1144 | 0.1095 (−4.44%) | 0.1142 (−0.13%) |
| LLC accesses w1 | 4.53 M | 6.64 M | 4.56 M |

97.1% of the loss recovered in both windows. The other four workloads return
*identical cycle counts* to `spp_dev` — the gate provably never fires on them.

Percentages are cycles saved / baseline cycles, matching `results/summary.csv`.

## Ablation

Level 1 (suppress lookahead) is a measured no-op: identical cycles to `spp_dev`
in both windows, `suppressed lookahead: 0`. All prefetches here are depth 0.
Level 2 (demote L2 fills to LLC fills) is *worse* than no gate in both windows,
because the lower fill threshold routes requests down a more permissive branch
of SPP's `PREFETCH_FILTER`. Only level 3, outright suppression, recovers.

Thresholds 20,000–100,000 all give full recovery; 300,000 partial; 1,000,000
never engages (the workload's own ratio is 388,623).

## Reproducing

    # 1. build the gated prefetcher from pristine upstream spp_dev
    cp -r $CHAMPSIM/prefetcher/spp_dev $CHAMPSIM/prefetcher/spp_dev_gated
    cd $CHAMPSIM/prefetcher/spp_dev_gated
    for f in spp_dev.cc spp_dev.h; do
      sed -i 's/spp_dev/spp_dev_gated/g' $f
      mv $f "$(echo $f | sed 's/spp_dev/spp_dev_gated/')"
    done
    python3 scripts/mkgate2.py $CHAMPSIM/prefetcher/spp_dev_gated
    cd $CHAMPSIM && ./config.sh configs/spp_dev_gated_lru.json && make -j

    # 2. verify the gate is actually compiled in (an earlier build silently was not)
    $CHAMPSIM/bin/champsim_spp_dev_gated_lru --warmup-instructions 0 \
      --simulation-instructions 2000 traces/long_cmm.champsimtrace.xz | grep SPP-GATE

    # 3. sweep; thresholds are environment variables, so no rebuild per variant
    scripts/02b_sweep.sh champsim_spp_dev_gated_lru gated
    SPP_GATE_CAP=1            scripts/02b_sweep.sh champsim_spp_dev_gated_lru cap1  jll4 jll5 pmm
    SPP_GATE_WASTE_HIGH=20000 scripts/02b_sweep.sh champsim_spp_dev_gated_lru wh20k jll4
    scripts/03_collect.py control gated cap1 cap2 wh20k wh300k wh1m

`01_clone_module.sh` builds the clone *without* the gate — the null-change control
that produced 12 bit-identical results and is what exposed the silent build.
`02_sweep.sh` is superseded by `02b_sweep.sh` (its workload filter was ignored).

`prefetcher/spp_dev_gated/` in the repo root is the generated source, committed so
the result is reproducible without running the patcher.
