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
        ori_on_plane=normalize(np.cross(np.subtract(a,b), np.subtract(c,b)),delta)
        surface_normal=np.subtract(normalize(np.subtract(a,b)), normalize(np.subtract(c,b)))
    print("normal:", surface_normal)
    vertices=np.zeros(5, dtype=object)
    vertices[0]=b
    vertices[1]=ori_on_plane
    # calculate the vector first, add the origin (point b) later
    for i in range(2,5):
        vertices[i]=rotate_vector(vertices[i-1], 90, surface_normal)
    # add the origin (point b) make it into vertices of the rectangle
    # for i in range(1,5):
    #     vertices[i]=np.add(vertices[i],b)
    
    return vertices

delta=1
vector=np.array([0,0,-1])
normal=np.array([-1,1,0])
print("rotated:", rotate_vector(vector, 180, normal))
a=[1,2,0]
b=[1,1,0]
c=[2,1,0]
print('delta:', delta, get_pseudo_mesh_vertices(a, b, c, no_children=False, no_parent=False))