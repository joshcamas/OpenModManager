
import os
import json
from pprint import pprint

class Mod:
    def __init__(self):
        self.path = ""
        self.name = ""
        self.contents = []
        self.master = False
        self.enabled = False
        self.lost = False
        
        #Loose means it is not found in any of the mod folders
        self.loose = False
    
    @staticmethod
    def load(data):
        mod = Mod()
        mod.path = data['path']
        mod.name = data['name']
        mod.master = data['master']
        mod.enabled = data['enabled']
        mod.loose = data['loose']
        mod.lost = data['lost']
        mod.contents = data['contents']

        return(mod)
    
    def save(self):
        data = {}
        data['path'] = self.path
        data['name'] = self.name
        data['master'] = self.master
        data['enabled'] = self.enabled
        data['loose'] = self.loose
        data['lost'] = self.lost
        data['contents'] = self.contents

        return(data)
        
    def contains_content(self,content_path):
        for i in range(len(self.contents)):
            if(self.contents[i] == content_path):
                return True
        
        return False

    def add_content_path(self,content_path):
        if(self.contains_content(content_path)):
            return

        self.contents.append(content_path)
    
    #Builds content path
    def scan_mod(self):
        
        #Clear contents
        self.contents = []
        
        print("Scanning path " + self.name)
        
        try:
            for filename in os.listdir(self.path):
                if (filename.lower().endswith(".esp") or filename.lower().endswith(".esm")): 
                    name = os.path.basename(filename)
                    print("Found ESP/ESM: " + name)
                    
                    self.contents.append(name)
                    continue
                else:
                    continue
        except:
            pass


