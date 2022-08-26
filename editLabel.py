import glob, json, os, copy, shutil, math


class EditLabel():
    def __init__(self, inputPath:str):
        inputPath = inputPath.replace('\\', '/')
        self.setPath(inputPath)
        

    def __len__(self):
        return len(self.resultList)

    def __getitem__(self, index):
        try:
            with open(self.resultList[index], 'r') as f:
                json_data = json.load(f)
        except Exception as e:
            print(e)
            exceptmessage = f'{self.resultList[index]}의 json 파일을 읽을 수 없습니다.'
            print(exceptmessage)
            return exceptmessage
        return json_data

    def setPath(self, path):
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
        self.clipPath = path
        self.clipName = path.split('/')[-1]
        self.resultPath = path + '/result'
        
        if os.path.isdir(self.resultPath):
            self.resultList = glob.glob(self.resultPath + '/*.json')
            self.resultList.sort()
            self.resultNum = len(self.resultList)
            
        self.backupfolder = path + '/result_backup'
    
    def getResultList(self):
        return self.resultList

    def showJson(self, frame):
        with open(self.resultList[frame], 'r') as f:
            json_data = json.load(f)
        print("Show json info")
        return json_data
    
    # def set_json_list(self, filePath): 
    #     # if file Path is list
    #     if isinstance(filePath, list):
    #         self.resultList = filePath
    #     elif filePath.split('/')[-1] != 'result':
    #         self.resultList = glob.glob(filePath + 'result/*.json')
    #     else:
    #         self.resultList = glob.glob(filePath + '/*.json')
    #     self.resultList.sort()
    #     self.resultNum = len(self.resultList)
    #     return self.resultList, self.resultNum

    # check object id
    def checkObjectId(self, id, maxId = None) -> list:
        frame_is_Id = []
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
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
    def changeDim(self, id, width, height, length, frame = None):
        dim = [width, height, length] # 변경할 크기
        frames = []
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            for annot in json_data['annotation']:
                if int(annot['id']) == id:
                    for dim_idx, dim_value in enumerate(dim):
                        if dim_value:
                            annot['3d_box'][0]['dimension'][dim_idx] = dim_value
                    print(f"프레임 {json_data['frame_no']}: {id}의 박스 크기를 {annot['3d_box'][0]['dimension']}로 변경")
                    frames.append(json_data['frame_no'])
                    with open(self.resultList[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                    continue
        return annot['3d_box'][0]['dimension'], frames

    # change id
    def changeId(self, id, newId):
        frames = []
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            for annot in json_data['annotation']:
                if annot['id'] == f'{id}' or annot['id'] == id:
                    annot['id'] = newId
                    print(f'프레임 {json_data["frame_no"]}: {id}의 id를 {newId}로 변경')
                    frames.append(json_data['frame_no'])
                    with open(self.resultList[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")    
        return frames

    # change Angle
    def changeAngle(self, id, angle):
        r'''
        id: int - 객체 번호
        angle: float 객체 회전 각도 (degree, 12시 방향 0도)
        return: list - 회전 각도가 변경된 프레임 번호
        '''
        frames = []
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            
            # change degree to radian
            angle_rad = math.radians(angle)

            for annot in json_data['annotation']:
                if int(annot['id']) == id:
                    formerAngle = math.degrees(annot['3d_box'][0]['rotation_y'])
                    annot['3d_box'][0]['rotation_y'] = angle_rad
                    print(f'프레임 {json_data["frame_no"]}: {id}의 각도 변경 {formerAngle} -> {angle}')
                    frames.append(json_data['frame_no'])
                    with open(self.resultList[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')
        print("----------------------------------------------------")
        return frames, formerAngle
    
    # chnage angle 180
    def changeAngle180(self, id):
        frames = []
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            
            for annot in json_data['annotation']:
                if int(annot['id']) == id:
                    curAngle = annot['3d_box'][0]['rotation_y']
                    changedAngle = (curAngle + math.pi) % (2 * math.pi)
                    annot['3d_box'][0]['rotation_y'] = changedAngle
                    print(f'프레임 {json_data["frame_no"]}: {id}의 각도를 180˚ 회전 {math.degrees(curAngle)}-> {math.degrees(changedAngle)}')
                    frames.append(json_data['frame_no'])
                    with open(self.resultList[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
        return frames, math.degrees(curAngle), math.degrees(changedAngle)
                            
    # change category
    def changeCategory(self, id, obj_type, category: str):
        r'''
        id: int - 객체 번호
        obj_type: object type
        category: object category
        return: frames
        '''
        frames = []
        atypical_cat = ['MEDIAN_STRIP', 'SOUND_BARRIER', 'OVERPASS', 'RAMP_SECT', 'TUNNEL']
    
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
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
                    with open(self.resultList[idx], 'w') as f:
                        json.dump(json_data, f, indent=4)
                        #print(f'{self.json_list[idx]}에 변경 완료')    
        print("----------------------------------------------------")
        return frames

    # change bugged object id
    def changeBuggedId(self, max_id):
        # change bugged id that is bigger than max_id and end with series of 1
        # for example if max_id is 30, chage 5111 to 5, 101 to 10, 111 to 11, 2111 to 21, 3111 to 3, 4111 to 4, 1011 to 10
        # if max_id is 100, change 5111 to 51, 101 to 10, 111 to 11, 2111 to 21, 3111 to 3, 4111 to 4, 1011 to 10
        # all buged numbers end with series of 1
        changed_num_count = 0
        for idx in range(self.resultNum):
            with open(self.resultList[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
            max_id = str(max_id) # 변경할 크기

            for annot in json_data['annotation']:
                if int(annot['id']) > int(max_id):
                    for i in range(len(annot['id'])):
                        if annot['id'][i] == '1' and int(annot['id'][:i+1]) > int(max_id):
                            
                            annot['id'] = annot['id'][:i]
                            print(f'프레임 {json_data["frame_no"]}: {annot["id"]}의 id를 {annot["id"][:i]}로 변경')
                            with open(self.resultList[idx], 'w') as f:
                                json.dump(json_data, f, indent=4)
                                changed_num_count += 1
                            break
                        
                        elif annot['id'][i] == '1' and len(annot['id'][:i]) >= len(max_id):
                            annot['id'] = annot['id'][:i]
                            print(f'프레임 {json_data["frame_no"]}: {annot["id"]}의 id를 {annot["id"][:i]}로 변경')
                            with open(self.resultList[idx], 'w') as f:
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
        frames_copy = []
        frames_paste = []
        
        with open(self.resultList[frame-1], 'r') as f:
            json_data = json.load(f) # 목표 프레임의 json 데이터 불러옴
        for annot1 in json_data['annotation']:
            if int(annot1['id']) == id:
                copy_annot = annot1
                print(copy_annot)
        
        # 입력한 시작 프레임부터 종료 프레임까지 복사
        for idx in range(start-1, end):
            if idx+1 == frame:
                continue

            with open(self.resultList[idx], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴

            # 해당 프레임에 아무 객체 정보가 없다면 바로 객체 복사
            if not json_data['annotation']:
                json_data['annotation'].append(copy_annot)
                with open(self.resultList[idx], 'w') as f:
                    json.dump(json_data, f, indent=4)
                print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 복사.')
                frames_copy.append(json_data['frame_no'])
                continue
            
            obj_num = len(json_data['annotation']) # 해당 프레임에 있는 객체 수
            obj_count = 0
            for annot2 in json_data['annotation']:
                obj_count+=1
                if int(annot2['id']) == id:
                    if CHANGE: # 붙여넣기 옵션이 켜져있다면 기존 객체의 값을 덮어쓰기
                        annot2 = self.copy_annotation(annot2, copy_annot)
                        print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 붙여넣기')
                        frames_paste.append(json_data['frame_no'])
                        break

                    else: # 붙여넣기 옵션이 꺼져있다면 지나가기
                        print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 지나감')
                        break
                
                # if for문이 마지막에 도달했다면 객체 복사
                
                else: # 객체 id가 다르면 객체 복사
                    if obj_num == obj_count:
                        json_data['annotation'].append(copy_annot)
                        print(f'프레임 {json_data["frame_no"]}: 객체 {id}의 오브젝트를 복사..')
                        frames_copy.append(json_data['frame_no'])
                        break
            
            with open(self.resultList[idx], 'w') as f:
                json.dump(json_data, f, indent=4)
        print("----------------------------------------------------")
        return frames_copy, frames_paste

    def copy_annotation(self, annot, copy_annot):
        for key in copy_annot.keys():
            annot[key] = copy_annot[key]
        return annot



    # make backup file
    def makeBackup(self):
        copied_file_count = 0
        backupFileList = []
        try:
            if not os.path.exists(self.backupfolder):
                os.mkdir(self.backupfolder)
        except OSError:
            print('Error: Creating directory of backup')
            exit()

        for idx in range(self.resultNum):
            shutil.copy(self.resultList[idx], self.backupfolder)
            print(f'{self.resultList[idx]}을 백업파일로 만들었습니다.')
            backupFileList.append(self.backupfolder+self.resultList[idx].split('/')[-1])
            copied_file_count += 1

        if copied_file_count == 0:
            print('백업파일을 만들 수 없습니다.')
            return 0
        else:
            print('{}개 파일 백업 완료'.format(copied_file_count))
            print("----------------------------------------------------")    
            return copied_file_count, backupFileList

    # restore backup file
    def restoreBackup(self) -> int:
        backupFiles = glob.glob(self.backupfolder + '/*.json')
        copied_file_count = 0
        curFilesList = []
        try:
            if not os.path.exists(self.backupfolder):
                print('백업파일이 없습니다.')
                return False
        # if backup folder is not exist
        except OSError:
            print('Error: backup folder is not exist')
            return False
        try:
            if not os.path.exists(self.resultPath):
                os.mkdir(self.resultPath)
        except OSError:
            print('Error: Creating directory of backup')
            exit()
            
        for file in backupFiles:
            #shutil.copy(self.backupfolder + '/' + self.json_list[idx].split('\\')[-1], self.json_list[idx])
            shutil.copy(file, self.resultPath)
            curFilesList.append(self.resultPath + '/' + file.split('\\')[-1])
            print(f'{file}을 백업파일로 복원했습니다.')
            copied_file_count += 1
        self.setPath(self.clipPath)
        
        if copied_file_count == 0:
            print('백업파일이 없습니다.')
            return 0
        else:
            print('{}개 파일 복원 완료'.format(copied_file_count))
            print("----------------------------------------------------")    
            return copied_file_count, curFilesList