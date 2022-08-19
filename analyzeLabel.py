import glob, json, os, copy, shutil
from editLabel import EditLabel

class AnalyzeLabel(EditLabel):
    
    def __init__(self, clipPath) -> None:
        super().__init__(clipPath)
        '''
        부모 클래스 변수
        - self.filepath
        - self.backupfolder
        - self.json_list
        - self.json_file_num
        
        현재 클래스의 변수
        - self.clip_path
        - self.clip_name
        '''
        # clip_name: S_Clip_00000_01 ~ 17 or A_Clip_00000_01 ~ 17
        self.clip_path, self.clip_name = self.set_path(clipPath)        
        
    def set_path(self, clipPath):
        clipPath = clipPath.replace('\\', '/')
        lastfoler = clipPath.split('/')[-1]
        
        if lastfoler == 'result':
            clipPath = clipPath.replace(lastfoler, '')[:-1]
            clipname = clipPath.split('/')[-1]
        elif lastfoler[1:5] == '_Clip' or lastfoler[0:5] == 'Clip_':
            clipname = clipPath.split('/')[-1]
        else:
            print('잘못된 경로입니다.')
            return False
        return clipPath, clipname
    
    def fix_filenames(self):
        clip_listdir = os.listdir(self.clip_path)
        sensor_abb_dic = {'CameraFront': 'CF', 'Lidar': 'LR', 'RadarFront': 'RF', 
                      'GNSS_INS': 'GI', 'CameraRear': 'CR', 'Lidar_camera_calib': 'LCC',
                      'Lidar_radar_calb': 'LRC', 'Radar_camera_calib': 'RCC', 'FrontCenter': 'CF',
                      'Radar_Center': 'RF'}
        depth3_folders = ['Lidar', 'GNSS_INS']
        depth4_folders = ['Radar', 'Calib']
        depth5_folders = ['Camera']
        
        
        # depth2, depth3, depth4, depth5 폴더 이름
        
        for d2_folder in clip_listdir:
            # pass calibration folder
            if d2_folder.lower() == 'calib':
                continue
            
            # 1. fix depth3 files
            if d2_folder in depth3_folders:
                depth3_path = self.clip_path + '/' + d2_folder
                sensor_abb = sensor_abb_dic[d2_folder]
                # fix depth2 path
                self.rename_files(depth3_path, sensor_abb)
                continue
            
            # 2. fix depth4 files
            if d2_folder in depth4_folders: 
                depth3_path = self.clip_path + '/' + d2_folder
                depth4_list = os.listdir(depth3_path)
                for d3_folder in depth4_list:
                    sensor_abb = sensor_abb_dic[d3_folder]
                    depth4_path = depth3_path + '/' + d3_folder
                    self.rename_files(depth4_path, sensor_abb)
                continue
                
            # 3. fix depth5 files
            if d2_folder in depth5_folders:
                depth3_path = self.clip_path + '/' + d2_folder
                depth4_list = os.listdir(depth3_path)
                for d3_folder in depth4_list:
                    if d2_folder.lower() == 'camera':
                        sensor_abb = sensor_abb_dic[d3_folder]
                    depth4_path = depth3_path + '/' + d3_folder
                    depth5_list = os.listdir(depth4_path)
                    for d4_folder in depth5_list:
                        if d2_folder.lower() != 'camera':
                            sensor_abb = sensor_abb_dic[d4_folder]
                        depth5_path = depth4_path + '/' + d4_folder
                        self.rename_files(depth5_path, sensor_abb)
            
                
    def rename_files(self, path, sensor_abb):
        # 파일명에 고려해야할 것
        # 과제번호_클립번호_센서_프레임.확장자
        
        
        for unit in self.clip_name.split('_'):
            if unit.isdigit():
                clip_num = int(unit)
                break
        
        file_list = glob.glob(path + '/*')
        for file in file_list:
            if sensor_abb =='GI':
                file_num = int(file[-5])
            else:
                file_num = int(file.split('\\')[-1].split('_')[-1].split('.')[0])
            file_extension = file.split('.')[-1]
            
            # if first 4 string is a intiger
            if file.split('\\')[-1][:4].isdigit() or file.split('\\')[-1][:5] == 'event': # GNSS_INS 의 구 파일이 event1.txt로 명명된 경우 포함
                renamed_file = path + '/2-048_' + f'{clip_num:05d}' + '_' + sensor_abb+ f'_{file_num:03d}.' + file_extension
                os.renames(file, renamed_file)
                print(file, '->', renamed_file)
            else:
                renamed_file = '_'.join(file.split('_')[:-1]) + '_{:03d}'.format(file_num) + '.' + file_extension
                os.renames(file, renamed_file)
                print(file, '->', renamed_file)
            
tester = AnalyzeLabel('C:\datasets\extract_2022-08-02-18-18-53\Clip_00034_test')
tester.fix_filenames()