class Profile:
    def __init__(self):
        self.name = ""
        self.main_datafile_path = ""
        self.openmw_config_path = ""

        self.mod_folders = []
        
        #Ordered mods
        self.mods = []
        
        #Ordered content
        self.ordered_content = []
    
    def onload(self):
        #Scan config for changes
        self.scan_config()
        
        #Scan mod folders
        self.scan_modfolders()
        
        self.scan_modcontents()
        
        self.fill_contentlist()
    
    #Saves actual config!
    def save_config(self):
        
        #First remove all data lines
        
        lines_to_remove = []
        lines = []
        
        with open(self.openmw_config_path) as fp:  
            line = fp.readline()
            cnt = 0
            while line:
                lines.append(line)
                linesplit = line.strip().split("=")
                linetype = linesplit[0]
               
                if(linetype == "data"):
                    lines_to_remove.append(cnt)

                if(linetype == "content"):
                    lines_to_remove.append(cnt)

                line = fp.readline()
                cnt += 1
        
        #Open config
        with open(self.openmw_config_path,"w") as fp:  
            
            #Clear data / content lines
            cnt = 0
            for line in lines:
                found = False
                
                for i in range(len(lines_to_remove)):
                    if(lines_to_remove[i] == cnt):
                        found = True

                if (found == False):
                    fp.write(line)
                cnt += 1
            
            #Add data / content lines
            
            #data
            for i in range(len(self.mods)):
                if(self.mods[i].enabled):
                    line = 'data="' + os.path.normpath(self.mods[i].path) + '"\n'
                    fp.write(line)
            
            #content
            for i in range(len(self.ordered_content)):
                if(self.ordered_content[i].enabled and self.get_mod(self.ordered_content[i].mod).enabled):
                    line = 'content=' + self.ordered_content[i].path + '\n'
                    fp.write(line)
                    
    def move_mod(self,mod,up):
        index = self.get_mod_index(mod.name)
        
        if(up):
            self.mods[index], self.mods[index-1] = self.mods[index-1], self.mods[index]
        else:
            self.mods[index], self.mods[index+1] = self.mods[index+1], self.mods[index]
        
    def move_content(self,content,up):
        index = self.get_content_index(content.path)
        
        if(up):
            self.ordered_content[index], self.ordered_content[index-1] = self.ordered_content[index-1], self.ordered_content[index]
        else:
            self.ordered_content[index], self.ordered_content[index+1] = self.ordered_content[index+1], self.ordered_content[index]
        
        
    def mod_exists(self,path):
        for i in range(len(self.mods)):
            if(os.path.normpath(self.mods[i].path) == os.path.normpath(path)):
                return True
        
        return False
        
    def scan_modfolders(self):
        print("Starting Scan")
        newmods = []
        oldfoundmods = []
        
        #First tag all mods as not lost
        for i in range(len(self.mods)):
            self.mods[i].lost = False
        
        for i in range(len(self.mod_folders)):
            print("Scanning",self.mod_folders)
            newmods,oldfoundmods = self.scan_modfolder(self.mod_folders[i],newmods,oldfoundmods)
        
        #Go through mods and try to find ones that weren't found in the scan
        #If one is found, tag it as "lost"
        
        for i in range(len(self.mods)):
            
            #Ignore loose mods
            if(self.mods[i].loose == True):
                continue
            
            found = False
            for m in range(len(oldfoundmods)):
                if(os.path.normpath(self.mods[i].path) == os.path.normpath((oldfoundmods[m]))):
                    found = True
            
            if(found == False):
                print("Missing Mod: " + self.mods[i].name)
                self.mods[i].lost = True

        #Go through new mods and add them
        for i in range(len(newmods)):
            
            mod = Mod()
            mod.path = newmods[i]
            mod.path = mod.path.replace('"','')
            mod.name = os.path.split(newmods[i])[1]
            self.mods.append(mod)
            
            print("New Mod: " + mod.name)
            
    #Scan a folder
    def scan_modfolder(self,path,newmods,oldfoundmods):
        subdirs =  [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]

        for i in range(len(subdirs)):
            print("    Scanning subfolder",subdirs[i])
            if(self.mod_exists(path + subdirs[i]) == False):
                #Add mod
                newmods.append(path + subdirs[i])
            else:
                oldfoundmods.append(path + subdirs[i])

        return(newmods,oldfoundmods)
    
    def scan_modcontents(self):
        for i in range(len(self.mods)):
            self.mods[i].scan_mod()
            
    def find_master(self):
        for i in range(len(self.mods)):
            if(self.mods[i].name == "Master"):
                return self.mods[i]
                
        return None
    
    #Finds any content that is missing from the profile's list, and adds it to the bottom
    def fill_contentlist(self):
        
        oldfoundcontent = []
        newcontent = []
        for i in range(len(self.mods)):
            for c in range(len(self.mods[i].contents)):
                found = False
                for cc in range(len(self.ordered_content)):
                    if(self.ordered_content[cc].path == self.mods[i].contents[c]):
                        found = True
                        oldfoundcontent.append(self.ordered_content[cc])
                        break
                
                if(found == False):
                    print("adding content")
                    content = Content(self.mods[i].contents[c],self.mods[i].name,self.mods[i].enabled,False)

                    newcontent.append(content)
        
        #Look for content that is no longer valid. Tag "lost" if so
        '''
        for i in range(len(self.ordered_content)):
            for j in range(len(oldfoundcontent)):
                found = False
                if(os.path.normpath(self.ordered_content[i].path) == os.path.normpath(oldfoundcontent[j].path)):
                    found = True
            
            if(found == False):
                print("LOST Content: " + self.ordered_content[i].path)
                self.ordered_content[i].lost = True
        '''
        #Add new content
        for i in range(len(newcontent)):
            print("New Content: " + newcontent[i].path)
            self.ordered_content.append(newcontent[i])
        
    #Scans the config and updates for any files that are missing
    def scan_config(self):
        
        found_content = []
        found_data = []
        
        with open(self.openmw_config_path) as fp:  
            line = fp.readline()
            cnt = 1
            while line:
               
                linesplit = line.strip().split("=")
                linetype = linesplit[0]
               
                if(linetype == "data"):
                    print("Data:",linesplit[1])
                    found_data.append(linesplit[1])
                       
                if(linetype == "content"):
                    print("Content:",linesplit[1])
                    found_content.append(linesplit[1])

                line = fp.readline()
                cnt += 1
        
        '''
        #Create master if it does not exist
        master = self.find_master()
        
        if(master == None):
            master = Mod()
            master.name = "Master"
            master.master = True
            master.enabled = True
            master.loose = True
            self.mods.append(master)
        '''
        
        #Build new mods if they do not exist
        
        
       #Data
        for i in range(len(found_data)):

            found = False
            for m in range(len(self.mods)):
                np = os.path.normpath(found_data[i]).replace('"','')
                
                if(os.path.normpath(self.mods[m].path) == np):
                    found = True
                    break
            
            if(found == False):
                # new mod
                np = os.path.normpath(found_data[i]).replace('"','')

                newmod = Mod()
                newmod.path = np
                newmod.name = os.path.split(np)[1]
                newmod.loose = True
                newmod.lost = False
                newmod.enabled = True

                self.mods.append(newmod)
                
        '''
        #Content
        for i in range(len(found_content)):
            found = False
            for m in range(len(self.mods)):
                if(self.mods[m].contains_content(found_content[i])):
                    found = True
                    break
            
            if(found == False):
                #Add to master
                master.add_content_path(found_content[i])
        '''
        
    
    def remove_mod(self,mod):
        self.mods.remove(mod)
    
    def get_mod(self,name):
        for i in range(len(self.mods)):
            if(self.mods[i].name == name):
                return self.mods[i]
        
        return None
    
    def get_mod_index(self,name):
        for i in range(len(self.mods)):
            if(self.mods[i].name == name):
                return i
        
        return None
    
    def get_content_index(self,path):
        for i in range(len(self.ordered_content)):
            if(self.ordered_content[i].path == path):
                return i
        
        return None
        
    @staticmethod
    def get_json_path(path,name):
        return (path + name + ".json")
    
    @staticmethod
    def load_from_json(path,name):
        profile = Profile()
        try:
            data = json.load(open(Profile.get_json_path(path,name)))

        except:
            return None
        
        profile.name = name
        profile.mod_folders = data['mod_folders']
        profile.openmw_config_path = data['openmw_config']
        
        #Mods
        for i in range(len(data['mods'])):
            profile.mods.append(Mod.load(data['mods'][i]))
        
        #Content
        for i in range(len(data['ordered_content'])):
            profile.ordered_content.append(Content.load(data['ordered_content'][i]))
            
        return profile
	
    def save_json(self,path):
        #Build data
        data = {}
        data['mod_folders'] = self.mod_folders
        data['openmw_config'] = self.openmw_config_path
        data['mods'] = []
        data['ordered_content'] = []
        
        for i in range(len(self.mods)):
            data['mods'].append(self.mods[i].save())
        
        for i in range(len(self.ordered_content)):
            data['ordered_content'].append(self.ordered_content[i].save())
            
        #Save data
        with open(Profile.get_json_path(path,self.name), 'w') as outfile:  
            json.dump(data, outfile)
    
