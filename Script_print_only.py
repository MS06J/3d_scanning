import bpy
import numpy as np
# import scipy as sp

# def normalize(vector,desired_length=1):
#     norm=np.linalg.norm(vector)
#     ratio=norm/desired_length
#     vector=np.devide(vector,ratio)

#     return vector

# def pseudo_mesh_orientation(a, b, c):
#     ori_on_plane=np.divide(np.add(normalize(np.subtract(a,b)),normalize(np.subtract(c,b))),2)
#     surface_normal=np.cross(ori_on_plane,np.cross(a,ori_on_plane))
#     #retract the length of ori to delta
#     ori_on_plane=normalize(ori_on_plane,delta)
#     ori_on_plane_1=sp.spatial.transform.Rotation.from_rotvec(ori_on_plane,)




# Get all armature objects in the scene
armature_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
print('start')

delta=0.01 #delta control the width of the mesh

nodes=list()
edges=list()
name2idx=dict()
starting_viewed=False

# Iterate through each armature object
for armature_obj in armature_objects:
    if armature_obj.name == 'metarig':
        print("Armature:", armature_obj.name)
        f = open('D:/Download/3DScanning/Projects/Models/pinocchino_skeleton.off', 'w')
        #print("appearance {linewidth 10}\n", file=f)
        print("node_name x y z previous_node_name", file=f)
        
        #save head location for the starting bone (only run once)
        for bone in armature_obj.data.bones:
            if bone.parent is None and starting_viewed == False:
                #point=["starting point", str(bone.head_local.x), str(bone.head_local.y), str(bone.head_local.z)]
                point=[str(bone.head_local.x), str(bone.head_local.y), str(bone.head_local.z)]
                nodes.append(point)
                break

        #save tail location for all bones
        for bone in armature_obj.data.bones:  
            if bone.parent is None:
                #point=[bone.name, str(bone.tail_local.x), str(bone.tail_local.y), str(bone.tail_local.z), 'starting point']
                point=[str(bone.tail_local.x), str(bone.tail_local.y), str(bone.tail_local.z)]
            else:
                point=[str(bone.tail_local.x), str(bone.tail_local.y), str(bone.tail_local.z)]
                #point=[bone.name, str(bone.tail_local.x), str(bone.tail_local.y), str(bone.tail_local.z), bone.parent.name]
            nodes.append(point)
            name2idx[bone.name] = len(nodes)-1
            
        # #adding edges
        # for bone in armature_obj.data.bones:
        #     if bone.parent is None:
        #         edges.append([str(name2idx[bone.name]), '0'])
        #     else:
        #         edges.append([str(name2idx[bone.name]),str(name2idx[bone.parent.name])])

        for i in range(len(nodes)):
            #print(i, ' '.join(nodes[i]), file=f)
            print(' '.join(nodes[i]), file=f)
        # for i in range(len(edges)):
        #     print(i, ' '.join(edges[i]), file=f)

        f.close()

print("end")
                
        