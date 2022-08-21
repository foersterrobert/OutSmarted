import bpy
import bpy_extras
import random
import os

startPath = r'C:\Users\Robert\Downloads\renderpics\labelren'

#Camera angle randomize
def set_camera_random():
    camposx=random.uniform(30,70)
    camposy=random.uniform(130,160)
    camposz=random.uniform(30,70)
    bpy.data.objects["Camera"].location[0]=camposx
    bpy.data.objects["Camera"].location[1]=camposy
    bpy.data.objects["Camera"].location[2]=camposz
    
def set_light_random():
    bpy.data.objects["light"].rotation_euler[0]=random.uniform(-8,8)
    bpy.data.objects["light"].rotation_euler[1]=random.uniform(-8,8)
    bpy.data.objects["light"].rotation_euler[2]=random.uniform(-8,8)
    bpy.data.objects["light"].location[0]=random.uniform(30,50)
    bpy.data.objects["light"].location[1]=random.uniform(-30,0)
    bpy.data.objects["light"].location[2]=random.uniform(190,280)
    bpy.data.materials["Material.092"].node_tree.nodes["Emission"].inputs[1].default_value=random.uniform(1,100)
    bpy.data.materials["Material.092"].node_tree.nodes["Emission"].inputs[0].default_value[0]=random.uniform(0,1)
    bpy.data.materials["Material.092"].node_tree.nodes["Emission"].inputs[0].default_value[1]=random.uniform(0,1)
    bpy.data.materials["Material.092"].node_tree.nodes["Emission"].inputs[0].default_value[2]=random.uniform(0,1)
    bpy.data.materials["Material.092"].node_tree.nodes["Emission"].inputs[0].default_value[3]=random.uniform(0.8,1) 
    
    bpy.data.objects["light.001"].rotation_euler[0]=random.uniform(-15,15)
    bpy.data.objects["light.001"].rotation_euler[1]=random.uniform(-15,15)
    bpy.data.objects["light.001"].rotation_euler[2]=random.uniform(-15,15)
    bpy.data.objects["light.001"].location[1]=random.uniform(-15,30)
    bpy.data.objects["light.001"].location[2]=random.uniform(10,100)
    bpy.data.materials["Material.001"].node_tree.nodes["Emission"].inputs[1].default_value=random.uniform(1,100)
    bpy.data.materials["Material.001"].node_tree.nodes["Emission"].inputs[0].default_value[0]=random.uniform(0,1)
    bpy.data.materials["Material.001"].node_tree.nodes["Emission"].inputs[0].default_value[1]=random.uniform(0,1)
    bpy.data.materials["Material.001"].node_tree.nodes["Emission"].inputs[0].default_value[2]=random.uniform(0,1)
    bpy.data.materials["Material.001"].node_tree.nodes["Emission"].inputs[0].default_value[3]=random.uniform(0.8,1) 

    bpy.data.objects["light.002"].rotation_euler[0]=random.uniform(-15,15)
    bpy.data.objects["light.002"].rotation_euler[1]=random.uniform(-15,15)
    bpy.data.objects["light.002"].rotation_euler[2]=random.uniform(-15,15)
    bpy.data.objects["light.002"].location[1]=random.uniform(-15,30)
    bpy.data.objects["light.002"].location[2]=random.uniform(10,100)
    bpy.data.materials["Material.003"].node_tree.nodes["Emission"].inputs[1].default_value=random.uniform(1,100)   
    bpy.data.materials["Material.003"].node_tree.nodes["Emission"].inputs[0].default_value[0]=random.uniform(0,1)
    bpy.data.materials["Material.003"].node_tree.nodes["Emission"].inputs[0].default_value[1]=random.uniform(0,1)
    bpy.data.materials["Material.003"].node_tree.nodes["Emission"].inputs[0].default_value[2]=random.uniform(0,1)
    bpy.data.materials["Material.003"].node_tree.nodes["Emission"].inputs[0].default_value[3]=random.uniform(0.8,1) 

def set_pieces_blank():
    for i in range(42):
        bpy.data.objects["white-half."+str(i)].hide_set(True)
        bpy.data.objects["black-half."+str(i)].hide_set(True)
        
    for i in range(42):
       bpy.data.objects["black-half."+str(i)].hide_viewport=True
       bpy.data.objects["white-half."+str(i)].hide_viewport=True
        
