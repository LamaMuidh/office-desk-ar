import json, struct, math
from pathlib import Path

ROOT=Path(__file__).parent
def make(width):
    data=bytearray(); views=[]; access=[]; meshes=[]; nodes=[]
    def buf(values,typ,n,kind):
        offset=len(data); data.extend(struct.pack('<'+typ*len(values),*values))
        while len(data)%4:data.append(0)
        views.append({'buffer':0,'byteOffset':offset,'byteLength':len(values)*struct.calcsize(typ)})
        a={'bufferView':len(views)-1,'componentType':5126 if typ=='f' else 5123,'count':len(values)//n,'type':kind}
        if kind=='VEC3':a.update(min=[min(values[i::3]) for i in range(3)],max=[max(values[i::3]) for i in range(3)])
        access.append(a); return len(access)-1
    def box(name,size,center,mat):
        x,y,z=[v/2 for v in size]; p=[]; norm=[]; inds=[]
        faces=[([(x,-y,-z),(x,y,-z),(x,y,z),(x,-y,z)],(1,0,0)),
        ([(-x,-y,z),(-x,y,z),(-x,y,-z),(-x,-y,-z)],(-1,0,0)),
        ([(-x,y,-z),(-x,y,z),(x,y,z),(x,y,-z)],(0,1,0)),
        ([(-x,-y,z),(-x,-y,-z),(x,-y,-z),(x,-y,z)],(0,-1,0)),
        ([(x,-y,z),(x,y,z),(-x,y,z),(-x,-y,z)],(0,0,1)),
        ([(-x,-y,-z),(-x,y,-z),(x,y,-z),(x,-y,-z)],(0,0,-1))]
        for coords,n in faces:
            start=len(p)//3
            for v in coords:p.extend(v); norm.extend(n)
            inds.extend([start,start+1,start+2,start,start+2,start+3])
        meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':buf(p,'f',3,'VEC3'),'NORMAL':buf(norm,'f',3,'VEC3')},'indices':buf(inds,'H',1,'SCALAR'),'material':mat}]})
        nodes.append({'mesh':len(meshes)-1,'translation':center,'name':name})
    box('Desktop: 25 mm', [width,.025,.8],[0,.7375,0],0)
    # Grain strips are shallow inlaid material regions, contained in the desktop envelope.
    import random
    random.seed(7)
    for i in range(95):
        z=-.39+i*.0082
        length=random.uniform(.15,.75); xpos=random.uniform(-width/2+length/2,width/2-length/2)
        box('Walnut grain',[length,.0001,random.uniform(.0006,.0018)],[xpos,.74998,z],2+i%2)
    for x in [-.75,.75]:
        box('Foot depth 68 cm',[.1,.025,.68],[x,.0225,0],1)
        for z in [-.26,.26]:
            box('Foot pad',[.08,.01,.07],[x,.005,z],1)
            box('Lower telescopic leg',[.075,.31,.075],[x,.19,z],1)
            box('Middle telescopic leg',[.065,.22,.065],[x,.455,z],1)
            box('Upper telescopic leg',[.055,.12,.055],[x,.625,z],1)
        box('Side support',[.1,.04,.64],[x,.705,0],1)
    for z in [-.28,.28]:box('Cross rail',[1.5,.04,.045],[0,.705,z],1)
    box('Control box',[.23,.035,.1],[.15,.6875,0],1)
    box('Keypad',[.13,.018,.06],[.66,.703,.354],1)
    mats=[{'name':'Dark walnut','pbrMetallicRoughness':{'baseColorFactor':[.24,.135,.065,1],'roughnessFactor':.65}},
    {'name':'Black powder coated steel','pbrMetallicRoughness':{'baseColorFactor':[.035,.039,.04,1],'metallicFactor':.35,'roughnessFactor':.6}},
    {'name':'Walnut dark grain','pbrMetallicRoughness':{'baseColorFactor':[.13,.067,.027,1],'roughnessFactor':.7}},
    {'name':'Walnut light grain','pbrMetallicRoughness':{'baseColorFactor':[.3,.18,.09,1],'roughnessFactor':.7}}]
    g={'asset':{'version':'2.0','generator':'Office Station dimensional prototype'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':access}
    j=json.dumps(g,separators=(',',':')).encode(); j+=b' '*((-len(j))%4)
    out=struct.pack('<III',0x46546c67,2,28+len(j)+len(data))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(data),0x004e4942)+data
    (ROOT/f'desk-{round(width*100)}.glb').write_bytes(out)
    print(f'Desk {width} x 0.8 x 0.75 m, surface 0.025 m; {len(out)} bytes')
for w in [1.8,2.0]:make(w)
