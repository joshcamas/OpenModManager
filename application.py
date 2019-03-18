# Snapshot: 

import sys
import tkinter as tk
from tkinter import ttk as ttk

import math

import fluid.fluid_light as ui
import fluid.fluid_progressive_light as pui
import fluid.srcframe as srcframe

import openmm

class Application(ui.App):

    #Build application window
    def build(self):
        print("Building Application")
        
        #self.frame = srcframe.VerticalScrolledFrame(self.parent).interior

        self.vertical_frame = srcframe.VerticalScrollFrame(self.frame)
        self.vertical_frame.grid(row=0,column=0,sticky="WENS")

        self.vertical_interior = self.vertical_frame.interior
        
        
        self.frame.bind("<Configure>", self.onchange)
        
        #self.scrollbar_frame = ui.Frame(self.vertical_interior)
        
        #self.scrollbar_frame.grid(row=0,column=0,sticky="WENS")
        self.parent.geometry('900x350')

        self.profile_path = "profiles/"
        self.current_profile = None
        self.autosave = True
        self.buildapp()
    
    def onchange(self,event):

        self.frame.update_idletasks() 

        canvasWidth    = self.frame.winfo_width()
        canvasHeight   = self.frame.winfo_height()

        self.vertical_frame.changesize(canvasWidth,canvasHeight)
        
    def buildapp(self):
        
        #for widget in self.vertical_frame.frame.winfo_children():
        #   widget.destroy()
    
    
        self.ui = pui.Progress(self.vertical_interior)
        self.ui.setsticky("NW")
        self.ui.startvertical() #Start app
        self.ui.starthorizontal() #start top bar
		
        self.b_createprofile = self.ui.addbutton("Create Profile")
        self.b_createprofile.setcommand(self.open_createprofilewindow)

        self.i_loadprofile = self.ui.adddropdown("",["Load Profile"])
        self.i_loadprofile.setcommand(self.loadprofile)
        
        self.b_saveprofile = self.ui.addbutton("Quit")
        self.b_saveprofile.setcommand(self._quit)
        
        if(self.current_profile == None):
            self.b_saveprofile.button.config(state = tk.DISABLED)
            
        self.build_profilelist()
        #self.b_loadprofile.button.config(state = tk.DISABLED)
        
        self.ui.stophorizontal()

        if(self.current_profile):
            self.buildapp_main()
            
    def buildapp_main(self):
        self.ui.starttabs("Mods")
        
        self.ui.starthorizontal()
        
        #self.b_addmod = self.ui.addbutton("Add Mod")
        
        self.b_addmodf = self.ui.addbutton("Add Mod Folder")
        self.b_addmodf.setcommand(self.open_addmodfolderwindow)
        
        self.b_refresh = self.ui.addbutton("Refresh")
        self.b_refresh.setcommand(self.refresh)
        
        self.b_saveconfig = self.ui.addbutton("Save OpenMW Config")
        self.b_saveconfig.setcommand(self.saveconfig)
        
        self.ui.stophorizontal()
        
        self.ui.starthorizontal()
        
        self.buildapp_modlist()
        self.buildapp_contentlist()
        
        self.ui.stophorizontal()
        
     #   self.ui.newtab("Load Order")
     #   self.buildapp_loadorder()
        
        self.ui.newtab("Settings")
        
        self.ui.stoptabs()
    
    def buildapp_loadorder(self):
        self.ui.starthorizontal()
        
        self.buildapp_datalist()
        
        
        
        self.ui.stophorizontal()
    
    def buildapp_modlist(self):

        #Mod List
        self.ui.startvertical()
        self.ui.addlabel("Mod Order",True)
        
        profile = self.current_profile
        
        self.ui.starthorizontal()
        
        self.ui.startvertical()
        for i in range(len(profile.mods)):
            self.ui.starthorizontal()
            self.draw_mod(profile.mods[i],i)
            self.ui.stophorizontal()
            
        self.ui.stopvertical()
        self.ui.startvertical()
        
        for i in range(len(profile.mods)):
            self.ui.starthorizontal()
            self.draw_mod_buttons(profile.mods[i],i)
            self.ui.stophorizontal()
        
        self.ui.stopvertical()
        
        self.ui.stophorizontal()
        
        self.ui.stopvertical()
    
    def draw_mod(self,mod,i):
        profile = self.current_profile
        
        if(mod.lost):
            mod.enabled = False
            
        enabled = self.ui.addcheckbox("",mod.enabled)

        enabled.setcommand(lambda: self.on_command_togglemod(enabled,mod))
        
        labelstr = ""
        
        if(mod.lost):
            labelstr += "(MISSING) "
            
        if(mod.master):
            labelstr += "(MASTER) "

        labelstr += mod.name
        label = self.ui.addlabel(labelstr)
        
        label.label.config(height=1)
        
        if(mod.lost or mod.master):
            enabled.check.config(state = tk.DISABLED)
    
    def draw_mod_buttons(self,mod,i):
        profile = self.current_profile
        
        up = self.ui.addbutton("↑")
        down = self.ui.addbutton("↓")
    
        up.setcommand(lambda: self.on_command_moveup_mod(mod))
        down.setcommand(lambda: self.on_command_movedown_mod(mod))
        
        up.button.config(height=1)
        down.button.config(height=1)
        
        if(i == 0):
            up.button.config(state = tk.DISABLED)
            
        if(i == len(profile.mods)-1):
            down.button.config(state = tk.DISABLED)
        
        #If this object is not a master, and the above mod is a master, then
        #disable up arrow
        if(i != 0 and profile.mods[i].master == False):
            if(profile.mods[i-1].master):
                up.button.config(state = tk.DISABLED)
        
        #If this object is a master, and the below mod is not, disable down arrow
        if(i != len(profile.mods)-1 and profile.mods[i].master == True):
            if(profile.mods[i+1].master == False):
                down.button.config(state = tk.DISABLED)
                
                    
        if(mod.lost):
            remove = self.ui.addbutton("X")
            remove.setcommand(lambda: self.on_command_removemod(mod))


    def buildapp_contentlist(self):

         #Mod List
        self.ui.startvertical()
        
        self.ui.addlabel("ESP Order",True)

        profile = self.current_profile
        
        self.ui.starthorizontal()
        
        self.ui.startvertical()
        for i in range(len(profile.ordered_content)):
            self.ui.starthorizontal()
            
            self.draw_content(profile.ordered_content[i],i)

            self.ui.stophorizontal()
        self.ui.stopvertical()
        
        self.ui.startvertical()
        for i in range(len(profile.ordered_content)):
            self.ui.starthorizontal()
            
            self.draw_content_buttons(profile.ordered_content[i],i)

            self.ui.stophorizontal()
        self.ui.stopvertical()
        
        self.ui.stophorizontal()
        
        self.ui.stopvertical()
        
    
    def draw_content(self,content,index):
        
        mod = self.current_profile.get_mod(content.mod)
        
        if(mod.lost or content.lost):
            content.enabled = False
        
        #if(mod.enabled == False):
        #    content.enabled = False
            
        enabled = self.ui.addcheckbox("",content.enabled)

        enabled.setcommand(lambda: self.on_command_togglecontent(enabled,content))
        
        label = ""
        
        if(content.lost):
            label += "(MISSING) "
            
        if(mod.master):
            label += "(MASTER) "

        
        label += content.getname()
        
        self.ui.addlabel(label)
        
        if(content.lost or mod.lost or mod.master):
            enabled.check.config(state = tk.DISABLED)
        
        #if(mod.enabled == False):
        #    enabled.check.config(state = tk.DISABLED)
        
        if(content.lost):
            remove = self.ui.addbutton("X")
           # remove.setcommand(lambda: self.on_command_removemod(mod))

    def draw_content_buttons(self,content,i):
        profile = self.current_profile
        
        mod = self.current_profile.get_mod(content.mod)
        modindex = self.current_profile.get_mod_index(content.mod)
        
        
        up = self.ui.addbutton("↑")
        down = self.ui.addbutton("↓")
    
        up.setcommand(lambda: self.on_command_moveup_content(content))
        down.setcommand(lambda: self.on_command_movedown_content(content))
        
        if(i == 0):
            up.button.config(state = tk.DISABLED)
            
        if(i == len(profile.ordered_content)-1):
            down.button.config(state = tk.DISABLED)
        
        '''
        #If this object is not a master, and the above mod is a master, then
        #disable up arrow
        if(i != 0 and profile.mods[modindex].master == False):
            if(profile.mods[i-1].master):
                up.button.config(state = tk.DISABLED)
        
        #If this object is a master, and the below mod is not, disable down arrow
        if(modindex != len(profile.mods)-1 and profile.mods[modindex].master == True):
            if(profile.mods[i+1].master == False):
                down.button.config(state = tk.DISABLED)
        '''
                    
        if(mod.lost or content.lost):
            remove = self.ui.addbutton("X")
            remove.setcommand(lambda: self.on_command_removemod(mod))

        
    def open_createprofilewindow(self):
        t = tk.Toplevel(self.frame)
        t.wm_title("Create profile")
        
        self.initwindow = t
        
        app = CreateProfileWindow(t)
        app.frame.pack(side="top", fill="both", expand=True)
        app.build(self.on_profile_create)
    
    def on_command_movedown_mod(self,mod):
        self.current_profile.move_mod(mod,False)
        self.buildapp()
        self.autosaveprofile()
        
    
    def on_command_moveup_mod(self,mod):
        self.current_profile.move_mod(mod,True)
        self.buildapp()
        self.autosaveprofile()
        
    def on_command_movedown_content(self,content):
        self.current_profile.move_content(content,False)
        self.buildapp()
        self.autosaveprofile()
        
    def on_command_moveup_content(self,content):
        self.current_profile.move_content(content,True)
        self.buildapp()
        self.autosaveprofile()
        
        
    def on_command_togglecontent(self,checkbox,content):
        value = checkbox.getvalue()
        
        if(value == 1 and content.enabled == False):
            self.on_content_enable(content)
        
        elif(value == 0 and content.enabled == True):
            self.on_content_disable(content)
            
    
    def on_command_togglemod(self,checkbox,mod):
                    
        value = checkbox.getvalue()
        
        if(value == 1 and mod.enabled == False):
            self.on_mod_enable(mod)
        
        elif(value == 0 and mod.enabled == True):
            self.on_mod_disable(mod)
                
    def on_command_removemod(self,mod):
        self.current_profile.remove_mod(mod)
        self.buildapp()
    
    def open_addmodfolderwindow(self):
        t = tk.Toplevel(self.frame)
        t.wm_title("Add Mod Folder")
        
        self.initwindow = t
        
        app = CreateModFolderWindow(t)
        app.frame.pack(side="top", fill="both", expand=True)
        app.build(self.on_modfolder_create)
    
    
    def loadprofile(self,*args):
        name = self.i_loadprofile.getvalue()

        if(name == "Load Profile"):
            return
            
        profile = openmm.load_profile(self.profile_path,name)
        
        if(profile == None):
            print("Could Not load profile!")
            return
            
        self.current_profile = profile
        self.current_profile.onload()
        
        self.buildapp()
    
    def saveprofile(self):
        self.current_profile.save_json(self.profile_path)

    def autosaveprofile(self):
        if(self.autosave):
            self.saveprofile()
            
    def on_profile_create(self,profile):
        #Set as current
        self.current_profile = profile
        self.current_profile.onload()

        #Save profile
        self.saveprofile()
        
        self.buildapp()
        self.build_profilelist()
        
        self.autosaveprofile()

    def on_modfolder_create(self,mod):
        
        #self.current_profile.mods.append(mod)
        
        #add mod folder to list
        self.current_profile.mod_folders.append(mod)
        
        self.current_profile.onload()
        #Update list
        self.buildapp()
        
        self.autosaveprofile()
        
    def build_profilelist(self):
        options = []
        options.append("Load Profile")
        
        profiles = openmm.getall_profiles(self.profile_path)
        
        for i in range(len(profiles)):
            options.append(profiles[i])
            
        self.i_loadprofile.setoptions(options)
        
        '''
        if(self.current_profile != None):
            
            print(self.i_loadprofile.getvalue())
            print(self.current_profile.name)
            
            if(self.i_loadprofile.getvalue() != self.current_profile.name):
                self.i_loadprofile.setvalue(self.current_profile.name)
        '''
    
    def on_mod_enable(self,mod):
        mod.enabled = True
        print("ENABLE")
        
        self.autosaveprofile()
    
    def on_mod_disable(self,mod):
        mod.enabled = False
        print("DISABLE")
        
        self.autosaveprofile()
    
    def on_content_enable(self,content):
        content.enabled = True
        print("ENABLE")
        
        self.autosaveprofile()

    def on_content_disable(self,content):
        content.enabled = False
        print("DISABLE")
        
        self.autosaveprofile()
        
    def refresh(self):
        self.current_profile.onload()
        self.buildapp()
            
    def saveconfig(self):
        self.current_profile.save_config()
        
    def _quit(self):
        root.quit()
        root.destroy()