def set_pieces_random(): 
    #Toggling through row 0
    for i in range(7):
        ranchos=random.randint(0,2)
        
        if ranchos==0:
            bpy.data.objects["white-half."+str(i)].hide_set(False)
            bpy.data.objects["black-half."+str(i)].hide_set(True)
            
        elif ranchos==1:
            bpy.data.objects["white-half."+str(i)].hide_set(True)
            bpy.data.objects["black-half."+str(i)].hide_set(False)
        
     #   else:
      #     bpy.data.objects["white-half."+str(i)].hide_set(True)
        #   bpy.data.objects["black-half."+str(i)].hide_set(True)

    
    for j in range(1,6):
            v=j-1
        
            for i in range(7):
                ranchos2=random.randint(0,4)
                
                if bpy.data.objects["white-half."+str(i+(7*v))].visible_get()==True or bpy.data.objects["black-half."+str(i+(7*v))].visible_get()==True:
                    
                    if ranchos2==0 or ranchos2==2:
                        bpy.data.objects["white-half."+str(i+(7*j))].hide_set(False)
                        bpy.data.objects["black-half."+str(i+(7*j))].hide_set(True)
                        
                    elif ranchos2==1 or ranchos2==3:
                        bpy.data.objects["black-half."+str(i+(7*j))].hide_set(False)
                        bpy.data.objects["white-half."+str(i+(7*j))].hide_set(True)
                    
                    else:
                        bpy.data.objects["black-half."+str(i+(7*j))].hide_set(True)
                        bpy.data.objects["white-half."+str(i+(7*j))].hide_set(True)
                                                
                elif bpy.data.objects["white-half."+str(i+(7*v))].visible_get()==False and bpy.data.objects["black-half."+str(i+(7*v))].visible_get()==False:
                                        
                    bpy.data.objects["black-half."+str(i+(7*j))].hide_set(True)
                    bpy.data.objects["white-half."+str(i+(7*j))].hide_set(True)


    #Checking if visible in viewport and toggling in render
    for r in range(42):
        
        if bpy.data.objects["white-half."+str(r)].visible_get()==True:
            bpy.data.objects["white-half."+str(r)].hide_render=False
            
                
        elif bpy.data.objects["white-half."+str(r)].visible_get()==False:
            bpy.data.objects["white-half."+str(r)].hide_render=True
                
    for e in range(42):
        
        if bpy.data.objects["black-half."+str(e)].visible_get()==True:
            bpy.data.objects["black-half."+str(e)].hide_render=False
            
                
        elif bpy.data.objects["black-half."+str(e)].visible_get()==False:
            bpy.data.objects["black-half."+str(e)].hide_render=True
    

statelist = []

    
for i in range(42):
    statelist.append(0)
    
def get_statelist(a):
    for e in range(42):
               
        if bpy.data.objects["black-half."+str(e)].visible_get()==False and bpy.data.objects["white-half."+str(e)].visible_get()==False:
            statelist[e]=0
        elif bpy.data.objects["white-half."+str(e)].visible_get()==True:
            statelist[e]=1
        elif bpy.data.objects["black-half."+str(e)].visible_get()==True:
            statelist[e]=2
            
    with open(os.path.join(startPath, "lists/"+str(a)+"list.txt"), "w") as f:
        f.write(str(statelist))
        
#creating coordinates 
def get_coords(name):
    a=bpy.data.objects[name+"corner"].location[0]
    b=bpy.data.objects[name+"corner"].location[1]
    c=bpy.data.objects[name+"corner"].location[2]
    
    bpy.context.scene.cursor.location = (a, b, c)
    bpy.context.view_layer.objects.active = bpy.data.objects['Camera']        
    scene = bpy.context.scene
    obj = bpy.context.object
    co = bpy.context.scene.cursor.location
    
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene,obj, co)
    return co_2d

def get_coords_all(a):
    scene = bpy.context.scene
    render = scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    dl=get_coords("downleft")
    dr=get_coords("downright")
    ur=get_coords("upright")
    ul=get_coords("upleft")
    
    nul=[ul[0]*res_x,(ul[1])*res_y]
    nur=[ur[0]*res_x,(ur[1])*res_y]
    ndr=[dr[0]*res_x,(dr[1])*res_y]
    ndl=[dl[0]*res_x,(dl[1])*res_y]
    corray=[nul, nur, ndr, ndl]
    
    with open(os.path.join(startPath, "coords/"+str(a)+"coords.txt"), "w") as f:
        f.write(str(corray))

##renaming objects
#for i in range(42):
#    bpy.data.objects["black-half."+str(i+1)].name="black-half."+str(i)


def all_pieces_visible():
    for i in range(42):
        bpy.data.objects["black-half."+str(i)].hide_set(False)
        bpy.data.objects["white-half."+str(i)].hide_set(False)

    for i in range(42):
       bpy.data.objects["black-half."+str(i)].hide_viewport=False
       bpy.data.objects["white-half."+str(i)].hide_viewport=False
       
def set_background():
    bpy.data.materials["backgroundm"].node_tree.nodes["Noise Texture"].inputs[2].default_value=random.uniform(-80,80)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[4].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[5].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[6].default_value=random.uniform(0,1) 
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[7].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[8].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[9].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[10].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[11].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[12].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[13].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[14].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[15].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[17].default_value=random.uniform(0,1)
    bpy.data.materials["backgroundm"].node_tree.nodes["Principled BSDF"].inputs[18].default_value=random.uniform(0,1)
    bpy.data.objects["background"].location[0]=random.uniform(30,60)
    
def set_board():
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[4].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[5].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[6].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[7].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[8].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[9].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[10].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[11].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[12].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[13].default_value=random.uniform(0,1)
    bpy.data.materials["boardm"].node_tree.nodes["Principled BSDF"].inputs[14].default_value=random.uniform(0,1)

for b in range(800):
    a=b+4030
    
    if random.random() > 0.8:
        set_pieces_random()
    else:
        set_pieces_blank()
        
    set_camera_random()
    set_background()
    set_board()
    set_light_random()
    get_statelist(a)
    
    bpy.context.scene.render.image_settings.file_format='JPEG'
    bpy.context.scene.render.filepath = os.path.join(startPath, "pictures/"+str(a)+"lbrn.jpeg")
    bpy.ops.render.render(use_viewport = True, write_still=True)
    get_coords_all(a)
    
