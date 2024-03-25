
import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os
from tqdm import tqdm


TIME_FRAME = 100
TIME_FRAME_MIN = .2#1.5
TIME_FRAME_MAX = 12

def process_bag(bag_file,output_dir,timeline_array,timestamp_array,depth_copy_path=None):
    bag_name = os.path.basename(bag_file).replace('.bag','')
    #create folder for each bag file
    output_dir = os.path.join(output_dir,bag_name)
    os.makedirs(output_dir,exist_ok=True)
    #create 2 folder for rgb and depth
    rgb_dir = os.path.join(output_dir,'rgb')
    depth_dir = os.path.join(output_dir,'depth')
    os.makedirs(rgb_dir,exist_ok=True)
    os.makedirs(depth_dir,exist_ok=True)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(bag_file)
    profile = pipeline.start(config)
    align_to = rs.stream.color
    align = rs.align(align_to)
    current_frame = 0
    d_c_fr = 0
    depth_sequences = {} #np.zeros((TIME_FRAME,480,640),dtype=np.uint16)
    stop = False
    #create pair of timeline_array: (timeline_array[i],timeline_array[i+1]]),...
    timeline_pairs = []
    for i in range(len(timestamp_array) - 1):
        if timestamp_array[i+1] - timestamp_array[i] > TIME_FRAME_MIN * 1000 and timestamp_array[i+1] - timestamp_array[i] < TIME_FRAME_MAX * 1000:
            timeline_pairs.append((timeline_array[i],timeline_array[i+1],timestamp_array[i],timestamp_array[i+1]))
    current_video_render = None
    current_depth_matrix = None
    written_pairs = 0
    while not stop:
        try:
            #print(current_frame)
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            current_frame_timestamp = color_frame.get_timestamp()

            #_t = [str(round(color_frame.get_timestamp()-t,5)) for t in timeline_array]

            #depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            #print(frames.get_timestamp())
            for i,(start_frame,end_frame,start_stamp,end_stamp) in enumerate(timeline_pairs):
                end_frame = int((end_stamp - start_stamp) /1000 * 60) + start_frame 
                dur = int((end_stamp - start_stamp) /1000 * 60) + 1
                keypoint = (start_frame,end_frame) 
                if current_frame_timestamp < end_stamp and current_frame_timestamp >= start_stamp:
                    #if start_frame then init cv save avi
                    if abs(current_frame_timestamp - start_stamp) <= .1 and not current_video_render:
                        #init video writer
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        current_video_render = cv2.VideoWriter(os.path.join(rgb_dir,f'{start_frame}_{bag_name}_.avi'),fourcc, 30.0, (640,480))
                        depth_sequences[keypoint] = np.zeros((dur ,480,640),dtype=np.uint16)
                        d_c_fr = current_frame
                    
                    #if end_frame then release video writer
                    if abs(current_frame_timestamp - end_stamp) <= 40 and current_video_render:
                        print(f'Releasing video {keypoint}...')
                        #crop depth_sequences
                        _depth_sequences = depth_sequences[keypoint][:current_frame - d_c_fr + 1]

                        np.save(os.path.join(depth_dir,f'{keypoint[0]}_{bag_name}_.npy'),_depth_sequences)
                        if depth_copy_path:
                            np.save(os.path.join(depth_copy_path,f'{keypoint[0]}_{bag_name}_.npy'),_depth_sequences)
                        current_video_render.release()
                        current_video_render = None
                        #remove keypoint from depth_sequences
                        depth_sequences[keypoint] = None
                        #remove keypoint from timeline_pairs
                        #if end of timeline_pairs then stop
                        
                        if written_pairs >= len(timeline_pairs) - 1:
                            print('Done!')
                            stop = True
                        written_pairs += 1
                        break
                    elif current_video_render:
                        print(f'Writing frame {current_frame} to {keypoint} DU: {int((end_stamp - start_stamp) /1000 * 60)}f LOC: {current_frame_timestamp - start_stamp} {current_frame_timestamp - end_stamp}...')
                        depth_sequences[keypoint][current_frame - d_c_fr] = depth_image
                        #wrtie video
                        color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
                        current_video_render.write(color_image)
                            
            if stop:
                return

                
            current_frame += 1
        except Exception as e:
            print(e)
            break
def get_timeline_array(timeline_file):
    #read a file txt, sample 1 line: 82,capture,1704616757716.6748 get only 82
    timeline_array = []
    timestamp_array = []
    with open(timeline_file,'r') as f:
        for line in f.readlines():
            timeline_array.append(int(line.split(',')[0]))
            timestamp_array.append(float(line.split(',')[2].replace('\n','')))
    return timeline_array,timestamp_array

def process_folder(input_dir,output_dir,depth_copy_path):
    #find bag and txt file in folder F:\RealsenseCapture\output\A17P2
    timeline_array,timestamp_array = get_timeline_array(os.path.join(input_dir,'timeline.txt'))
    bag_files = [os.path.join(input_dir,file) for file in os.listdir(input_dir) if file.endswith('.bag')]
    for bag_file in bag_files:
        process_bag(bag_file,output_dir,timeline_array,timestamp_array,depth_copy_path)
def main():
    #find bag and txt file in folder F:\RealsenseCapture\output\A17P2
    output_dir = r'E:\OutputSplitAbsoluteVer2'
    batch_input_dir = r"E:\RealsenseData"
    depth_copy_path = r"E:\DepthAbsolute"
    os.makedirs(depth_copy_path,exist_ok=True)
    #tqdm on all folder in batch_input_dir
    for input_dir in tqdm(os.listdir(batch_input_dir)):
        input_dir = os.path.join(batch_input_dir,input_dir)
        process_folder(input_dir,output_dir,depth_copy_path)

if __name__ == '__main__':
    main()

            