import re, struct, collections
CLS={0:"SCALAR",1:"VECTOR",2:"MATRIX_ROWS",3:"MATRIX_COLUMNS",4:"OBJECT",5:"STRUCT"}
d=open("shaderdb.bin","rb").read()
def cstr(b,a):
    e=b.find(b"\0",a); return b[a:e].decode("latin-1","replace") if e>=0 else ""
tables=[]
for m in re.finditer(b"CTAB", d):
    base=m.start()+4
    try: size,c,v,nconst,cinfo,fl,tgt=struct.unpack_from("<7I",d,base)
    except struct.error: continue
    if size!=0x1C or not (0<nconst<512): continue
    if base+cinfo+nconst*20>len(d): continue
    t=cstr(d,base+tgt) if base+tgt<len(d) else "?"
    if not re.match(r"^(vs|ps)_\d_\d$",t): continue
    rows=[]
    for i in range(nconst):
        o=base+cinfo+i*20
        no,rs,ri,rc,_r,ti,_dv=struct.unpack_from("<IHHHHII",d,o)
        if base+no>=len(d): continue
        cl=None
        if base+ti+12<=len(d):
            cl,ty,rr,cc,el,sm=struct.unpack_from("<6H",d,base+ti)
        rows.append((cstr(d,base+no),rs,ri,rc,cl))
    tables.append((rows,t))
print("parsed %d tables (vs=%d ps=%d)"%(len(tables),
      sum(1 for _,t in tables if t.startswith("vs")), sum(1 for _,t in tables if t.startswith("ps"))))

# transform vocabulary
rx=re.compile(r"world|view|proj|camera|eye|bone|skin|matrix",re.I)
where=collections.defaultdict(collections.Counter); cls=collections.defaultdict(collections.Counter)
for rows,t in tables:
    for nm,rs,ri,rc,cl in rows:
        if rs!=2: continue
        if rx.search(nm):
            where[nm][(t,ri,rc)]+=1; cls[nm][CLS.get(cl,cl)]+=1
print()
print("=== transform-ish float4 constants ===")
for n,name in sorted(((sum(v.values()),k) for k,v in where.items()),reverse=True)[:18]:
    spots=", ".join("%s c%d x%d(%d)"%(t,r,c,k) for (t,r,c),k in where[name].most_common(3))
    print("  %-34s %-6d %-16s %s"%(name,n,",".join(cls[name]),spots))

# the c0 vs c128 split - is it a skinning palette?
print()
print("=== why g_WorldViewProj moves between c0 and c128 ===")
tab=collections.Counter()
for rows,t in tables:
    if not t.startswith("vs"): continue
    dd={r[0]:r for r in rows if r[1]==2}
    if "g_WorldViewProj" not in dd: continue
    reg=dd["g_WorldViewProj"][2]
    big=[ (nm,r[2],r[3]) for nm,r in dd.items() if r[3]>=32 ]
    tab[(reg, tuple(sorted(big)))]+=1
for (reg,big),n in tab.most_common(8):
    print("  c%-4d : %5d shaders ; large arrays present: %s"%(reg,n,big if big else "none"))
