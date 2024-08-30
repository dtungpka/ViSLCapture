import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2
import pyrealsense2 as rs
import numpy as np
import os
import time
import argparse
import yaml
import shutil


VERSION = "1.2.0-alpha"

class Config:
    running = True
    config_file_path = "config/config.yaml"
    config = None
    def __init__(self, config_file=None, action_map=None) :
        #if config file is not None, load the config file, else create a new one
        if config_file is not None:
            Config.config_file_path = config_file
        
        if os.path.exists(Config.config_file_path): 
            Config.load()
        else:
            Config.config = {
                "save_location": os.path.join(os.getcwd(), "output"),
                "name": "A0P0",
                "range": 10,
                "icon": "_internal/Nahida_2.ico",
                "action_map": "config/maps.txt",
                "rs_rgb_resolution": [640,480],
                "rs_depth_resolution": [640,480],
                "rs_rgb_fps": 30,
                "rs_depth_fps": 30,
                "start_person": 0
            }
        if action_map is not None:
            Config.config["action_map"] = action_map

        #check action map file if exist, then copy to _internal
        if os.path.exists(Config.config["action_map"]):
            shutil.copyfile(Config.config["action_map"],os.path.join('_internal',os.path.basename(Config.config["action_map"])))
        Config.save()
    def save():
        with open(Config.config_file_path, "w",encoding='utf-8') as f:
            yaml.dump(Config.config, f, default_flow_style=False)
    def load():
        with open(Config.config_file_path, "r",encoding='utf-8') as f:
            Config.config = yaml.load(f, Loader=yaml.FullLoader)
    def get(key):
        return Config.config[key]
    def set(key, value):
        Config.config[key] = value
        Config.save()




class SubWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuration")
        self.actions_list = {}
        #set icon
        self.iconbitmap(Config.get("icon"))
        self.geometry("400x200")  # Set the desired dimensions
        self.resizable(False, False)  # Disable resizing

        self.manual_id_inputed = False
        self.manual_action_name_inputed = False

        #Toolbar menu with: Options, Config, Map
        #Option with:Wipe data, Exit
        #Config with: Open config file, Open config folder
        #Map with: Open map file, Reset map file, Get online map file

        # Create the widgets
        self.parent = parent

        self.option_menu = tk.Menu(self)
        self.config_menu = tk.Menu(self)
        self.map_menu = tk.Menu(self)
        self.input_menu = tk.Menu(self)

        self.option_menu.add_command(label="Check missing", command=self.check_missing)
        self.option_menu.add_command(label="Wipe data", command=self.bui)
        self.option_menu.add_command(label="Exit", command=self.exit)

        self.config_menu.add_command(label="Open config file", command=self.open_config_file)
        self.config_menu.add_command(label="Open config folder", command=self.open_config_folder)

        self.map_menu.add_command(label="Open map file", command=self.open_map_file)
        self.map_menu.add_command(label="Overwrite map file", command=self.overwrite_map_file)
        self.map_menu.add_command(label="Reset map file", command=self.reset_map_file)
        self.map_menu.add_command(label="Get online map file", command=self.get_online_map_file)

        self.input_menu.add_command(label="Reset ID", command=self.reset_id, accelerator="Ctrl+R")
        self.input_menu.add_command(label="Reset Action Name", command=self.reset_action_name, accelerator="Ctrl+E")

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_cascade(label="Options", menu=self.option_menu)
        self.menu_bar.add_cascade(label="Config", menu=self.config_menu)
        self.menu_bar.add_cascade(label="Map", menu=self.map_menu)
        self.menu_bar.add_cascade(label="Input field", menu=self.input_menu)

        self.config(menu=self.menu_bar)




        default_save_location = Config.get("save_location")
        if os.path.exists(default_save_location):
            self.datas = os.listdir(default_save_location)
        else :
            os.makedirs(default_save_location)
            self.datas = os.listdir(default_save_location)
        self.save_location_label = tk.Label(self, text="Save Location:")
        self.save_location_label.pack()
        
        self.save_location_entry = tk.Entry(self, width=50)
        self.save_location_entry.insert(0, default_save_location)
        self.save_location_entry.pack()

        

        
        
        self.name_label = tk.Label(self, text="ID:") #A0P0
        self.name_label.pack()
        
        self.name_entry = tk.Entry(self, width=50)
        self.name_entry.pack()

        #action_name
        self.action_name_label = tk.Label(self, text="Action Name:")
        self.action_name_label.pack()
        self.action_name_entry = tk.Entry(self, width=50)
        self.action_name_entry.pack()




        print(default_save_location)
        if os.path.exists(default_save_location):
            self.datas = os.listdir(default_save_location)
            print(self.datas)
            last_action = 0
            last_person = 0
            for data in self.datas:
                if os.path.isdir(os.path.join(default_save_location,data)):
                    _action,_person = data.replace('A','').split("P")
                    #convert to int
                    _action = int(_action)
                    _person = int(_person)
                    #check if this is the lastest
                    if _action > last_action:
                        last_action = _action
                        last_person = _person
                    elif _action == last_action:
                        if _person > last_person:
                            last_person = _person
            if last_action != 0 and last_person != 0:
                self.name_entry.insert(0, f"A{last_action}P{last_person+1}")

        #add trigger to action_name_entry and name_entry when value is changed
        self.action_name_entry.bind("<KeyRelease>",self.update_id)
        self.name_entry.bind("<KeyRelease>",self.update_name)

        #shortcuts
        self.bind("<Control-r>", self.reset_id)
        self.bind("<Control-e>", self.reset_action_name)
            





        
        self.range_label = tk.Label(self, text="Repeats:")
        self.range_label.pack()

        
        self.range_entry = tk.Entry(self, width=50)
        self.range_entry.pack()
        self.range_entry.insert(0, Config.get("range"))
        
        self.confirm_button = tk.Button(self, text="Confirm", command=self.confirm)
        self.confirm_button.pack()

        self.update_name(None)
        self.update_id(None)

        #move the window to the center of the screen
        self.update()
        self.geometry(f"+{int(self.winfo_screenwidth()/2 - self.winfo_width()/2)}+{int(self.winfo_screenheight()/2 - self.winfo_height()/2)}")
        self.update()

    def wipe_data(self):
        #ask for confirmation, if yes, delete the content of the save location
        result = messagebox.askquestion("Wipe data", "Are you sure you want to wipe data?")
        if result == 'yes':
            shutil.rmtree(Config.get("save_location"))
            os.makedirs(Config.get("save_location"))
            self.datas = os.listdir(Config.get("save_location"))
            messagebox.showinfo("Wipe data","Wipe data completed!")
        self.focus_set()


    def exit(self):
        Config.running = False
        self.parent.stop()

    def open_config_file(self):
        #check if full path, if not then add full path
        temp_path = Config.config_file_path
        if not ':' in temp_path:
            temp_path = os.path.join(os.getcwd(),temp_path)

        os.startfile(temp_path)

    def open_config_folder(self):
        os.startfile(os.path.dirname(Config.config_file_path))

    def open_map_file(self):
        temp_path = Config.get("action_map")
        if not ':' in temp_path:
            temp_path = os.path.join(os.getcwd(),temp_path)
        os.startfile(temp_path)

    def overwrite_map_file(self):
        file = filedialog.askopenfile(mode='r', filetypes=[('Map Files','*.txt')])
        if file is None:
            return
        shutil.copyfile(file.name,Config.config["action_map"])
        shutil.copyfile(Config.config["action_map"],os.path.join('_internal',os.path.basename(Config.config["action_map"])))

        #show messagebox: Map file overwritten:.... and list content of the file
        with open(Config.config["action_map"], "r",encoding='utf-8') as f:
            content = f.read()
        messagebox.showinfo("Overwrite map file",f"Map file overwritten: {file.name}\n" + content)
        self.actions_list = {}
        self.focus_set()

    def reset_map_file(self):
        shutil.copyfile(os.path.join('_internal',os.path.basename(Config.config["action_map"])),Config.config["action_map"])
        messagebox.showinfo("Reset map file","Reset map file completed!")
        self.focus_set()

    def get_online_map_file(self):
        link = "https://daihocphenikaa-my.sharepoint.com/:f:/g/personal/21010294_st_phenikaa-uni_edu_vn/EklmQosvwLJImilJ2m2gz-4BdsznPj8e3DvosIE-VXDi2A?e=kE7eHT"
        os.startfile(link)

    def check_missing(self):
        missing_record = []
        _from_person = 999
        _to_person = 0
        for data in self.datas:
            if os.path.isdir(os.path.join(Config.get("save_location"),data)):
                _action,_person = data.replace('A','').split("P")
                #convert to int
                _action = int(_action)
                _person = int(_person)
                _from_person = min(_from_person,_person)
                _to_person = max(_to_person,_person)
        available_action = set([data.split("P")[0] for data in self.datas])
        for action_ID in available_action:
            for person in range(_from_person,_to_person+1):
                if not os.path.exists(os.path.join(Config.get("save_location"),f"{action_ID}P{person}")):
                    missing_record.append(f"{action_ID}P{person}: {self.actions_list[action_ID]}")
        
        if len(missing_record) == 0:
            messagebox.showinfo("Check missing","No missing record found!")
        else:
            messagebox.showinfo("Check missing",f"{len(missing_record)} missing record found!\n" + "\n".join(missing_record))
        #focus to the subwindow
        self.focus_set()


    def reset_id(self,event=None):
        self.manual_id_inputed = False
        self.update_id(None)

    def reset_action_name(self,event=None):
        self.manual_action_name_inputed = False
        action_name = self.load_action_name()
        self.action_name_entry.delete(0,tk.END)
        self.action_name_entry.insert(0,action_name)



    def load_action_name(self):
        if self.actions_list == {}:
            with open(Config.get("action_map"), "r",encoding='utf-8') as file:
                f = [line for line in file if '=>' in line]
                for line in f:
                    action, name = line.strip().split(" => ")
                    self.actions_list[action] = name
        action_name = '[Insert action]'
        input_id = self.name_entry.get()
        if "A" in input_id and "P" in input_id:
            action = input_id.split("P")[0]
            if action in self.actions_list:
                action_name = self.actions_list[action]
        return action_name
    
    def update_name(self,event): #name of action A00P00
        if event:
            self.manual_id_inputed = True   
        if self.manual_action_name_inputed:
            self.manual_action_name_inputed = True
            return
            

        action_name = self.load_action_name()
        if action_name == '[Insert action]' and self.action_name_entry.get() != '[Insert action]' and not  self.action_name_entry.get() in self.actions_list.values():
            action_name = self.action_name_entry.get()
        else:
            self.action_name_entry.delete(0,tk.END)
            self.action_name_entry.insert(0,action_name)

    def update_id(self,event): #name of action [Insert action]
        if event:
            self.manual_action_name_inputed = True
        if self.manual_id_inputed:
            self.manual_id_inputed = True
            return

        actionID = None
        action = None
        for action, name in self.actions_list.items():
            if name == self.action_name_entry.get():
                actionID = action
                break
        all_ap = {}
        for data in self.datas:
            if data.split("P")[0] not in all_ap:
                all_ap[data.split("P")[0]] = int(data.split("P")[1])
            else:
                all_ap[data.split("P")[0]] = max(all_ap[data.split("P")[0]],int(data.split("P")[1]))
        #print(all_ap)
        if actionID is None:
            #print(all_ap.keys())
            if all_ap == {}:
                actionID = f"A{int(action[1:])+1}"
            else:
                actionID = f"A{max([int(action[1:]) for action in all_ap.keys()]) + 1}"
            all_ap[actionID] = max(Config.get("start_person") - 1,0)
        if actionID not in all_ap:
            all_ap[actionID] = max(Config.get("start_person") - 1,0)
        self.name_entry.delete(0,tk.END)
        self.name_entry.insert(0,f"{actionID}P{all_ap[actionID]+1}")


    def save_action_name(self):
        name_entry = self.name_entry.get()
        action_name = self.action_name_entry.get()
        action = name_entry.split("P")[0]
        self.actions_list[action] = action_name
        with open(Config.get("action_map"), "w",encoding='utf-8') as f:
            for action, name in self.actions_list.items():
                f.write(f"{action} => {name}\n")

        

        
    def confirm(self):
        if Config.get("start_person") == 0:
            Config.set("start_person",int(self.name_entry.get().split("P")[1]))
        self.save_action_name()
        #close the window
        Config.save()
        self.parent.set_parameters(self.save_location_entry.get(), self.name_entry.get(), self.range_entry.get())
        
        self.destroy()

