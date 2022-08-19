import os
import glob
import time

# 최상위폴더 경로
root_path = r'D:\data_48\20220818_02_track'
clips_path = glob.glob(os.path.join(root_path, '*', '*'))

for clip in clips_path:
    start = time.time()
    clip_num = os.path.basename(clip).replace('Clip_', '')
    
    # calib 체크
    lc_cal_dist = os.path.join(clip, 'calib', 'Lidar_camera_calib',
                               f'481_ND_{clip_num}_LCC_CF.txt')
    lr_cal_dist = os.path.join(clip, 'Calib', 'Lidar_radar_calib', 
                               f'481_ND_{clip_num}_LRC_RF.txt')
    
    # 카메라, 라이다, 레이다 체크
    camera_dist = [os.path.join(clip, 'Camera', 'CameraFront', 'blur',
                                f'481_ND_{clip_num}_CF_{str(i):0>3s}.png')
                   for i in range(1, 101)]
    lidar_dist = [os.path.join(clip, 'Lidar',
                               f'481_ND_{clip_num}_LR_{str(i):0>3s}.pcd')
                  for i in range(1, 101)]
    radar_dist = [os.path.join(clip, 'Radar', 'RadarFront',
                               f'481_ND_{clip_num}_RF_{str(i):0>3s}.pcd')
                  for i in range(1, 101)]
    
    lc_cal = os.path.exists(lc_cal_dist)
    lr_cal = os.path.exists(lr_cal_dist)
    
    c = [os.path.exists(cam) for cam in camera_dist]
    l = [os.path.exists(lid) for lid in lidar_dist]
    r = [os.path.exists(rad) for rad in radar_dist]
    
    end = time.time()
    elapsed = end - start
    
    print(f'{clip} : {lc_cal} {lr_cal} {all(c)} {all(l)} {all(r)} [{elapsed:.4f} s]')

print(f'dir : lidar_camera cal / lidar_radar cal / cam / lidar / radar')
print(f'all clips checked')