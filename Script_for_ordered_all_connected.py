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

def get_pseudo_mesh_vertices(d, n2v, n2sn, a=None, b=None, c=None,previous_joint_name=None, no_children=False, no_parent=False):
    # a:previous joint 
    # b:current joint 
    # c:next joint 
    # (xyz position)
    # return a list of four vertices of the sqaure mesh

    if no_children:
        # for node that has no children
        surface_normal=normalize(np.subtract(a,b))
        ori_on_plane=np.array([d,0,0])
        
    elif no_parent:
        # for node that has no parent
        surface_normal=normalize(np.subtract(c,b))
        ori_on_plane=np.array([d,0,0])
    else:
        ori_on_plane=normalize(np.cross(np.subtract(a,b), np.subtract(c,b)),d)
        surface_normal=normalize(np.subtract(normalize(np.subtract(a,b)), normalize(np.subtract(c,b))))
        # from two directons of surface_normal, find the one that has bigger inner product with previous surface_normal
        if np.inner(-surface_normal,n2sn[previous_joint_name]) >= np.inner(surface_normal,n2sn[previous_joint_name]):
            surface_normal=-surface_normal
    vertices=np.zeros(5, dtype=object)
    vertices[0]=b
    vertices[1]=ori_on_plane
    # calculate the vector first, add the origin (point b) later
    for i in range(2,5):
        vertices[i]=normalize(rotate_vector(vertices[i-1], 90, surface_normal),d)
    # to maintain consistency with respecto to previous joint, rearrange the order
    if not no_parent:
        # from four of the vectors, find the one that is closest to the first vector of previous joint.
        change_idx=np.argmax(np.array([np.dot(vector, n2v[previous_joint_name][1]) for vector in vertices[1:5]]))
        temp_vertices=vertices.copy()
        for i in range(4):
            if i+change_idx>3:
                temp_vertices[i+1]=vertices[(change_idx+i)%4+1]
            else:
                temp_vertices[i+1]=vertices[change_idx+i+1]
        vertices=temp_vertices
    # add the origin (point b) make it into vertices of the rectangle
    for i in range(1,5):
        vertices[i]=np.add(vertices[i],b)
    return surface_normal, vertices

def write_perpendicular_surface_connection_idx(bone_name, name2idx, file_to_write):
    #write connections on the surface perpendicular to surface normal
    idx=5*name2idx[bone_name]
    for i in range(4):
        # array_to_write=[idx, idx+1, idx+(i+1)%4+1]
        print('3', idx, idx+i+1, idx+(i+1)%4+1,file=file_to_write)
    
def write_parallel_surface_connection_idx(bone_name, previous_bone_name, name2idx, file_to_write):
    idx=5*name2idx[previous_bone_name]
    v=[idx, idx+1, idx+2, idx+3, idx+4]
    idx=5*name2idx[bone_name]
    i=[idx, idx+1, idx+2, idx+3, idx+4]

    print('3', v[1], i[1], i[2], file=file_to_write)
    print('3', i[2], v[2], v[1], file=file_to_write)
    print('3', v[2], i[3], i[2], file=file_to_write)
    print('3', v[2], v[3], i[3], file=file_to_write)
    print('3', v[3], i[4], i[3], file=file_to_write)
    print('3', v[3], v[4], i[4], file=file_to_write)
    print('3', v[4], i[1], i[4], file=file_to_write)
    print('3', v[4], v[1], i[1], file=file_to_write)

def write_that_fucking_cube(bone,delta):
    cube_vertices=list()
    


# Get all armature objects in the scene
armature_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
print('start')

delta=0.05 #delta control the width of the mesh
scale=10 #scaling the coordinate of the skeleton

nodes=list()
edges=list()
already_write_count=0
starting_point_count=0
name2idx=dict()
name2surface_normal=dict()
name2vertices=dict()
starting_viewed=False
add_vertical_planes=True
add_remark_in_file=False

spine_node_num=13
leg_node_num=5

