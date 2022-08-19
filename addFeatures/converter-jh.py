import os
import glob
import time

# 클립상위폴더 경로
# root_path = r'D:\data_48\20220818_02_track\extract_2022-08-03-15-44-05'
clips_path = glob.glob(os.path.join(root_path, '*'))

for clip in clips_path:
    start = time.time()
    clip_num = os.path.basename(clip).replace('Clip_', '')

    # 기존 calib 파일
    lc_cal = os.path.join(clip, 'Calib', 'Lidar_camera_calib', 'cam0.txt')
    lr_cal = os.path.join(clip, 'Calib', 'Lidar_radar_calib', 'srs_front_center.txt')

    # 변경된 calib 파일명
    lc_cal_dist = os.path.join(clip, 'Calib', 'Lidar_camera_calib', f'481_ND_{clip_num}_LCC_CF.txt')
    lr_cal_dist = os.path.join(clip, 'Calib', 'Lidar_radar_calib', f'481_ND_{clip_num}_LRC_RF.txt')

    # calib 파일명 변경
    os.rename(lc_cal, lc_cal_dist)
    os.rename(lr_cal, lr_cal_dist)

    # Calib 폴더명 calib으로 변경(소문자)
    os.rename(
        os.path.join(clip, 'Calib'),
        os.path.join(clip, 'calib')
    )

    # 기존 카메라, 라이다, 레이다 파일 리스트
    cameras = glob.glob(os.path.join(clip, 'Camera', 'FrontCenter', 'blur', '*.png'))
    lidars = glob.glob(os.path.join(clip, 'Lidar', '*.pcd'))
    radars = glob.glob(os.path.join(clip, 'Radar', 'Radar_Center', '*.pcd'))

    # 변경된 카메라, 라이다, 레이다 파일명 리스트
    cameras_dist = [os.path.join(clip, 'Camera', 'FrontCenter', 'blur', f'481_ND_{clip_num}_CF_{os.path.basename(i)[1:]}') for i in cameras]
    lidars_dist = [os.path.join(clip, 'Lidar', f'481_ND_{clip_num}_LR_{os.path.basename(i)[1:]}') for i in lidars]
    radars_dist = [os.path.join(clip, 'Radar', 'Radar_Center', f'481_ND_{clip_num}_RF_{os.path.basename(i)[1:]}') for i in radars]

    # 카메라, 라이다, 레이다 파일명 변경
    for c, c_d in zip(cameras, cameras_dist):
        os.rename(c, c_d)
    
    for l, l_d in zip(lidars, lidars_dist):
        os.rename(l, l_d)
    
    for r, r_d in zip(radars, radars_dist):
        os.rename(r, r_d)
    
    # 카메라, 레이다 폴더명 변경
    os.rename(
        os.path.join(clip, 'Camera', 'FrontCenter'),
        os.path.join(clip, 'Camera', 'CameraFront')
    )
    os.rename(
        os.path.join(clip, 'Radar', 'Radar_Center'),
        os.path.join(clip, 'Radar', 'RadarFront')
    )

    end = time.time()
    elapsed = end - start
    
    print(f'clip_{clip_num} converted [{elapsed:.4f} s]')

print('all converted')