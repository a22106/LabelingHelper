import glob, json, os, copy, shutil, math


class EditLabel():
    def __init__(self, input_path:str):
        input_path = input_path.replace('\\', '/')
        self.set_path(input_path)
        

    def __len__(self):
        return len(self.result_list)

    def __getitem__(self, index):
        try:
            with open(self.result_list[index], 'r') as f:
                json_data = json.load(f)
        except Exception as e:
            print(e)
            exceptmessage = f'{self.result_list[index]}의 json 파일을 읽을 수 없습니다.'
            print(exceptmessage)
            return exceptmessage
        return json_data

    def set_path(self, path):
        '''
        클래스 변수
        - self.clipPath: str - 클립 경로
        - self.resultPath: str - 레이블 폴더 경로
        - self.backupfolder: str - 백업 폴더 경로
        - self.resultList: list - json 파일 경로 리스트
        - self.resultNum: int - json 파일 수
        - self.clipName: str - 클립 이름
        '''
        # self.clipName: S_Clip_00000_01 ~ 17 or A_Clip_00000_01 ~ 17
        basename_units = os.path.basename(path).split('_')
        basename_units = [x.lower() for x in basename_units]
        if 'clip' not in basename_units:
            raise Exception('클립 폴더가 아닙니다.')
        path = path.replace('\\', '/')
        self.clip_path = path
        self.clip_name = path.split('/')[-1]
        self.result_path = path + '/result'
        
        if os.path.isdir(self.result_path):
            self.result_list = glob.glob(self.result_path + '/*.json')
            self.result_list.sort()
            self.result_num = len(self.result_list)
            
        self.backupfolder = path + '/result_backup'
    
    def get_result_list(self):
        return self.result_list

    def show_json(self, frame):
        with open(self.result_list[frame], 'r') as f:
            json_data = json.load(f)
        print("Show json info")
        return json_data
    

    # check object id
    def check_object_id(self, id) -> list:
        frame_is_id = []
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f)
                
            for annot in json_data['annotation']:
                if int(annot['id']) == int(id):
                    print(f'프레임 {idx+1}에 객체 번호 {id}가 있습니다.')
                    frame_is_id.append(idx+1)

        if not frame_is_id:
            print(f'어느 프레임에도 객체 번호 {id}(이)가 없습니다.')
            print("----------------------------------------------------")

        return frame_is_id
    
    # change dimension
    def change_dim(self, id, width, height, length):
        dim = [width, height, length] # 변경할 크기
        frames = []
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            for annot in json_data['annotation']:
                if int(annot['id']) == id:
                    for dim_idx, dim_value in enumerate(dim):
                        if dim_value:
                            annot['3d_box'][0]['dimension'][dim_idx] = dim_value
                    print(f"프레임 {json_data['frame_no']}: {id}의 박스 크기를 {annot['3d_box'][0]['dimension']}로 변경")
                    frames.append(json_data['frame_no'])
                    with open(self.result_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                    continue
        return annot['3d_box'][0]['dimension'], frames

    # change id
    def change_id(self, id, new_id):
        frames = []
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            for annot in json_data['annotation']:
                if annot['id'] == f'{id}' or annot['id'] == id:
                    annot['id'] = new_id
                    print(f'프레임 {json_data["frame_no"]}: {id}의 id를 {new_id}로 변경')
                    frames.append(json_data['frame_no'])
                    with open(self.result_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")    
        return frames

    # change Angle
    def change_angle(self, id, angle):
        r'''
        id: int - 객체 번호
        angle: float 객체 회전 각도 (degree, 12시 방향 0도)
        return: list - 회전 각도가 변경된 프레임 번호
        '''
        frames = []
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            
            # change degree to radian
            angle_rad = math.radians(angle)

            for annot in json_data['annotation']:
                if int(annot['id']) == id:
                    former_angle = math.degrees(annot['3d_box'][0]['rotation_y'])
                    annot['3d_box'][0]['rotation_y'] = angle_rad
                    print(f'프레임 {json_data["frame_no"]}: {id}의 각도 변경 {former_angle} -> {angle}')
                    frames.append(json_data['frame_no'])
                    with open(self.result_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")
        return frames, former_angle
    
    # chnage angle 180
    def change_angle180(self, id):
        frames = []
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            
            for annot in json_data['annotation']:
                if int(annot['id']) == id:
                    cur_angle = annot['3d_box'][0]['rotation_y']
                    changed_angle = (cur_angle + math.pi) % (2 * math.pi)
                    annot['3d_box'][0]['rotation_y'] = changed_angle
                    print(f'프레임 {json_data["frame_no"]}: {id}의 각도를 180˚ 회전 {math.degrees(cur_angle)}-> {math.degrees(changed_angle)}')
                    frames.append(json_data['frame_no'])
                    with open(self.result_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
        return frames, math.degrees(cur_angle), math.degrees(changed_angle)
                            
    # change category
    def change_category(self, id, obj_type, category: str):
        r'''
        id: int - 객체 번호
        obj_type: object type
        category: object category
        return: frames
        '''
        frames = []
        atypical_cat = ['MEDIAN_STRIP', 'SOUND_BARRIER', 'OVERPASS', 'RAMP_SECT', 'TUNNEL']
    
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
                
            for annot in json_data['annotation']:
                if int(annot['id']) == id and annot['category'] != category:
                    annot['obj_type'] = obj_type
                    annot['category'] = category
                    if category in atypical_cat:
                        annot['atypical_yn'] = "y"
                    else:
                        annot['atypical_yn'] = "n"
                    
                    print(f'프레임 {json_data["frame_no"]}: {id}의 카테고리를 {category}로 변경')
                    frames.append(json_data['frame_no'])
                    with open(self.result_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')    
        print("----------------------------------------------------")
        return frames

    # change bugged object id
    def change_bugged_id(self, max_id):
        # change bugged id that is bigger than max_id and end with series of 1
        # for example if max_id is 30, chage 5111 to 5, 101 to 10, 111 to 11, 2111 to 21, 3111 to 3, 4111 to 4, 1011 to 10
        # if max_id is 100, change 5111 to 51, 101 to 10, 111 to 11, 2111 to 21, 3111 to 3, 4111 to 4, 1011 to 10
        # all buged numbers end with series of 1
        changed_num_count = 0
        for idx in range(self.result_num):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            max_id = str(max_id) # 변경할 크기

            for annot in json_data['annotation']:
                if int(annot['id']) > int(max_id):
                    for i in range(len(annot['id'])):
                        if annot['id'][i] == '1' and int(annot['id'][:i+1]) > int(max_id):
                            
                            annot['id'] = annot['id'][:i]
                            print(f'프레임 {json_data["frame_no"]}: {annot["id"]}의 id를 {annot["id"][:i]}로 변경')
                            with open(self.result_list[idx], 'w') as f:
                                json.dump(json_data, f, indent=4)
                                changed_num_count += 1
                            break
                        
                        elif annot['id'][i] == '1' and len(annot['id'][:i]) >= len(max_id):
                            annot['id'] = annot['id'][:i]
                            print(f'프레임 {json_data["frame_no"]}: {annot["id"]}의 id를 {annot["id"][:i]}로 변경')
                            with open(self.result_list[idx], 'w') as f:
                                json.dump(json_data, f, indent=4)
                                changed_num_count += 1
                            break
                else:
                    continue
        print(f'{changed_num_count}개의 id를 변경했습니다.')
        return changed_num_count
    
    # copy objects
    def copy_object(self, obj_id, frame, start=1, end=100, CHANGE=False):
        obj_id, start, end = int(obj_id), int(start), int(end)
        frames_copy = []
        frames_paste = []
        
        with open(self.result_list[frame-1], 'r') as f:
            json_data = json.load(f) # 목표 프레임의 json 데이터 불러옴
        for annot1 in json_data['annotation']:
            if int(annot1['id']) == obj_id:
                copy_annot = annot1
                print(copy_annot)
        
        # 입력한 시작 프레임부터 종료 프레임까지 복사
        for idx in range(start-1, end):
            if idx+1 == frame:
                continue

            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            # 해당 프레임에 아무 객체 정보가 없다면 바로 객체 복사
            if not json_data['annotation']:
                json_data['annotation'].append(copy_annot)
                with open(self.result_list[idx], 'w') as f:
                    json.dump(json_data, f, indent=4)
                print(f'프레임 {json_data["frame_no"]}: 객체 {obj_id}의 오브젝트를 복사.')
                frames_copy.append(json_data['frame_no'])
                continue
            
            obj_num = len(json_data['annotation']) # 해당 프레임에 있는 객체 수
            obj_count = 0
            for annot2 in json_data['annotation']:
                obj_count+=1
                if int(annot2['id']) == obj_id:
                    if CHANGE: # 붙여넣기 옵션이 켜져있다면 기존 객체의 값을 덮어쓰기
                        annot2 = self.copy_annotation(annot2, copy_annot)
                        print(f'프레임 {json_data["frame_no"]}: 객체 {obj_id}의 오브젝트를 붙여넣기')
                        frames_paste.append(json_data['frame_no'])
                        break

                    else: # 붙여넣기 옵션이 꺼져있다면 지나가기
                        print(f'프레임 {json_data["frame_no"]}: 객체 {obj_id}의 오브젝트를 지나감')
                        break
                
                # if for문이 마지막에 도달했다면 객체 복사
                
                else: # 객체 id가 다르면 객체 복사
                    if obj_num == obj_count:
                        json_data['annotation'].append(copy_annot)
                        print(f'프레임 {json_data["frame_no"]}: 객체 {obj_id}의 오브젝트를 복사..')
                        frames_copy.append(json_data['frame_no'])
                        break
            
            with open(self.result_list[idx], 'w') as f:
                json.dump(json_data, f, indent=4)
        print("----------------------------------------------------")
        return frames_copy, frames_paste

    def copy_annotation(self, annot, copy_annot):
        for key in copy_annot.keys():
            annot[key] = copy_annot[key]
        return annot

    # delete objects
    def remove_obj(self, obj: dict):
        frames_delete = []
        if obj['id'] <=0:
            print('id는 0보다 커야합니다.')
            return frames_delete
        obj_id, start, end = obj['id'], obj['startFrame'], obj['endFrame']
        
        for idx in range(start-1, end):
            with open(self.result_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            
            if not json_data['annotation']:
                continue
            
            for annot2 in json_data['annotation']:
                if int(annot2['id']) == obj_id:
                    try:
                        json_data['annotation'].remove(annot2)
                    except:
                        print(f'프레임 {json_data["frame_no"]}: 객체 {obj_id}가 이미 삭제되었습니다.')
                        continue
                    print(f'프레임 {json_data["frame_no"]}: 객체 {obj_id}의 오브젝트를 삭제.')
                    frames_delete.append(json_data['frame_no'])
                    break
                
            with open(self.result_list[idx], 'w') as f:
                json.dump(json_data, f, indent=4)
        print("----------------------------------------------------")
        return frames_delete


    # make backup file
    def make_backup(self):
        copied_file_count = 0
        backup_file_list = []
        try:
            if not os.path.exists(self.backupfolder):
                os.mkdir(self.backupfolder)
        except OSError:
            print('Error: Creating directory of backup')
            exit()

        for idx in range(self.result_num):
            shutil.copy(self.result_list[idx], self.backupfolder)
            print(f'{self.result_list[idx]}을 백업파일로 만들었습니다.')
            backup_file_list.append(self.backupfolder+self.result_list[idx].split('/')[-1])
            copied_file_count += 1

        if copied_file_count == 0:
            print('백업파일을 만들 수 없습니다.')
            return 0
        else:
            print('{}개 파일 백업 완료'.format(copied_file_count))
            print("----------------------------------------------------")    
            return copied_file_count, backup_file_list

    # restore backup file
    def restore_backup(self) -> int:
        backup_files = glob.glob(self.backupfolder + '/*.json')
        copied_file_count = 0
        cur_files_list = []
        try:
            if not os.path.exists(self.backupfolder):
                print('백업파일이 없습니다.')
                return False
        # if backup folder is not exist
        except OSError:
            print('Error: backup folder is not exist')
            return False
        try:
            if not os.path.exists(self.result_path):
                os.mkdir(self.result_path)
        except OSError:
            print('Error: Creating directory of backup')
            exit()
            
        for file in backup_files:
            #shutil.copy(self.backupfolder + '/' + self.json_list[idx].split('\\')[-1], self.json_list[idx])
            shutil.copy(file, self.result_path)
            cur_files_list.append(self.result_path + '/' + file.split('\\')[-1])
            print(f'{file}을 백업파일로 복원했습니다.')
            copied_file_count += 1
        self.set_path(self.clip_path)
        
        if copied_file_count == 0:
            print('백업파일이 없습니다.')
            return 0
        else:
            print('{}개 파일 복원 완료'.format(copied_file_count))
            print("----------------------------------------------------")    
            return copied_file_count, cur_files_list