class MainWindow(tk.Tk):
    def __init__(self,debug=False):
        super().__init__()
        self.title("ViSL Capture" + " v" + VERSION)
        self.iconbitmap(Config.get("icon"))
        self.geometry("1480x680")  # Set the correct dimensions
        
        self.rgb_frame = tk.Label(self, width=640, height=480)
        self.rgb_frame.grid(row=0, column=0, sticky="nsew")
        
        self.depth_frame = tk.Label(self, width=640, height=480)
        self.depth_frame.grid(row=0, column=1, sticky="nsew")

        #exit menu btn
        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label="Exit", command=self.stop)
        self.config(menu=self.menu_bar)

        
        


        # Create a frame to hold the buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Create the discard button
        self.discard_button = tk.Button(button_frame, text="Discard", command=self.discard_video, bg="yellow", height=2, width=10)
        self.discard_button.pack(side=tk.LEFT, padx=5)

        # Create the capture button
        self.capture_button = tk.Button(button_frame, text="Capture", command=self.capture_video, bg="green", height=2, width=10)
        self.capture_button.pack(side=tk.LEFT, padx=5)


        self.timeline_label = tk.Label(self, text="Waiting for configuration...")
        self.timeline_label.grid(row=1, column=1, columnspan=2, )
        self.timeline_label.config(font=("Courier", 20))
        self.timeline_label.config(anchor="center")
        self.timeline_label.config(justify="center")
        self.timeline_label.config(wraplength=1280)


        self.bind("<space>", self.capture_video)
        #bing delete key to discard video
        self.bind("<Delete>", self.discard_video)

        #bind esc key to close the window
        self.bind("<Escape>", self.stop)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.save_location = None
        self.name = None
        self.range = None
        self.is_initiated = False
        self.last_capture = 0
        self.update_size_ = 0
        self.bag_size = 0

    def init_camera(self,save_img=True,enable_view=True,):
        #set RS2_OPTION_AUTO_EXPOSURE_PRIORITY to 0
        self.filename = self.name
        if '.bag' not in self.filename.lower():
            self.filename += '.bag'
        self.align = rs.align(rs.stream.color)
        self.savepath = os.path.join(self.save_location,self.filename[:-4])
        self.save_img = save_img
        self.enable_view = enable_view
        self.pose_name = self.name  
        self.pose_count = self.range
        os.makedirs(self.savepath,exist_ok=True)
        if save_img:
            self.rgbpath = os.path.join(self.savepath,'RGB')
            self.depthpath = os.path.join(self.savepath,'DEPTH')


            
            os.makedirs(self.rgbpath,exist_ok=True)
            os.makedirs(self.depthpath,exist_ok=True)
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        #RS2_OPTION_AUTO_EXPOSURE_PRIORITY
        
        
        rgb_res = Config.get("rs_rgb_resolution")
        depth_res = Config.get("rs_depth_resolution")
        rgb_fps = Config.get("rs_rgb_fps")
        depth_fps = Config.get("rs_depth_fps")

        self.config.enable_stream(rs.stream.color, rgb_res[0], rgb_res[1], rs.format.rgb8, rgb_fps)
        self.config.enable_stream(rs.stream.depth,  depth_res[0], depth_res[1], rs.format.z16, depth_fps)
        self.config.enable_record_to_file(os.path.join(self.savepath,self.filename))
        self.profile = self.pipeline.start(self.config)
        self.device = self.profile.get_device()
        sensor = self.device.first_depth_sensor()
        #sensor.set_option(rs.option.auto_exposure_mode,0)

        print("Recorder initialized")
        intr = self.profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        print(intr.width, intr.height, intr.fx, intr.fy, intr.ppx, intr.ppy)
        self.timeline = []
        self.timeline_label.config(text=self.get_timeline_label())
        self.is_initiated = True
        self.current_frame = 0
        self.current_timestamp = 0
        self.start_recording_time = time.time()
    def set_timeline_keypoint(self,frame:int,action:str,time_stamp:float=0):
        self.timeline.append((frame,action,time_stamp))
    def get_bag_size(self):
        #update size of bag file every 5s
        if time.time() - self.update_size_ < 1:
            return self.bag_size
        self.update_size_ = time.time()
        #return size of bag file , as str. Format as GB if > 1GB else MB
        size = os.path.getsize(os.path.join(self.savepath,self.filename))
        self.bag_size = f"{size/1024/1024/1024:.2f}GB" if size > 1024*1024*1024 else f"{size/1024/1024:.2f}MB"
        return self.bag_size
    def set_timeline_indicator(self):
        pass
    def get_timeline_label(self):
        if len(self.timeline) == 0:
            return f"Ready to record {self.pose_name}|0/{self.pose_count-1} {0.00}% ({self.get_bag_size()})"
        else:
            return f"Recording {self.pose_name}|{len(self.timeline)-1}/{self.pose_count-1} ({self.get_bag_size()})"
 
    def set_parameters(self, save_location, name, range):
        #set main focus to the main window ,and maximize it (not fullscreen)
        self.focus_set()
        self.state('zoomed')

        
        print("Setting parameters...")
        self.save_location = save_location
        self.name = name
        self.range = int(range) + 1 
        self.init_camera()
        self.update_frame()

    def update_frame(self):
        # Add code here to update the frame
        if time.time() - self.last_capture > 0.5:
            self.capture_button.config(bg="green")
            self.discard_button.config(bg="yellow")
            
        _st_time = time.time()
        
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        #set the current timestamp
        self.current_timestamp = color_frame.get_timestamp()
        color_image = np.asanyarray(color_frame.get_data())
        depth_frame = aligned_frames.get_depth_frame()
        #depth_frame = rs.decimation_filter(1).process(depth_frame)
        #depth_frame = rs.disparity_transform(True).process(depth_frame)
        #depth_frame = rs.spatial_filter().process(depth_frame)
        depth_frame = rs.temporal_filter().process(depth_frame)
        #depth_frame = rs.disparity_transform(False).process(depth_frame)
        # depth_frame = rs.hole_filling_filter().process(depth_frame)
        depth_image = np.asanyarray(depth_frame.get_data())
        #color_image1 = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        depth_color_frame = rs.colorizer().colorize(depth_frame)
        depth_color_image = np.asanyarray(depth_color_frame.get_data())
        #add timeline label to color image
        #cv2.putText(color_image,self.get_timeline_label(),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
        depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_BGR2RGB)
        if time.time()-_st_time > 0.05:
            print(f"Time to get frame: {time.time()-_st_time:.2f}")
        _st_time = time.time()
        # Convert the images to PIL format...
        image = Image.fromarray(color_image)
        depth_image = Image.fromarray(depth_color_image)

        # ...and then to ImageTk format
        imagetk = ImageTk.PhotoImage(image=image)
        depth_imagetk = ImageTk.PhotoImage(image=depth_image)
        if time.time()-_st_time > 0.05:
            print(f"Time to convert to ImageTk: {time.time()-_st_time:.2f}")
        _st_time = time.time()

        # Update the canvas
        self.rgb_frame.configure(image=imagetk)
        self.depth_frame.configure(image=depth_imagetk)
        self.rgb_frame.image = imagetk
        self.depth_frame.image = depth_imagetk
        if time.time()-_st_time > 0.05:
            print(f"Time to update frame: {time.time()-_st_time:.2f}")

        #print(f"FPS: {1/(time.time()-_st_time):.2f}")
        self.timeline_label.config(text=self.get_timeline_label())
        self.current_frame += 1
        if len(self.timeline) >= int(self.range) :
            #save timeline
            with open(os.path.join(self.savepath,'timeline.txt'),'w') as f:
                for frame,action,current_timestamp in self.timeline:
                    f.write(f"{frame},{action},{current_timestamp}\n")
            #show message
            self.timeline_label.config(text=f"Recording completed! {self.get_bag_size()}")
            #stop recording
            self.is_initiated = False
            #disable capture button
            self.capture_button.config(state=tk.DISABLED)
            #stop camera
            self.pipeline.stop()
            #close main window
            #show a message box

            
            result = messagebox.askquestion("Recording completed!", f"Recording completed! {self.get_bag_size()}\nDo you want to continue?")
            if result == 'yes':
                self.destroy()
            else:
                self.stop()

            

        else:
            # Repeat every 'interval' ms
            self.after(1, self.update_frame)





    def stop(self, event=None):
        Config.running = False
        if self.is_initiated:
            self.pipeline.stop()
        super().destroy()

    def destroy(self):
        if self.is_initiated:
            self.pipeline.stop()
        super().destroy()
    
    def capture_video(self, event=None):
        print("Capturing video...")
        if time.time() - self.last_capture < 0.5:
            return
        self.last_capture = time.time()
        #set the capture button to red
        self.capture_button.config(bg="red")
        self.set_timeline_keypoint(self.current_frame,"capture",self.current_timestamp)
    def discard_video(self, event=None):
        print("Discarding video...")
        if time.time() - self.last_capture < 0.5:
            return
        self.last_capture = time.time()
        self.discard_button.config(bg="red")
        self.pose_count += 1
        self.range += 1
        self.set_timeline_keypoint(self.current_frame,"discard",self.current_timestamp)
        pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ViSL Capture")
    parser.add_argument("--config",'-c', help="Path to the configuration file",default="config/config.yaml")
    parser.add_argument("--action_map",'-m', help="Path to the action map file",default="config/maps.txt")
    parser.add_argument("--debug",'-d', help="Debug mode",type=bool,default=False)
    args = parser.parse_args()

    while Config.running:
        Config(args.config,args.action_map)
        window = MainWindow(debug=args.debug)
        subwindow = SubWindow(window)
        subwindow.mainloop()
        Config.save()
        window.mainloop()
