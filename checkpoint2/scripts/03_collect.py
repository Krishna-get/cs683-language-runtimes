#!/usr/bin/env python3
"""Parse ChampSim outputs -> CSV. usage: 03_collect.py <tag> [<tag>...]"""
import re,sys,csv,os
HOME=os.path.expanduser("~")
CP2=f"{HOME}/cs683/checkpoint2"; CP1=f"{HOME}/cs683/results"
rows=[]
wl=[l.split('\t') for l in open(f"{CP2}/workloads.tsv") if not l.startswith('#') and l.strip()]
def parse(p):
    if not os.path.exists(p): return None
    t=open(p).read(); d={}
    m=re.search(r"cumulative IPC: ([\d.]+).*?cycles: (\d+)",t)
    if not m: return None
    d['ipc'],d['cycles']=float(m.group(1)),int(m.group(2))
    m=re.search(r"MPKI: ([\d.e-]+)",t); d['branch_mpki']=float(m.group(1)) if m else None
    for lvl,key in [("cpu0_L2C","l2"),("LLC","llc")]:
        m=re.search(rf"{lvl} LOAD\s+ACCESS:\s+(\d+) HIT:\s+(\d+) MISS:\s+(\d+)",t)
        if m: d[f'{key}_load_miss']=int(m.group(3)); d[f'{key}_load_mpki']=int(m.group(3))/30000.0
        m=re.search(rf"{lvl} TOTAL\s+ACCESS:\s+(\d+) HIT:\s+(\d+) MISS:\s+(\d+)",t)
        if m: d[f'{key}_total_acc']=int(m.group(1)); d[f'{key}_total_miss']=int(m.group(3))
    m=re.search(r"cpu0_L2C PREFETCH REQUESTED:\s+(\d+) ISSUED:\s+(\d+) USEFUL:\s+(\d+) USELESS:\s+(\d+)",t)
    if m: d['pf_req'],d['pf_iss'],d['pf_useful'],d['pf_useless']=[int(m.group(i)) for i in (1,2,3,4)]
    return d
tags=sys.argv[1:] or ['gated']
for lang,algo,win,trace,pfx in [(w[0],w[1],w[2],w[3],w[4].strip()) for w in wl]:
    for tag,path in [('no',f"{CP1}/{pfx}_no.txt"),('spp_dev',f"{CP1}/{pfx}_spp_dev.txt"),
                     ('ip_stride',f"{CP1}/{pfx}_ip_stride.txt")]+\
                    [(t,f"{CP2}/results/{pfx}_{t}.txt") for t in tags]:
        d=parse(path)
        if d: rows.append(dict(lang=lang,algo=algo,window=win,prefix=pfx,cfg=tag,**d))
base={(r['prefix']):r['cycles'] for r in rows if r['cfg']=='no'}
for r in rows:
    b=base.get(r['prefix'])
    r['speedup_pct']=round((b-r['cycles'])/b*100,3) if b else None
keys=sorted({k for r in rows for k in r})
out=f"{CP2}/results/summary.csv"
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
print("wrote",out)
for r in rows:
    print(f"{r['lang']:7} {r['algo']:7} w{r['window']} {r['cfg']:16} IPC={r['ipc']:<9} spd={r['speedup_pct']}%")
