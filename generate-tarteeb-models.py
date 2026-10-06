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
    def rounded_top(width, depth, radius, thickness, y):
        # Extruded rounded rectangle. Dimensions are in meters.
        outline=[]
        for cx,cz,angle in [(width/2-radius,depth/2-radius,0),(-width/2+radius,depth/2-radius,90),(-width/2+radius,-depth/2+radius,180),(width/2-radius,-depth/2+radius,270)]:
            for i in range(9):
                a=math.radians(angle+i*90/8)
                outline.append((cx+radius*math.cos(a),cz+radius*math.sin(a)))
        p=[]; normals=[]; indices=[]
        def triangle(points,normal):
            start=len(p)//3
            for point in points:p.extend(point); normals.extend(normal)
            indices.extend([start,start+1,start+2])
        for i,(x,z) in enumerate(outline):
            nx,nz=outline[(i+1)%len(outline)]
            triangle([(0,y,0),(nx,y,nz),(x,y,z)],(0,1,0))
            triangle([(0,y-thickness,0),(x,y-thickness,z),(nx,y-thickness,nz)],(0,-1,0))
            dx,dz=nx-x,nz-z; length=math.hypot(dx,dz); normal=(dz/length,0,-dx/length)
            triangle([(x,y-thickness,z),(x,y,z),(nx,y,nz)],normal)
            triangle([(x,y-thickness,z),(nx,y,nz),(nx,y-thickness,nz)],normal)
        meshes.append({'name':'Rounded walnut desktop','primitives':[{'attributes':{'POSITION':buf(p,'f',3,'VEC3'),'NORMAL':buf(normals,'f',3,'VEC3')},'indices':buf(indices,'H',1,'SCALAR'),'material':0}]})
        nodes.append({'mesh':len(meshes)-1,'name':'Rounded walnut desktop'})
    rounded_top(width,.8,.045,.025,.75)
    import random
    random.seed(7)
    for i in range(85):
        z=-.35+i*.0082; length=random.uniform(.15,.7)
        xpos=random.uniform(-width/2+.06+length/2,width/2-.06-length/2)
        box('Walnut grain',[length,.0001,random.uniform(.0006,.0016)],[xpos,.74998,z],2+i%2)
    spacing=width-.32
    for x in [-spacing/2,spacing/2]:
        box('T-shaped foot',[.085,.03,.68],[x,.035,0],1)
        for z in [-.28,.28]:box('Foot pad',[.07,.02,.075],[x,.01,z],1)
        box('Lower telescopic column',[.085,.29,.08],[x,.195,0],1)
        box('Middle telescopic column',[.075,.22,.07],[x,.445,0],1)
        box('Upper telescopic column',[.065,.15,.06],[x,.63,0],1)
        box('Top support',[.08,.035,.57],[x,.705,0],1)
        box('Motor housing',[.16,.06,.12],[x,.679,0],1)
    box('Cross rail',[spacing,.055,.065],[0,.6925,0],1)
    box('Control box',[.22,.035,.12],[.12,.66,0],1)
    box('Keypad',[.14,.045,.035],[width/2-.32,.6975,.373],4)
    for i in range(4):box('Keypad button',[.012,.012,.002],[width/2-.355+i*.023,.702,.392],5)
    mats=[{'name':'Dark walnut','pbrMetallicRoughness':{'baseColorFactor':[.24,.135,.065,1],'roughnessFactor':.65}},
    {'name':'Dark grey powder coated steel','pbrMetallicRoughness':{'baseColorFactor':[.12,.13,.13,1],'metallicFactor':.35,'roughnessFactor':.6}},
    {'name':'Walnut dark grain','pbrMetallicRoughness':{'baseColorFactor':[.13,.067,.027,1],'roughnessFactor':.7}},
    {'name':'Walnut light grain','pbrMetallicRoughness':{'baseColorFactor':[.3,.18,.09,1],'roughnessFactor':.7}}]
    mats.extend([{'name':'Keypad black','pbrMetallicRoughness':{'baseColorFactor':[.02,.02,.02,1]}},{'name':'Keypad buttons','pbrMetallicRoughness':{'baseColorFactor':[.55,.55,.55,1]}}])
    g={'asset':{'version':'2.0','generator':'Office Station dimensional prototype'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':len(data)}],'bufferViews':views,'accessors':access}
    j=json.dumps(g,separators=(',',':')).encode(); j+=b' '*((-len(j))%4)
    out=struct.pack('<III',0x46546c67,2,28+len(j)+len(data))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(data),0x004e4942)+data
    (ROOT/f'tarteeb-{round(width*100)}.glb').write_bytes(out)
    print(f'Desk {width} x 0.8 x 0.75 m, surface 0.025 m; {len(out)} bytes')
for w in [1.6,1.8]:make(w)

