import sys
import struct, json, sys, collections
import capstone
EXE = sys.argv[1]   # path to a Steamless-unpacked copy of PrinceOfPersia_Launcher.exe
d = open(EXE,"rb").read()
DICT = {int(k,16): v for k,v in json.load(open("crc_dict.json")).items()}
pe=struct.unpack_from("<I",d,0x3c)[0]; nsec=struct.unpack_from("<H",d,pe+6)[0]; optsz=struct.unpack_from("<H",d,pe+20)[0]
imgbase=struct.unpack_from("<I",d,pe+24+28)[0]
secs=[]
for i in range(nsec):
    o=pe+24+optsz+40*i
    nm=d[o:o+8].rstrip(b"\0").decode(); vsz,va,rsz,ro=struct.unpack_from("<IIII",d,o+8)
    secs.append((nm,imgbase+va,vsz,ro,rsz))
def va2f(va):
    for n,v,vsz,ro,rsz in secs:
        if v<=va<v+vsz:
            f=ro+(va-v)
            return f if f<ro+rsz else None
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True

def walk(va, maxins=600):
    """linear disassembly until ret/int3 padding run"""
    f = va2f(va)
    if f is None: return []
    out=[]; n=0; pad=0
    for ins in md.disasm(d[f:f+maxins*8], va):
        out.append(ins); n+=1
        if ins.mnemonic == "int3":
            pad += 1
            if pad >= 4: break
        else: pad = 0
        if n>=maxins: break
    return out

def consts(ins_list):
    r=[]
    for ins in ins_list:
        for op in ins.operands:
            if op.type == capstone.x86.X86_OP_IMM:
                v = op.imm & 0xffffffff
                if v in DICT: r.append((ins.address, v, DICT[v]))
        # also mov dword ptr [..], imm32 captured above
    return r

targets = json.load(open("targets.json"))
for label, slots in targets.items():
    print("\n################ %s" % label)
    seen=set()
    for slot, va in slots:
        ins = walk(va)
        cs = consts(ins)
        cs = [c for c in cs if c[1] not in seen]
        for a,v,names in cs:
            seen.add(v)
            print("  slot %-3s fn 0x%08x  @0x%08x  const 0x%08x -> %s" % (slot, va, a, v, ",".join(names)))
