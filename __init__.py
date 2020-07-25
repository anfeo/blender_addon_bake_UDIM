bl_info = {
    "name": "Bake UDIM Tiles",
    "author": "Alfonso Annarumma",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Render Properties > Bake",
    "description": "Baking UDIM Tiles with one click",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}


import bpy
import os
import bmesh

def uv_traslate(obj,i):
    me = obj.data
    bm = bmesh.new()
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()
    #bm.faces.layers.tex.verify()  # currently blender needs both layers.

    # scale UVs x2
    for f in bm.faces:
        for l in f.loops:
            l[uv_layer].uv[0] -= i

    #bm.to_mesh(me)
    me.update()


def bake_udim(context):
    obj = context.scene.view_layers[0].objects.active
    
    data = bpy.data
    images = data.images
    mat = obj.active_material
    nodes = mat.node_tree.nodes
    if nodes.active.type == 'TEX_IMAGE':
        if nodes.active.image.source =='TILED':
            
            udim_node = nodes.active
            udim = udim_node.image
            basename = bpy.path.basename(udim.filepath)
            udim_name = basename.split('.')[0]
            udim_dir = os.path.dirname(bpy.path.abspath(udim.filepath))
            split = udim.filepath.split('.')
            ext = split[-1]
            

            

            list = []

            for t in udim.tiles:
                list.append(t.number)
                
            i = 0
            l = len(list)-1
           

            for n in list:
                if obj.mode != 'EDIT':
                    bpy.ops.object.editmode_toggle()
                   
                    uv_traslate(obj,i)
                
                if obj.mode == 'EDIT':
                    bpy.ops.object.editmode_toggle()
                bake = images.new("bake", udim.size[0], udim.size[1], alpha=False, float_buffer=udim.is_float, stereo3d=False, is_data=False, tiled=False)
                bake_node = nodes.new("ShaderNodeTexImage")
                bake_node.name = "bake_image"
                bake_node.image = bake    
                nodes.active = bake_node
                bake_node.select = True
                
                
                filepath = udim_dir+'/'+udim_name+'.'+str(n)+"."+ext
                print(filepath)
                bake.filepath = filepath
                
                type = bpy.context.scene.cycles.bake_type
                bpy.ops.object.bake(type = type, filepath=filepath, save_mode='EXTERNAL')
                
                bake.save()
                
                nodes.remove(bake_node)
                images.remove(bake)
                
                if obj.mode != 'EDIT':
                    bpy.ops.object.editmode_toggle()
                   
                    uv_traslate(obj,-i)
                
                if obj.mode == 'EDIT':
                    bpy.ops.object.editmode_toggle()
                i += 1
        #        if i == l:
        #            f = -l
        #            if obj.mode != 'EDIT':
        #                bpy.ops.object.editmode_toggle()
        #            uv_traslate(obj,f)
        #            if obj.mode == 'EDIT':
        #                bpy.ops.object.editmode_toggle()
                
                
            
            nodes.active = udim_node
            udim.reload()
        else:
            print("Select Udim Node")
    else:
        print("Select Udim Node")
        
        
class SCENE_OT_Bake_Udim(bpy.types.Operator):
    """Select a UDIM Image Node"""
    bl_idname = "object.bake_udim"
    bl_label = "Bake for UDIM Image"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        
        bake_udim(bpy.context)
        
        return {'FINISHED'}

def menu_func(self, context):
    
    layout = self.layout
    layout.operator("object.bake_udim")


def register():
    bpy.utils.register_class(SCENE_OT_Bake_Udim)
    bpy.types.CYCLES_RENDER_PT_bake.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_Bake_Udim)
    bpy.types.CYCLES_RENDER_PT_bake.remove(menu_func)

if __name__ == "__main__":
    register()
