import numpy as np
import quaternion

def normalize(vector,desired_length=1):
    norm=np.linalg.norm(vector)
    ratio=norm/desired_length
    vector=np.divide(vector,ratio)
    
    return vector

def rotate_vector(vector, angle_degrees, axis):
    # Convert the angle from degrees to radians
    angle_radians = np.deg2rad(angle_degrees)

    #Normalize the axis
    axis = axis / np.linalg.norm(axis)

    # Normalize the vector
    vector = vector / np.linalg.norm(vector)

    # Create the rotation quaternion
    rotation_quaternion = quaternion.from_rotation_vector(angle_radians * axis)

    # Convert the vector to a pure quaternion
    vector_quaternion = quaternion.quaternion(0, *vector)

    # Apply the rotation using quaternion multiplication
    rotated_vector_quaternion = rotation_quaternion * vector_quaternion * rotation_quaternion.conjugate()

    # print("size of rotated_vector_quaternion:", np.shape(rotated_vector_quaternion))
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
        ori_on_plane=normalize(np.cross(normalize(np.subtract(a,b)), normalize(np.subtract(c,b))),delta)
        surface_normal=normalize(np.subtract(normalize(np.subtract(a,b)), normalize(np.subtract(c,b))))
    print('ori_on_plane', np.array2string(ori_on_plane,separator= ','))
    print("normal:", np.array2string(surface_normal,separator= ','))
    vertices=np.zeros(5, dtype=object)
    vertices[0]=b
    vertices[1]=ori_on_plane
    # calculate the vector first, add the origin (point b) later
    for i in range(2,5):
        vertices[i]=normalize(rotate_vector(vertices[i-1], 90, surface_normal),delta)
    # add the origin (point b) make it into vertices of the rectangle
    for i in range(1,5):
        vertices[i]=np.add(vertices[i],b)
    
    return vertices

delta=0.5
a=[-0.14888252317905426, 0.6568670272827148, 0.628582775592804]
b=[-0.16227105259895325, 0.6353074908256531, 0.3390066623687744]
c=[-0.14406679570674896, 0.6797270774841309, 0.07186122983694077]
print('a,b:', np.array2string(np.subtract(a,b),separator= ','))
print('c,b:', np.array2string(np.subtract(c,b),separator= ','))

print(get_pseudo_mesh_vertices(a, b, c, no_children=False, no_parent=False))