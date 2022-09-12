import glob, json, os, copy, shutil

class AnalyzeLabel():
    
    def __init__(self, clip_path = None, extract_path = None) -> None:
        '''
        부모 클래스 변수
        - self.clipPath: str - 클립 경로
        - self.resultPath: str - 레이블 폴더 경로
        - self.backupfolder: str - 백업 폴더 경로
        - self.resultList: list - json 파일 경로 리스트
        - self.resultNum: int - json 파일 수
        - self.clipName: str - 클립 이름
        '''
        # self.clipName: S_Clip_00000_01 ~ 17 or A_Clip_00000_01 ~ 17
        
        self.clip_path = clip_path
        self.extract_path = extract_path
        self.clipPath_list = None
    
    # 파일명 일괄수정
    def fix_filenames(self, clip_path = None):
        clip_path = clip_path.replace('\\', '/')
        if clip_path:
            clip_listdir = os.listdir(clip_path)
        else:
            clip_listdir = os.listdir(self.clip_path)
        sensor_abb_dic = {'CameraFront': 'CF', 'CameraLeft': 'CL', 'CameraBack': 'CB', 'CameraRight':'CR',
                        'FrontCenter':'CF', 'RadarFront': 'RF', 'RadarFrontLeft': 'RFL', 'RadarFrontRight': 'RFR',
                        'RadarBackLeft': 'RBL', 'RadarBackRight': 'RBR', 'GNSS_INS': 'GI', 
                        'CameraRear': 'CR', 'Lidar_camera_calib': 'LCC', 'Lidar_radar_calib': 'LRC',
                        'Radar_camera_calib': 'RCC', 'result':'CF',
                        'result_backup':'CF', 'Lidar': 'LR'}
        depth3_folders = ['lidar', 'gnss_ins', 'result'] # 추후에 result도 camera 파일명 정보대로 변경 기능 추가
        depth4_folders = ['radar', 'calib']
        depth5_folders = ['camera']
        
        # depth2, depth3, depth4, depth5 폴더 이름
        
        for d2_folder in clip_listdir:
            # pass calibration folder
            # if d2_folder.lower() == 'calib':
            #     continue
            
            # 1. fix depth3 files (lidar, gnss_ins, result)
            if d2_folder.lower() in depth3_folders:
                depth3_path = clip_path + '/' + d2_folder # depth3 폴더 경로
                sensor_abb = sensor_abb_dic[d2_folder] # depth3 경로 약자
                self.rename_files(depth3_path, sensor_abb) # depth3 폴더 경로에서 파일명 일괄 변경
                continue
            
            # 2. fix depth4 files (radar, calib)
            if d2_folder.lower() in depth4_folders: 
                depth3_path = clip_path + '/' + d2_folder
                depth4_list = os.listdir(depth3_path)
                for d3_folder in depth4_list:
                    if d3_folder == 'FrontCamera': # 예전 Camera 하위폴더
                        d3_folder = 'CameraFront'
                    elif d3_folder == 'Radar_Center': # 예전 Radar 하위폴더
                        d3_folder = 'RadarFront'
                    sensor_abb = sensor_abb_dic[d3_folder]
                    depth4_path = depth3_path + '/' + d3_folder
                    self.rename_files(depth4_path, sensor_abb)
                continue

            # 3. fix depth5 files (camera)
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

        is_calib = False
        clip_num = int(path.split('Clip_')[-1].split('_')[0].split('/')[0]) # 00000 ~ 99999 클립 고유번호 추출
        if sensor_abb == 'LCC' or sensor_abb == 'LRC' or sensor_abb == 'RCC': # calib 폴더인 경우
            is_calib = True
        
        
        # for unit in clip_name.split('_'):
        #     if unit.isdigit():
        #         clip_num = int(unit)
        #         break
        
        file_list = glob.glob(path + '/*')
        for file in file_list:
            file_name = os.path.basename(file)
            
            if file_name[:3] == 'cam' or file_name[:4] == '2-048':
                continue

            if is_calib:
                pass
            elif file_name[:5] == 'event':
                file_num = 1
            else:
                file_num = int(file_name.split('_')[-1].split('.')[0])
            file_extension = file.split('.')[-1]

            # 특수한 상황. 추후 정리
            if file_name[:4].isdigit() or \
                file_name[:5] == 'event' or \
                file_name[:3] == '481':
                spetical_case = True
            
            if is_calib:
                # change '481_ND' to '2-048' in file
                renamed_file = path + '/'+ file_name.replace('481_ND', '2-048')
                is_file_renamed = self.rename_and_print(file, renamed_file)
            else:
                renamed_file = path + '/'+ '2-048_' + f'{clip_num:05d}' + '_' + sensor_abb+ f'_{file_num:03d}.' + file_extension
                is_file_renamed = self.rename_and_print(file, renamed_file)
            # else:
            #     renamed_file = '_'.join(file.split('_')[:-1]) + f'_{file_num:03d}' + '.' + file_extension
            #     is_file_renamed = self.renameAndPrint(file, renamed_file)
        return True

    def rename_and_print(self, file, renamed_file):
        os.renames(file, renamed_file)
        print(file, '->', renamed_file)
        return True
            
# tester = AnalyzeLabel('C:\datasets\extract_2022-08-02-18-18-53\Clip_00034_test')
# tester.fix_filenames()