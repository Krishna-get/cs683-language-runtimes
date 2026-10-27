# Microarchitectural Characterisation of Language Runtimes: C vs JVM vs CPython

CS683 course project, Checkpoint I. Krishna Kukreja, 24b3971.

The same two algorithms in C, Java and Python, traced with Intel Pin and
simulated in ChampSim under three L2 prefetchers. The question: for identical
work, how does the language runtime change cache and branch behaviour, and do
existing prefetchers help any of them?

## Layout

| Path | Contents |
|---|---|
| `src/c`, `src/java`, `src/python` | the six workloads |
| `tracer/` | patch adding a per-thread filter to the ChampSim Pin tracer |
| `scripts/` | tracing, trace-checking and prefetcher-sweep scripts |
| `results/` | ChampSim output for every run (see `results/README.md`) |
| `counts/` | Pin instruction counts used to calibrate trace windows |

Traces are not in the repo: each is 2.56 GB raw, 2.6–36 MB compressed.
Regenerate them with the scripts below.

## Which source files are the workloads

- Matrix multiply: `src/c/matrix_mult_512_v2.c`, `src/java/MatrixMult.java`, `src/python/matrix_mult.py`
- Linked list: `src/c/linked_list.c`, `src/java/LinkedList.java`, `src/python/linked_list.py`

Other files in `src/` are earlier variants kept for reference.
`matrix_mult_pad_512.c` is the padded version used for the cache-set-conflict
experiment. `MatrixMultWarmupOnly.java` and `matrix_mult_init.py` are helpers
for measuring skip counts, not workloads.

## Versions

ChampSim commit 410cee62 · Intel Pin 3.31 · gcc 13.3.0 (`-O2 -fno-tree-vectorize`) ·
OpenJDK 21.0.12.1 (`-XX:+UseSerialGC`) · CPython 3.12.3

## Simulated machine

L1I 32 KB (64x8) · L1D 48 KB (64x12) · L2 512 KB (1024x8) · LLC 2 MB (2048x16) ·
ROB 352 · LRU at every level. Only the L2 prefetcher varies: none / ip_stride / spp_dev.
10M warm-up + 30M measured, from a 40M-record trace.

## Workload equivalence

Matrix multiply checksum is 16,392,906,262,816 in all three languages.
Linked-list checksums match across languages for every pass count used.
Values start at 300 so CPython's small-integer cache does not alias elements.
NumPy was used only as an external check, never inside a workload.

## Trace windows

Window positions were measured by a probe run under the tracer itself, because
JIT timing shifts with tool overhead: the Java application thread executes 9.09B
instructions under the tracer versus 14.58B under a light instruction counter.

See `scripts/` for the exact skip value used in each run.

## Reproducing

    # 1. build
    gcc -O2 -fno-tree-vectorize src/c/matrix_mult_512_v2.c -o bin/matrix_mult_512_v2
    javac -d bin/java src/java/MatrixMult.java

    # 2. trace (C and Python use -app_thread 0, Java uses the default 1)
    $PIN_ROOT/pin -t $CHAMPSIM/tracer/pin/obj-intel64/champsim_tracer.so \
      -app_thread 0 -s <skip> -t 40000000 \
      -o traces/<name>.champsimtrace -- ./bin/matrix_mult_512_v2
    xz -T0 traces/<name>.champsimtrace

    # 3. check the trace before simulating
    ./scripts/check_trace.sh <name>

    # 4. sweep the three prefetchers
    for pf in no ip_stride spp_dev; do
      $CHAMPSIM/bin/champsim_${pf}_lru --warmup-instructions 10000000 \
        --simulation-instructions 30000000 --hide-heartbeat \
        traces/<name>.champsimtrace.xz > results/<prefix>_${pf}.txt 2>&1
    done

# Result files

Each workload and window has three files, one per L2 prefetcher:
`<prefix>_no.txt`, `<prefix>_ip_stride.txt`, `<prefix>_spp_dev.txt`.
Every file is raw ChampSim output: per-level hit/miss/merge counts, prefetch
requested/issued/useful, TLB, branch statistics.

## Primary results (36 runs)

| Prefix | Workload | Window |
|---|---|---|
| `cmm` / `cmmb` | C matrix multiply | 1 / 2 |
| `java512_full` / `java512b_full` | Java matrix multiply | 1 / 2 |
| `pmm` / `pmmb` | Python matrix multiply | 1 / 2 |
| `cll` / `cllb` | C linked list | 1 / 2 |
| `jll` … `jll5` | Java linked list | several windows; `jll4`, `jll5` are the final pair |
| `pll` / `pll2` / `pllb` | Python linked list | 1 / 2 / 3 |
