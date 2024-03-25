import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2
import pyrealsense2 as rs
import numpy as np
import os
import time
import sys

class SubWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuration")
        #set icon
        self.iconbitmap('Nahida_2.ico')
        self.geometry("400x200")  # Set the desired dimensions
        self.resizable(False, False)  # Disable resizing
        self.parent = parent
        default_save_location = os.path.join(os.getcwd(), "output")
        
        self.save_location_label = tk.Label(self, text="Save Location:")
        self.save_location_label.pack()
        
        self.save_location_entry = tk.Entry(self, width=50)
        self.save_location_entry.insert(0, default_save_location)
        self.save_location_entry.pack()

        
        
        self.name_label = tk.Label(self, text="Name:")
        self.name_label.pack()
        
        self.name_entry = tk.Entry(self, width=50)
        self.name_entry.pack()
        print(default_save_location)
        if os.path.exists(default_save_location):
            datas = os.listdir(default_save_location)
            print(datas)
            last_action = 0
            last_person = 0
            for data in datas:
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







        
        self.range_label = tk.Label(self, text="Repeats:")
        self.range_label.pack()

        
        self.range_entry = tk.Entry(self, width=50)
        self.range_entry.pack()
        self.range_entry.insert(0, 11)
        
        self.confirm_button = tk.Button(self, text="Confirm", command=self.confirm)
        self.confirm_button.pack()
        
    def confirm(self):
        self.parent.set_parameters(self.save_location_entry.get(), self.name_entry.get(), self.range_entry.get())
        #close the window
        self.destroy()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D455 Capture")
        self.iconbitmap('Nahida_2.ico')
        self.geometry("1480x680")  # Set the correct dimensions
        
        self.rgb_frame = tk.Label(self, width=640, height=480)
        self.rgb_frame.grid(row=0, column=0, sticky="nsew")
        
        self.depth_frame = tk.Label(self, width=640, height=480)
        self.depth_frame.grid(row=0, column=1, sticky="nsew")
        
        self.capture_button = tk.Button(self, text="Capture", command=self.capture_video, bg="green")
        self.capture_button.grid(row=1, column=0, columnspan=2, pady=10)


        self.timeline_label = tk.Label(self, text="Waiting for configuration...")
        self.timeline_label.grid(row=1, column=1, columnspan=2, )
        self.timeline_label.config(font=("Courier", 20))
        self.timeline_label.config(anchor="center")
        self.timeline_label.config(justify="center")
        self.timeline_label.config(wraplength=1280)

        
        self.bind("<space>", self.capture_video)
        
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
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
        self.config.enable_stream(rs.stream.depth,  640, 480, rs.format.z16, 30)
        #self.config.enable_record_to_file(os.path.join(self.savepath,self.filename))
        self.config.enable_device_from_file(r"D:\2023-2024\Project\Realsense\output\A20P11\A20P11.bag")
        self.profile = self.pipeline.start(self.config)
        print("Recorder initialized")
        intr = self.profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        print(intr.width, intr.height, intr.fx, intr.fy, intr.ppx, intr.ppy)
        self.timeline = []
        self.timeline_label.config(text=self.get_timeline_label())
        self.is_initiated = True
        self.current_frame = 0
        self.current_timestamp = 0
    def set_timeline_keypoint(self,frame:int,action:str,time_stamp:float=0):
        self.timeline.append((frame,action,time_stamp))
    def get_bag_size(self):
        #update size of bag file every 5s
        if time.time() - self.update_size_ < 1:
            return self.bag_size
        self.update_size_ = time.time()
        #return size of bag file , as str. Format as GB if > 1GB else MB
        size = os.path.getsize(r"D:\2023-2024\Project\Realsense\output\A20P11\A20P11.bag")
        self.bag_size = f"{size/1024/1024/1024:.2f}GB" if size > 1024*1024*1024 else f"{size/1024/1024:.2f}MB"
        return self.bag_size
    def get_timeline_label(self):
        if len(self.timeline) == 0:
            return f"Ready to record {self.pose_name}|0/{self.pose_count-1} {0.00}% ({self.get_bag_size()})"
        else:
            return f"Recording {self.pose_name}|{len(self.timeline)-1}/{self.pose_count-1} {len(self.timeline)/self.pose_count*100:.2f}% ({self.get_bag_size()})"
 
    def set_parameters(self, save_location, name, range):
        print("Setting parameters...")
        self.save_location = save_location
        self.name = name
        self.range = int(range) 
        self.init_camera()
        self.update_frame()

    def update_frame(self):
        # Add code here to update the frame
        if time.time() - self.last_capture > 0.5:
            self.capture_button.config(bg="green")
        _st_time = time.time()
        
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        #set the current timestamp
        self.current_timestamp = color_frame.get_timestamp()
        color_image = np.asanyarray(color_frame.get_data())
        depth_frame = aligned_frames.get_depth_frame()
        depth_frame = rs.decimation_filter(1).process(depth_frame)
        #depth_frame = rs.disparity_transform(True).process(depth_frame)
        #depth_frame = rs.spatial_filter().process(depth_frame)
        #depth_frame = rs.temporal_filter().process(depth_frame)
        depth_frame = rs.disparity_transform(False).process(depth_frame)
        # depth_frame = rs.hole_filling_filter().process(depth_frame)
        depth_image = np.asanyarray(depth_frame.get_data())
        #color_image1 = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        depth_color_frame = rs.colorizer().colorize(depth_frame)
        depth_color_image = np.asanyarray(depth_color_frame.get_data())
        #add timeline label to color image
        #cv2.putText(color_image,self.get_timeline_label(),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
        depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_BGR2RGB)

        # Convert the images to PIL format...
        image = Image.fromarray(color_image)
        depth_image = Image.fromarray(depth_color_image)

        # ...and then to ImageTk format
        imagetk = ImageTk.PhotoImage(image=image)
        depth_imagetk = ImageTk.PhotoImage(image=depth_image)

        # Update the canvas
        self.rgb_frame.configure(image=imagetk)
        self.depth_frame.configure(image=depth_imagetk)
        self.rgb_frame.image = imagetk
        self.depth_frame.image = depth_imagetk
        #print(f"FPS: {1/(time.time()-_st_time):.2f}")
        self.timeline_label.config(text=self.get_timeline_label())
        self.current_frame += 1
        if len(self.timeline) >= int(self.range):
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

            
            messagebox.showinfo("Recording completed!",f"Recording completed! {self.get_bag_size()}")


            self.destroy()
            
            

        else:
            # Repeat every 'interval' ms
            self.after(1, self.update_frame)







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
        

if __name__ == "__main__":
    window = MainWindow()
    subwindow = SubWindow(window)
    subwindow.mainloop()
    window.mainloop()
