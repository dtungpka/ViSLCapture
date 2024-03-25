import pyrealsense2 as rs
import numpy as np
import cv2
import tifffile as tiff
import os
import time
import json
STREAM_TYPES = {
    rs.stream.color: 'Color',
    rs.stream.depth: 'Depth',
    rs.stream.infrared: 'Infrared',
    rs.stream.accel: 'Accel',
    rs.stream.gyro: 'Gyro',
    rs.stream.fisheye: 'Fisheye',
    rs.stream.pose: 'Pose',
    rs.stream.confidence: 'Confidence'
    
}

#Record all time, and timplement a exeprimental timeline func
#TODO: Onlyu save image when no motion. else save in ram

class Recorder:
    def __init__(self,filename:str,pose_name,pose_count=10,enable_view=True,save_img=True) -> None:
        if '.bag' not in filename.lower():
            filename += '.bag'
        self.align = rs.align(rs.stream.color)
        self.savepath = os.path.join(os.getcwd(),'output',filename[:-4])
        self.save_img = save_img
        self.enable_view = enable_view
        self.pose_name = pose_name  
        self.pose_count = pose_count
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
        self.config.enable_record_to_file(os.path.join(os.getcwd(),'output',filename))
        self.profile = self.pipeline.start(self.config)
        print("Recorder initialized")
        intr = self.profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        print(intr.width, intr.height, intr.fx, intr.fy, intr.ppx, intr.ppy)
        self.timeline = []
    def set_timeline_keypoint(self,frame:int,action:str):
        self.timeline.append((frame,action))
    
    def get_timeline_label(self):
        if len(self.timeline) == 0:
            return f"Ready to record {self.pose_name}|0/{self.pose_count} {0.00}%"
        else:
            return f"Recording {self.pose_name}|{len(self.timeline)}/{self.pose_count} {len(self.timeline)/self.pose_count*100:.2f}%"

    def update(self):
        current_frame = 0
        try:
            current_frame += 1
            _st_time = time.time()
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            depth_frame = aligned_frames.get_depth_frame()
            depth_frame = rs.decimation_filter(1).process(depth_frame)
            depth_frame = rs.disparity_transform(True).process(depth_frame)
            depth_frame = rs.spatial_filter().process(depth_frame)
            depth_frame = rs.temporal_filter().process(depth_frame)
            depth_frame = rs.disparity_transform(False).process(depth_frame)
            # depth_frame = rs.hole_filling_filter().process(depth_frame)
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image1 = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            #add timeline label to color image
            cv2.putText(color_image1,self.get_timeline_label(),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            if self.enable_view:
                cv2.imshow('Color Stream', color_image1)
                cv2.imshow('Depth Stream', depth_color_image )
                cv2.waitKey(1)
            if self.save_img:
                cv2.imwrite(os.path.join(self.rgbpath,f'{current_frame}.jpg'),color_image1)
                cv2.imwrite(os.path.join(self.depthpath,f'{current_frame}.jpg'),depth_color_image)
                #save depth as tiff
                tiff.imsave(os.path.join(self.depthpath,f'{current_frame}.tiff'),depth_image)
            #print(f'Frame {current_frame} saved in {time.time()-_st_time}s')
            #if space pressed, add keypoint
            if cv2.waitKey(1) & 0xFF == ord(' '):
                self.set_timeline_keypoint(current_frame,'keypoint')
            #if q pressed, stop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.set_timeline_keypoint(current_frame,'stop')
                break
        except KeyboardInterrupt:
            pass


        finally:
            self.pipeline.stop()
            #save timeline to  json
            with open(os.path.join(self.savepath,f'timeline_{self.pose_name}.json'),'w') as f:
                json.dump(self.timeline,f)

    def stop(self):
        self.pipeline.stop()
        print("Recorder stopped")



if __name__ == "__main__":
    recorder = Recorder("test2.bag","Hello",3,enable_view=True,save_img=False)
    recorder.start(-1)
   # recorder.stop()

