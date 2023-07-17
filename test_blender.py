import bpy
armature_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
for armature_obj in armature_objects:
    if armature_obj.name == 'metarig':
        for starting_bone in armature_obj.data.bones:
            print(starting_bone.children[0].name, starting_bone.children[0].tail_local)
            break