def get_supported_datafolders():
    supported = ["bookart", "fonts", "icons", "meshes", "music", "sound", "splash", "textures", "video"]
    return(supported)
    
def load_profile(path,name):
    #Create profile container

    profile = Profile.load_from_json(path,name)

    return profile

def getall_profiles(path):
	
    profiles = []
	
    for filename in os.listdir(path):
        if filename.endswith(".json"): 
            sp = filename.split(".")
            profiles.append(sp[0])
            continue
        else:
            continue
    return(profiles)
  
'''
class DataFolder:
    def __init__(self,path,mod):
        self.path = path
        self.mod = mod
    
    @staticmethod
    def load(data):
        datafolder = DataFolder(data['path'],data['mod'])
        return(datafolder)
        
    def save(self):
        data = {}
        data['path']  = self.path
        data['mod'] = self.mod 
        return(data)
'''  
class Content:
    def __init__(self,path,mod,enabled,lost):
        self.path = path
        self.mod = mod
        self.enabled = enabled
        self.lost = lost
    
    @staticmethod
    def load(data):
        content = Content(data['path'],data['mod'],data['enabled'],data['lost'])
        return(content)
    
    def save(self):
        data = {}
        data['path'] = self.path
        data['mod'] = self.mod 
        data['enabled'] = self.enabled
        data['lost'] = self.lost
        return(data)
    
    def getname(self):
        return os.path.split(self.path)[1]

