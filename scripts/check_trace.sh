#!/bin/bash
# usage: ./check_trace.sh <trace_name>
xz -dc ~/cs683/traces/$1.champsimtrace.xz | python3 -I -c "
import sys, collections
d = sys.stdin.buffer.read()
n = len(d)//64
ips = collections.Counter(d[o:o+8] for o in range(0, n*64, 64))
print('bytes', len(d), ' mod64', len(d)%64, ' records', n)
print('ip == 0 records:', ips.get(bytes(8), 0))
print('records with a register id >= 128:', sum(1 for o in range(0, n*64, 64) if max(d[o+10:o+16]) >= 128))
print('distinct ips:', len(ips))
top = ips.most_common(40)
print('top-40 ips cover: %.1f%%' % (100*sum(c for _, c in top)/n))
"
