import glob, json, os, copy, shutil


class EditLabel():
    def __init__(self, filepath:str = None):
        filepath = filepath.replace('\\', '/')
        self.filepath = filepath
        self.set_json_list(filepath)
        self.backupfolder = '/'.join(self.filepath.split('/')[:-1]) + '/result_backup'

    def __len__(self):
        return len(self.json_list)

    def __getitem__(self, index):
        return self.json_list[index]

    def showJson(self, frame):
        with open(self.json_list[frame], 'r') as f:
            json_data = json.load(f)
        print("Show json info")
        return json_data
    
    def set_json_list(self, filePath): 
        # if file Path is list
        if isinstance(filePath, list):
            self.json_list = filePath
        elif filePath.split('/')[-1] != 'result':
            self.json_list = glob.glob(filePath + 'result/*.json')
        else:
            self.json_list = glob.glob(filePath + '/*.json')
        self.json_list.sort()
        self.json_file_num = len(self.json_list)
        return self.json_list, self.json_file_num

    # check object id
    def checkObjectId(self, id, maxId = None) -> list:
        frame_is_Id = []
        for idx in range(self.json_file_num):
            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f)
                
            for annot in json_data['annotation']:
                if int(annot['id']) == int(id):
                    print(f'프레임 {idx+1}에 객체 번호 {id}가 있습니다.')
                    frame_is_Id.append(idx+1)

                # if maxId:
                #     if int(annot['id']) > maxId:
                #         print(f'frame {idx+1}: {annot["id"]}가 최대 id보다 큼')
        
        if not frame_is_Id:
            print(f'어느 프레임에도 객체 번호 {id}(이)가 없습니다.')
            print("----------------------------------------------------")

        return frame_is_Id
    
    # change dimension
    def changeDim(self, id, width, height, length):
        dim = [float(width), float(height), float(length)] # 변경할 크기
        with open(self.json_list[0], 'r') as f:
            temp_data = json.load(f)
        for idx in range(len(dim)):
            if dim[idx] == 0:
                dim[idx] = temp_data['annotation'][0]['3d_box'][0]['dimension'][idx]
        
        for idx in range(self.json_file_num):
            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            ori_dim = copy.deepcopy(dim) # 원래 크기 복사

            for annot in json_data['annotation']:
                if int(annot['id']) == int(id):
                    annot['3d_box'][0]['dimension'] = dim # 변경
                    print(f'프레임 {json_data["frame_no"]}: {id}의 크기를 {dim[0]}, {dim[1]}, {dim[2]}로 변경')
                    with open(self.json_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                    dim = ori_dim # 원래 크기로 변경
                    #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")
        return dim

    # change id
    def changeId(self, id, newId):
        for idx in range(self.json_file_num):
            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            for annot in json_data['annotation']:
                if annot['id'] == f'{id}' or annot['id'] == id:
                    annot['id'] = f'{newId}'
                    print(f'프레임 {json_data["frame_no"]}: {id}의 id를 {newId}로 변경')
                    with open(self.json_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")    

    # change angle
    def changeAngle(self, id, angle):
        for idx in range(self.json_file_num):
            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            angle = float(angle) # 변경할 크기
            # change degree to radian
            angle_rad = math.radians(angle)

            for annot in json_data['annotation']:
                if annot['id'] == f'{id}' or annot['id'] == id:
                    annot['3d_box'][0]['rotation_y'] = angle_rad
                    print(f'프레임 {json_data["frame_no"]}: {id}의 각도를 {angle}로 변경')
                    with open(self.json_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")
                            
    # change category
    def changeCategory(self, id, obj_type, category: str):
        atypical_cat = ['MEDIAN_STRIP', 'SOUND_BARRIER', 'OVERPASS', 'RAMP_SECT', 'TUNNEL']
    
        for idx in range(self.json_file_num):
            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
                id = int(id) 
                
            for annot in json_data['annotation']:
                if annot['id'] == id and annot['category'] != category:
                    annot['obj_type'] = obj_type
                    annot['category'] = category
                    if category in atypical_cat:
                        annot['atypical_yn'] = "y"
                    else:
                        annot['atypical_yn'] = "n"
                    
                    print(f'프레임 {json_data["frame_no"]}: {id}의 카테고리를 {category}로 변경')
                    with open(self.json_list[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')    
        print("----------------------------------------------------")

    # change bugged object id
    def changeBuggedId(self, max_id):
        # change bugged id that is bigger than max_id and end with series of 1
        # for example if max_id is 30, chage 5111 to 5, 101 to 10, 111 to 11, 2111 to 21, 3111 to 3, 4111 to 4, 1011 to 10
        # if max_id is 100, change 5111 to 51, 101 to 10, 111 to 11, 2111 to 21, 3111 to 3, 4111 to 4, 1011 to 10
        # all buged numbers end with series of 1
        changed_num_count = 0
        for idx in range(self.json_file_num):
            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            max_id = str(max_id) # 변경할 크기

            for annot in json_data['annotation']:
                if int(annot['id']) > int(max_id):
                    for i in range(len(annot['id'])):
                        if annot['id'][i] == '1' and int(annot['id'][:i+1]) > int(max_id):
                            
                            annot['id'] = annot['id'][:i]
                            print(f'프레임 {json_data["frame_no"]}: {annot["id"]}의 id를 {annot["id"][:i]}로 변경')
                            with open(self.json_list[idx], 'w') as f:
                                json.dump(json_data, f, indent=4)
                                changed_num_count += 1
                            break
                        
                        elif annot['id'][i] == '1' and len(annot['id'][:i]) >= len(max_id):
                            annot['id'] = annot['id'][:i]
                            print(f'프레임 {json_data["frame_no"]}: {annot["id"]}의 id를 {annot["id"][:i]}로 변경')
                            
                            with open(self.json_list[idx], 'w') as f:
                                json.dump(json_data, f, indent=4)
                                changed_num_count += 1
                            break
                        
                else:
                    continue

        print(f'{changed_num_count}개의 id를 변경했습니다.')
        return changed_num_count
    
    # copy objects
    def copyObject(self, id, frame, start=1, end=100, CHANGE=False):
        id, start, end = int(id), int(start), int(end) # 변경할 크기
        
        with open(self.json_list[frame-1], 'r') as f:
            json_data = json.load(f) # 목표 프레임의 json 데이터 불러옴
        for annot1 in json_data['annotation']:
            if int(annot1['id']) == id:
                copy_annot = annot1
                print(copy_annot)
        
        # 입력한 시작 프레임부터 종료 프레임까지 복사
        for idx in range(start-1, end):
            if idx+1 == frame:
                continue

            with open(self.json_list[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            # 해당 프레임에 아무 객체 정보가 없다면 바로 객체 복사
            if not json_data['annotation']:
                json_data['annotation'].append(copy_annot)
                with open(self.json_list[idx], 'w') as f:
                    json.dump(json_data, f, indent=4)
                print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 복사.')
                continue
            
            obj_num = len(json_data['annotation']) # 해당 프레임에 있는 객체 수
            obj_count = 0
            for annot2 in json_data['annotation']:
                obj_count+=1
                if int(annot2['id']) == id:
                    if CHANGE: # 붙여넣기 옵션이 켜져있다면 기존 객체의 값을 덮어쓰기
                        annot2 = self.copy_annotation(annot2, copy_annot)
                        print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 붙여넣기')
                        break

                    else: # 붙여넣기 옵션이 꺼져있다면 지나가기
                        print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 지나감')
                        break
                
                # if for문이 마지막에 도달했다면 객체 복사
                
                else: # 객체 id가 다르면 객체 복사
                    if obj_num == obj_count:
                        json_data['annotation'].append(copy_annot)
                        print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 복사..')
                        break
            
            with open(self.json_list[idx], 'w') as f:
                json.dump(json_data, f, indent=4)
        print("----------------------------------------------------")

    def copy_annotation(self, annot, copy_annot):
        for key in copy_annot.keys():
            annot[key] = copy_annot[key]
        return annot



    # make backup file
    def makeBackup(self):
        copied_file_count = 0
        try:
            if not os.path.exists(self.backupfolder):
                os.mkdir(self.backupfolder)
        except OSError:
            print('Error: Creating directory of backup')
            exit()

        for idx in range(self.json_file_num):
            shutil.copy(self.json_list[idx], self.backupfolder)
            print(f'{self.json_list[idx]}을 백업파일로 만들었습니다.')
            copied_file_count += 1

        if copied_file_count == 0:
            print('백업파일을 만들 수 없습니다.')
            return 0
        else:
            print('{}개 파일 백업 완료'.format(copied_file_count))
            print("----------------------------------------------------")    
            return copied_file_count

    # restore backup file
    def restoreBackup(self) -> int:
        backupFiles = glob.glob(self.backupfolder + '/*.json')
        copied_file_count = 0
        try:
            if not os.path.exists(self.backupfolder):
                print('백업파일이 없습니다.')
                return False
        # if backup folder is not exist
        except OSError:
            print('Error: backup folder is not exist')
            return False

        for file in backupFiles:
            #shutil.copy(self.backupfolder + '/' + self.json_list[idx].split('\\')[-1], self.json_list[idx])
            shutil.copy(file, self.filepath)
            print(f'{file}을 백업파일로 복원했습니다.')
            copied_file_count += 1
        
        if copied_file_count == 0:
            print('백업파일이 없습니다.')
            return 0
        else:
            print('{}개 파일 복원 완료'.format(copied_file_count))
            print("----------------------------------------------------")    
            return copied_file_count