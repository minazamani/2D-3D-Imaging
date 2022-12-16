import bpy
import bmesh
import math
import mathutils
import time
import bpy

thikness = 0.9
file_loc = 'Sphinx.obj'
imported_object = bpy.ops.import_scene.obj(filepath=file_loc)

def console_get():
    for area in bpy.context.screen.areas:
        if area.type == 'CONSOLE':
            for space in area.spaces:
                if space.type == 'CONSOLE':
                    return area, space
    return None, None


def console_write(text):
    area, space = console_get()
    if space is None:
        return

    context = bpy.context.copy()
    context.update(dict(
        space=space,
        area=area,
    ))
    for line in text.split("\n"):
        bpy.ops.console.scrollback_append(context, text=line, type='OUTPUT')

#console_write("Hello World")

obj = bpy.context.object
me = obj.data
bm = bmesh.from_edit_mesh(me)
 

def BoundingBoxFromPoints(points):
    """Takes a list of points, returns a tuple containing the corner points
       containting theminimum and maximum values in x, y, z directions"""
    xMin, yMin, zMin = float( 'inf'),float( 'inf'),float( 'inf')
    xMax, yMax, zMax = float('-inf'),float('-inf'),float('-inf')
    for p in points:
        if (p.x < xMin):
            xMin = p.x
        if (p.y < yMin):
            yMin = p.y
        if (p.z < zMin):
            zMin = p.z
        if (p.x > xMax):
            xMax = p.x
        if (p.y > yMax):
            yMax = p.y
        if (p.z > zMax):
            zMax = p.z
    return ( mathutils.Vector((xMin,yMin,zMin)), mathutils.Vector((xMax, yMax, zMax)) )

m = BoundingBoxFromPoints([v.co for v in me.vertices.values()])
minZ = m[0][2]
maxZ = m[1][2] 
console_write('min Z = ' + str(minZ))
cutters = []
Z = minZ + 0.25
#console_write('Z = ' + str(Z))
i = 0
 
locationZ = [] 
while Z < maxZ:
    locationZ.append(Z)
    cutters.append(i)
    Z = Z + thikness
    i = i + 1

console_write('locationZ = ' + str(locationZ))    


def add_v3v3(v0, v1):
    return (
        v0[0] + v1[0],
        v0[1] + v1[1],
        v0[2] + v1[2],
    )


def sub_v3v3(v0, v1):
    return (
        v0[0] - v1[0],
        v0[1] - v1[1],
        v0[2] - v1[2],
    )


def dot_v3v3(v0, v1):
    return (
        (v0[0] * v1[0]) +
        (v0[1] * v1[1]) +
        (v0[2] * v1[2])
    )


def len_squared_v3(v0):
    return dot_v3v3(v0, v0)


def mul_v3_fl(v0, f):
    return (
        v0[0] * f,
        v0[1] * f,
        v0[2] * f,
    )
    

def cross(u, v):
    return (
         u[1]*v[2] - u[2]*v[1],
         u[2]*v[0] - u[0]*v[2],
         u[0]*v[1] - u[1]*v[0]
         ) 
  
def isect_line_plane_v3(p0, p1, p_co, p_no, epsilon=1e-6):
    u = sub_v3v3(p1, p0)
    dot = dot_v3v3(p_no, u)
    if abs(dot) > epsilon:
        w = sub_v3v3(p0, p_co)
        fac = -dot_v3v3(p_no, w) / dot
#        console_write('fac = ' + str(fac))
        if fac > 1 or fac < 0:
#            console_write('Point is out of segment')
            return None
        else:
            u = mul_v3_fl(u, fac)
            result = add_v3v3(p0, u)
            return result
    else : 
        return None    

counter = 1
curr_faces = []    
p = []
newlist = []
faces = []
p_n = mathutils.Vector((0.0, 0.0, 1.0))
for cuti in cutters:
   for edge in bm.edges:
        print(cuti)
        b_intersect = False
        p1 = edge.verts[0] 
        p2 = edge.verts[1]
        intersectPoint = mathutils.Vector()
        p0 = mathutils.Vector((0.0, 0.0, locationZ[cuti]))
        p1v = mathutils.Vector((p1.co.x,p1.co.y, p1.co.z))
        p2v = mathutils.Vector((p2.co.x,p2.co.y, p2.co.z))    
        intersectPoint = isect_line_plane_v3(p1v,p2v, p0, p_n)           
        if intersectPoint is not None:
            #console_write('I am here')  
            newVert = bm.verts.new(intersectPoint)
            bmesh.update_edit_mesh(me)
            facei = []
            p.append(intersectPoint)
            for face in edge.link_faces:
                   facei.append(face.index)
            faces.append(facei)

console_write(str(p[1]))
ed = []

for i in range(len(p)):
    for j in range(i+1,len(p)):
        innerlist = []
        if len(set(faces[i]).intersection(set(faces[j]))) >0:
            #console_write('Intersection ' + str(i) + ' ' + str(j))
            if p[i][2] == p[j][2]:
                innerlist.append(i)
                innerlist.append(j)            
                ed.append(tuple(innerlist))
            

#console_write(str(ed))
v = p
e = ed
f =  []

cut = bpy.data.meshes.new('cut' )
cut.from_pydata(v, e, f)
cut.update()
obj_cut = bpy.data.objects.new('cut', cut)
collection_cut = bpy.data.collections.new('collection_cut')
bpy.context.scene.collection.children.link(collection_cut)
collection_cut.objects.link(obj_cut)            





