class CreateModFolderWindow(ui.App):
        #Build application window
    def build(self,oncreate):
        self.frameColor = "#e3e3e3"
        self.oncreate = oncreate
        self.buildapp()
	
    def buildapp(self):
        self.ui = pui.Progress(self)
        self.ui.setsticky("NW")
        self.ui.startvertical() #Start app
        
        self.ui.starthorizontal()
        
        self.ui.startvertical()
        self.i_folder= self.ui.addinputbox("Folder:","",False)
        self.ui.addlabel("The Folder structure must be correct")
        #self.i_zip= self.ui.addinputbox("Zip File:","D:/Projects/Morrowind_Multiplayer/Mods/",False)
        self.ui.stopvertical()

        self.ui.startvertical()
        #Blank
        self.ui.addlabel("")
        self.b_change_folder = self.ui.addbutton("Change")
        self.ui.stopvertical()

        self.ui.stophorizontal()
        
        self.ui.starthorizontal()
        self.b_cancel = self.ui.addbutton("Cancel")
        self.b_create = self.ui.addbutton("Create")
        self.ui.stophorizontal()
        
        #application settings
        self.b_cancel.setcommand(self._close)
        self.b_create.setcommand(self._create)
    
    def _create(self):
        #Create new profile
        #mod = openmm.Mod()
        #mod.name = self.i_name.getvalue()
        #mod.path = 
        self.oncreate(self.i_folder.getvalue())
        
        self._close()
        
    def _close(self):
        self.parent.destroy()
    
    
