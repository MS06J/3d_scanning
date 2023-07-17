import bpy
import numpy as np
import quaternion

def get_bone_coordinate(bone, get_head=False):
    if get_head:
        coordinate=np.array([bone.head_local.x, bone.head_local.y, bone.head_local.z])
    else:
        coordinate=np.array([bone.tail_local.x, bone.tail_local.y, bone.tail_local.z])

    return coordinate

def normalize(vector,desired_length=1):
    norm=np.linalg.norm(vector)
    ratio=norm/desired_length
    vector=np.divide(vector,ratio)

    return vector

def rotate_vector(vector, angle_degrees, axis):
    # Convert the angle from degrees to radians
    angle_radians = np.deg2rad(angle_degrees)

    # Normalize the vector
    vector = vector / np.linalg.norm(vector)

    # Create the rotation quaternion
    rotation_quaternion = quaternion.from_rotation_vector(angle_radians * axis)

    # Convert the vector to a pure quaternion
    vector_quaternion = quaternion.quaternion(0, *vector)

    # Apply the rotation using quaternion multiplication
    rotated_vector_quaternion = rotation_quaternion * vector_quaternion * rotation_quaternion.conjugate()

    # Extract the vector part from the resulting quaternion
    rotated_vector = np.array([rotated_vector_quaternion.x, rotated_vector_quaternion.y, rotated_vector_quaternion.z])

    return rotated_vector

def get_pseudo_mesh_vertices(a=None, b=None, c=None, no_children=False, no_parent=False):
    # a:previous joint 
    # b:current joint 
    # c:next joint 
    # (xyz position)
    # return a list of four vertices of the sqaure mesh

    if no_children:
        # for node that has no children
        surface_normal=normalize(np.subtract(a,b))
        ori_on_plane=np.array([delta,0,0])
    elif no_parent:
        # for node that has no parent
        surface_normal=normalize(np.subtract(c,b))
        ori_on_plane=np.array([delta,0,0])
    else:
        ori_on_plane=np.divide(np.add(normalize(np.subtract(a,b)),normalize(np.subtract(c,b))),2)
        surface_normal=np.cross(ori_on_plane,np.cross(a,ori_on_plane))
    # retract the length of ori to delta
    ori_on_plane=normalize(ori_on_plane, delta)
    vertices=np.empty(5, dtype=object)
    vertices[0]=b
    vertices[1]=ori_on_plane
    # calculate the vector first, add the origin (point b) later
    for i in range(2,5):
        vertices[i]=rotate_vector(vertices[i-1], 90, surface_normal)
    # add the origin (point b) make it into vertices of the rectangle
    for i in range(1,5):
        vertices[i]=np.add(vertices[i],b)
    
    return vertices

def write_perpendicular_surface_connection_idx(bone_name):
    #write connections on the surface perpendicular to surface normal
    idx=name2idx[bone_name]
    for i in range(4):
        array_to_write=[idx, idx+1, idx+(i+1)%4+1]
        print('3', *array_to_write,file=f)

def write_parallel_surface_connection_idx(bone_name, previous_bone_name):
    idx=name2idx[previous_bone_name]
    v=[idx, idx+1, idx+2, idx+3, idx+4]
    idx=name2idx[bone_name]
    i=[idx, idx+1, idx+2, idx+3, idx+4]

    print('3', v[1], i[1], i[2], file=f)
    print('3', i[2], v[2], v[1], file=f)
    print('3', v[2], i[3], i[2], file=f)
    print('3', v[2], v[3], i[3], file=f)
    print('3', v[3], i[4], i[3], file=f)
    print('3', v[3], v[4], i[4], file=f)
    print('3', v[4], i[1], i[4], file=f)
    print('3', v[4], v[1], i[1], file=f)

# Get all armature objects in the scene
armature_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
print('start')

delta=0.00000001 #delta control the width of the mesh
scale=10 #scaling the coordinate of the skeleton

nodes=list()
edges=list()
already_write_count=0
starting_point_count=0
name2idx=dict()
node2vertex=dict()
starting_viewed=False

spine_node_num=13
leg_node_num=5

# Iterate through each armature object
for armature_obj in armature_objects:
    if armature_obj.name == 'metarig':
        print("Armature:", armature_obj.name)
        f = open('D:/Download/3DScanning/Projects/Models/pseudo_mesh.off', 'w')

        print("COFF", file=f)

        #print (node_num, face_num, edge_nmu)
        #print(5*(spine_node_num+4*leg_node_num), 12*spine_node_num-8+4*(12*leg_node_num-8), 0, file=f)
        print('165 336 0', file=f)

        #start with head
        for starting_bone in armature_obj.data.bones:
            if starting_bone.parent is None:
                next_joint_coordinate=get_bone_coordinate(starting_bone)
                current_joint_coordinate=get_bone_coordinate(starting_bone, get_head=True)
                #get vectices and record writing index
                node2vertex['starting point'+str(starting_point_count)]=get_pseudo_mesh_vertices(b=current_joint_coordinate, c=next_joint_coordinate, no_parent=True)
                name2idx['starting point'+str(starting_point_count)]=already_write_count
                #write vertices coordinates into file
                [print(*vertices, file=f) for vertices in node2vertex['starting point'+str(starting_point_count)]]

                already_write_count=already_write_count+1
                starting_point_count=starting_point_count+1

                current_bone=starting_bone

                while True:
                    name2idx[current_bone.name]=already_write_count
                    already_write_count=already_write_count+1

                    if len(current_bone.children)==0:
                        current_joint_coordinate=get_bone_coordinate(current_bone)
                        previous_joint_coordinate=get_bone_coordinate(current_bone, get_head=True)
                        node2vertex[current_bone.name]=get_pseudo_mesh_vertices(a=previous_joint_coordinate, b=current_joint_coordinate, no_children=True)
                        #write vertices coordinates into file
                        [print(*vertices, file=f) for vertices in node2vertex[current_bone.name]]
                        print("Done with bone-chain", starting_point_count, "coordinates writing")
                        break
                    else:
                        next_joint_coordinate=get_bone_coordinate(current_bone.children[0])
                        current_joint_coordinate=get_bone_coordinate(current_bone)
                        previous_joint_coordinate=get_bone_coordinate(current_bone, get_head=True)
                        node2vertex[current_bone.name]=get_pseudo_mesh_vertices(a=next_joint_coordinate,b=current_joint_coordinate,c=previous_joint_coordinate)
                        #write vertices coordinates into file
                        [print(*vertices, file=f) for vertices in node2vertex[current_bone.name]]
                        current_bone=current_bone.children[0]

        #reset all counter
        starting_point_count=0
        #start with wirting edge into file
        for starting_bone in armature_obj.data.bones:
            if starting_bone.parent is None:
                write_perpendicular_surface_connection_idx('starting point'+str(starting_point_count))
                write_parallel_surface_connection_idx(starting_bone.name, 'starting point'+str(starting_point_count))
                starting_point_count=starting_point_count+1

                current_bone=starting_bone.children[0]
                while True:
                    write_perpendicular_surface_connection_idx(current_bone.name)
                    write_parallel_surface_connection_idx(current_bone.name, current_bone.parent.name)
                    if len(current_bone.children)==0:
                        print("Done with bone-chain", starting_point_count, " connection writing")
                        break
                    else:
                        current_bone=current_bone.children[0]
        f.close()

print("finish")