# Iterate through each armature object
for armature_obj in armature_objects:
    if armature_obj.name == 'metarig':
        print("Armature:", armature_obj.name)
        f = open('D:/Download/3DScanning/Projects/Models/pseudo_mesh.off', 'w')

        print("COFF", file=f)

        #print (node_num, face_num, edge_num)
        #print(5*(spine_node_num+4*leg_node_num), 12*spine_node_num-8+4*(12*leg_node_num-8), 0, file=f)
        if add_vertical_planes:
            print('165 356 0', file=f)
        else:
            print('165 264 0', file=f)

        #start with head
        for starting_bone in armature_obj.data.bones:
            if starting_bone.parent is None:
                current_joint_coordinate=get_bone_coordinate(starting_bone, get_head=True)
                next_joint_coordinate=get_bone_coordinate(starting_bone)
                #get vectices and record writing index
                name2surface_normal['starting_point'+str(starting_point_count)], name2vertices['starting_point'+str(starting_point_count)]=\
                    get_pseudo_mesh_vertices(delta, name2vertices, name2surface_normal, b=current_joint_coordinate, c=next_joint_coordinate, no_parent=True)
                name2idx['starting_point'+str(starting_point_count)]=already_write_count
                #write vertices coordinates into file
                if add_remark_in_file:
                    print('#', 'starting_point'+str(starting_point_count), 15, file=f)
                for vertices in name2vertices['starting_point'+str(starting_point_count)]:
                    print(*vertices, file=f)
                already_write_count=already_write_count+1

                current_bone=starting_bone

                while True:
                    name2idx[current_bone.name]=already_write_count
                    already_write_count=already_write_count+1

                    if len(current_bone.children)==0: #beginning head
                        previous_joint_coordinate=get_bone_coordinate(current_bone, get_head=True)
                        current_joint_coordinate=get_bone_coordinate(current_bone)
                        name2surface_normal[current_bone.name], name2vertices[current_bone.name]=\
                            get_pseudo_mesh_vertices(delta, name2vertices, name2surface_normal, a=previous_joint_coordinate, b=current_joint_coordinate,
                            previous_joint_name=current_bone.parent.name,no_children=True)
                        #write vertices coordinates into file
                        if add_remark_in_file:
                            print('#', current_bone.name, 5, file=f)
                        for vertices in name2vertices[current_bone.name]:
                            print(*vertices, file=f)
                        print("Done with bone-chain", starting_point_count, "coordinates writing")
                        break
                    else:
                        previous_joint_coordinate=get_bone_coordinate(current_bone, get_head=True)
                        current_joint_coordinate=get_bone_coordinate(current_bone)
                        next_joint_coordinate=get_bone_coordinate(current_bone.children[0])
                        if current_bone.parent==None:
                            name2surface_normal[current_bone.name], name2vertices[current_bone.name]=\
                                get_pseudo_mesh_vertices(delta, name2vertices, name2surface_normal, a=previous_joint_coordinate,b=current_joint_coordinate,c=next_joint_coordinate,
                                previous_joint_name='starting_point'+str(starting_point_count))
                        else:
                            name2surface_normal[current_bone.name], name2vertices[current_bone.name]=\
                                get_pseudo_mesh_vertices(delta, name2vertices, name2surface_normal, a=previous_joint_coordinate,b=current_joint_coordinate,c=next_joint_coordinate,
                                previous_joint_name=current_bone.parent.name)
                        # write vertices coordinates into file
                        if add_remark_in_file:
                            print('#', current_bone.name, 5, file=f)
                        for vertices in name2vertices[current_bone.name]:
                            print(*vertices, file=f)
                        current_bone=current_bone.children[0]
                starting_point_count=starting_point_count+1

        #reset all counter
        starting_point_count=0
        #start with wirting edge into file
        for starting_bone in armature_obj.data.bones:
            if starting_bone.parent is None:
                if add_remark_in_file:
                    print('#', 'starting_point'+str(starting_point_count), file=f)
                write_perpendicular_surface_connection_idx('starting_point'+str(starting_point_count), name2idx,f)
                if add_remark_in_file:
                    print('#', starting_bone.name, file=f)
                write_perpendicular_surface_connection_idx(starting_bone.name, name2idx,f)
                write_parallel_surface_connection_idx(starting_bone.name, 'starting_point'+str(starting_point_count), name2idx, f)

                current_bone=starting_bone.children[0]
                while True:
                    if add_remark_in_file:
                        print('#', current_bone.name, file=f)
                    if add_vertical_planes:
                        write_perpendicular_surface_connection_idx(current_bone.name, name2idx,f)
                    write_parallel_surface_connection_idx(current_bone.name, current_bone.parent.name, name2idx, f)
                    if len(current_bone.children)==0:
                        print("Done with bone-chain", starting_point_count, " connection writing")
                        break
                    else:
                        current_bone=current_bone.children[0]
                starting_point_count=starting_point_count+1
        f.close()

print("finish")