class CreateProfileWindow(ui.App):
        #Build application window
    def build(self,oncreate):
        self.frameColor = "#e3e3e3"
        self.oncreate = oncreate
        self.buildapp()
	
    def buildapp(self):
        self.ui = pui.Progress(self)
        self.ui.setsticky("NW")
        self.ui.startvertical() #Start app
        
        self.ui.starthorizontal()
        
        self.ui.startvertical()
        self.i_name= self.ui.addinputbox("Profile Name:","profile1",False)
        self.i_config_path= self.ui.addinputbox("OpenMW Config:","C:/Users/Josh/Documents/My Games/OpenMW/openmw.cfg",False)
        self.i_mod_path= self.ui.addinputbox("Default Mod Folder:","D:/Projects/Morrowind_Multiplayer/Mods/",False)
        self.ui.stopvertical()

        self.ui.startvertical()
        #Blank
        self.ui.addlabel("")
        self.b_changeconfig = self.ui.addbutton("Change")
        self.ui.stopvertical()

        self.ui.stophorizontal()
        
        self.ui.starthorizontal()
        self.b_cancel = self.ui.addbutton("Cancel")
        self.b_create = self.ui.addbutton("Create")
        self.ui.stophorizontal()
        
        #application settings
        self.b_cancel.setcommand(self._close)
        self.b_create.setcommand(self._create)
    
    def _create(self):
        #Create new profile
        profile = openmm.Profile()
        profile.name = self.i_name.getvalue()
        profile.openmw_config_path = self.i_config_path.getvalue()
        profile.mod_folders.append(self.i_mod_path.getvalue())
        self.oncreate(profile)
        
        self._close()

    def _close(self):
        self.parent.destroy()
    
if __name__ == "__main__":
    root = tk.Tk()
    
   # sw = tk.tix.ScrolledWindow(root, width=500, height=500)
    #sw.pack()
    
    app = Application(root)
    app.frame.pack(side="top", fill="both", expand=True)
    app.build()
    root.title("Open Mod Manager")
    root.mainloop()
    
