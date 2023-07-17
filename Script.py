import bpy
import numpy as np
import scipy as sp

def get_bone_coordinate(bone, get_head=False):
    if get_head:
        coordinate=np.array([bone.head.x, bone.head.y, bone.head.z])
    else:
        coordinate=np.array([bone.tail.x, bone.tail.y, bone.tail.z])

    return coordinate

def normalize(vector,desired_length=1):
    norm=np.linalg.norm(vector)
    ratio=norm/desired_length
    vector=np.devide(vector,ratio)

    return vector

def generate_quaternion(angle, axis):
    # Normalize the axis vector
    # angle in degree
    axis = axis / np.linalg.norm(axis)

    # Calculate the quaternion components
    w = np.cos(np.radian(angle) / 2)
    x = axis[0] * np.sin(angle / 2)
    y = axis[1] * np.sin(angle / 2)
    z = axis[2] * np.sin(angle / 2)

    quaternion = np.quaternion(w, x, y, z)
    return quaternion

def rotate_vector(vector, rotation_quaternion):
    # Normalize the vector
    vector = vector / np.linalg.norm(vector)

    # Convert the vector to a pure quaternion
    vector_quaternion = np.quaternion(0, *vector)

    # Apply the rotation using quaternion multiplication
    rotated_vector_quaternion = rotation_quaternion * vector_quaternion * np.conjugate(rotation_quaternion)

    # Extract the vector part from the resulting quaternion
    rotated_vector = np.array([rotated_vector_quaternion.x, rotated_vector_quaternion.y, rotated_vector_quaternion.z])

    return rotated_vector

def get_pseudo_mesh_vertices(a=None, b, c=None, no_children=False, no_parent=False):
    if no_children:
        # for node that has no children
        surface_normal=normalize(np.subtract(a,b))
        ori_on_plane=np.array([delta,0,0])
    elif no_parent:
        # for node that has no parent
        surface_normal=normalize(np.subtract(c,b))
        ori_on_plane=np.array([delta,0,0])
    # a:previous joint b:current joint c:next joint (xyz position)
    # return a list of four vertices of the sqaure mesh
    else:
        ori_on_plane=np.divide(np.add(normalize(np.subtract(a,b)),normalize(np.subtract(c,b))),2)
        surface_normal=np.cross(ori_on_plane,np.cross(a,ori_on_plane))
    # retract the length of ori to delta
    vertices=np.empty(4)
    vertices[1]=ori_on_plane
    # calculate the vector first, add the origin (point b) later
    for i in range(1,4):
        vertices[i]=rotate_vector(vertices[i-1],generate_quaternion(90, surface_normal))
    # add the origin (point b) make it into vertices of the rectangle
    for i in range(4):
        vertices[i]=np.add(vertices[i],b)
    
    return vertices

# Get all armature objects in the scene
armature_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
print('start')

delta=0.01 #delta control the width of the mesh

nodes=list()
edges=list()
name2idx=dict()
node2vertex=dict()
starting_viewed=False

spine_node_num=0
leg_node_num=5

# Iterate through each armature object
for armature_obj in armature_objects:
    if armature_obj.name == 'metarig':
        print("Armature:", armature_obj.name)
        f = open('D:/Download/3DScanning/Projects/Models/pseudo_mesh.off', 'w')
        print("appearance {linewidth 10}", file=f)
        print("{off", file=f)
        
        #save head location for the starting bone (only run once)
        for bone in armature_obj.data.bones:
            if bone.parent is None and starting_viewed == False:
                point=[str(bone.head.x), str(bone.head.y), str(bone.head.z), 'starting point']
                nodes.append(point)

                next_joint_coordinate=get_bone_coordinate(bone)
                current_joint_coordinate=get_bone_coordinate(bone, get_head=True)
                node2vertex['starting point']=get_pseudo_mesh_vertices(next_joint_coordinate,current_joint_coordinate,no_parent=True)

                break
            
        #save tail location for all bones
        for bone in armature_obj.data.bones:    
            point=[str(bone.tail.x), str(bone.tail.y), str(bone.tail.z), bone.name]
            nodes.append(point)
            name2idx[bone.name] = len(nodes)-1

            next_joint_coordinate=armature_obj.data.bones
            current_joint_coordinate=get_bone_coordinate(bone)
            previous_joint_coordinate=get_bone_coordinate(bone, get_head=True)

            
            node2vertex[bone.name]=get_pseudo_mesh_vertices()
            
        #adding edges
        for bone in armature_obj.data.bones:
            if bone.parent is None:
                edges.append([str(name2idx[bone.name]), '0'])
            else:
                edges.append([str(name2idx[bone.name]),str(name2idx[bone.parent.name])])


        #for spine, generate the mesh
        for bone in armature_obj.data.bones:
            if "spine" in bone.name:
                spine_node_num=spine_node_num+1
            spine_node_num=spine_node_num+1
        for bone in armature_obj.data.bones:
            if "spine" in bone.name:
                spine_node_num=spine_node_num+1
            spine_node_num=spine_node_num+1
        
        #print (node_num, face_num, edge_nmu)
        print(5*(spine_node_num+4*leg_node_num), 12*spine_node_num-8+4*(12*leg_node_num-8), 16*spine_node_num-8+4*(16*leg_node_num-8), file=f)

        #print spine point coordinate
        for bone in armature_obj.data.bones:
                   
                    

                
print("end")