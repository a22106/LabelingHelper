import glob, json, os, copy, shutil
from editLabel import EditLabel

class AnalyzeLabel(EditLabel):
    
    def __init__(self, clipPath) -> None:
        super().__init__(clipPath)
        '''
        부모 클래스 변수
        - self.filepath: str - 클립 경로
        - self.backupfolder: str - 백업 폴더 경로
        - self.json_list: list - json 파일 리스트(result)
        - self.json_file_num: int - json 파일 수
        
        현재 클래스의 변수
        - self.clip_path: str - 클립 경로
        - self.clip_name: str - 클립 이름
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
    
    # 파일명 일괄수정
    def fix_filenames(self, clip_path = None):
        clip_path = clip_path.replace('\\', '/')
        if clip_path:
            clip_listdir = os.listdir(clip_path)
        else:
            clip_listdir = os.listdir(self.clip_path)
        sensor_abb_dic = {'CameraFront': 'CF', 'Lidar': 'LR', 'RadarFront': 'RF', 
                      'GNSS_INS': 'GI', 'CameraRear': 'CR', 'Lidar_camera_calib': 'LCC',
                      'Lidar_radar_calib': 'LRC', 'Radar_camera_calib': 'RCC'}
        depth3_folders = ['lidar', 'gnss_ins'] # 추후에 result도 camera 파일명 정보대로 변경 기능 추가
        depth4_folders = ['radar', 'calib']
        depth5_folders = ['camera']

        
        
        # depth2, depth3, depth4, depth5 폴더 이름
        
        for d2_folder in clip_listdir:
            # pass calibration folder
            # if d2_folder.lower() == 'calib':
            #     continue
            
            # 1. fix depth3 files
            if d2_folder.lower() in depth3_folders:
                depth3_path = clip_path + '/' + d2_folder
                sensor_abb = sensor_abb_dic[d2_folder]
                # fix depth2 path
                self.rename_files(depth3_path, sensor_abb)
                continue
            
            # 2. fix depth4 files
            if d2_folder.lower() in depth4_folders: 
                depth3_path = clip_path + '/' + d2_folder
                depth4_list = os.listdir(depth3_path)
                for d3_folder in depth4_list:
                    if d3_folder == 'FrontCamera':
                        d3_folder = 'CameraFront'
                    elif d3_folder == 'Radar_Center':
                        d3_folder = 'RadarFront'
                    sensor_abb = sensor_abb_dic[d3_folder]
                    depth4_path = depth3_path + '/' + d3_folder
                    self.rename_files(depth4_path, sensor_abb)
                continue
                
            # 3. fix depth5 files
            if d2_folder.lower() in depth5_folders:
                depth3_path = clip_path + '/' + d2_folder
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
        return True
            
                
    def rename_files(self, path, sensor_abb):
        # 파일명에 고려해야할 것
        # 과제번호_클립번호_센서_프레임.확장자

        spetical_case = False
        is_calib = False
        clip_num = int(path.split('Clip_')[-1].split('_')[0])
        if sensor_abb == 'LCC' or sensor_abb == 'LRC' or sensor_abb == 'RCC':
            is_calib = True
        
        
        # for unit in clip_name.split('_'):
        #     if unit.isdigit():
        #         clip_num = int(unit)
        #         break
        
        file_list = glob.glob(path + '/*')
        for file in file_list:
            is_file_renamed = False
            file_name = file.split('\\')[-1]
            if file_name[:3] == 'cam':
                continue

            if is_calib:
                pass
            elif sensor_abb =='GI':
                file_num = int(file[-5])
            else:
                file_num = int(file_name.split('_')[-1].split('.')[0])
            file_extension = file.split('.')[-1]

            # 특수한 상황. 추후 정리
            if file_name[:4].isdigit() or \
                file_name[:5] == 'event' or \
                file_name[:3] == '481':
                spetical_case = True
            
            # if first 4 string is a intiger
            
            if is_calib:
                # change '481_ND' to '2-048' in file
                renamed_file = path + '/'+ file_name.replace('481_ND', '2-048')
                is_file_renamed = self.renameAndPrint(file, renamed_file)
            else:
                renamed_file = path + '/'+ '2-048_' + f'{clip_num:05d}' + '_' + sensor_abb+ f'_{file_num:03d}.' + file_extension
                is_file_renamed = self.renameAndPrint(file, renamed_file)
            # else:
            #     renamed_file = '_'.join(file.split('_')[:-1]) + f'_{file_num:03d}' + '.' + file_extension
            #     is_file_renamed = self.renameAndPrint(file, renamed_file)
        return True

    def renameAndPrint(self, file, renamed_file):
        os.renames(file, renamed_file)
        print(file, '->', renamed_file)
        return True
            
# tester = AnalyzeLabel('C:\datasets\extract_2022-08-02-18-18-53\Clip_00034_test')
# tester.fix_filenames()