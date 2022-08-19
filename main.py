import sys
from PyQt5.QtWidgets import QApplication,QPushButton, QMainWindow, \
    QAction, QInputDialog, QDesktopWidget, QFileDialog
from editLabel import EditLabel
        
import glob, json, os, math, copy, shutil
import numpy as np

# show the window
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filepath = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("json파일 편집 프로그램")
        self.resize(600, 400)
        self.center()
        self.statusBarMessage()      

        # # 파일 경로 입력 버튼 생성
        # inputDiButton = QPushButton('파일 경로 입력', self)
        # inputDiButton.move(300, 300)
        # inputDiButton.clicked.connect(self.inputFilePath)

        # result 경로 설정 버튼 생성
        openFolderAction = QAction('Open Folder', self)
        openFolderAction.setShortcut('Ctrl+O')
        openFolderAction.setStatusTip('Open Folder')
        openFolderAction.triggered.connect(self.openFolder)
        openFolderButton = QPushButton('*폴더 경로 설정*', self)
        #openFolderButton.move(300, 350)
        openFolderButton.move(50, 50)
        openFolderButton.clicked.connect(self.openFolder)

        # 0. 파일 백업 버튼 생성
        backupButton = QPushButton('0. 파일 백업', self)
        backupButton.move(400, 100)
        backupButton.clicked.connect(self.backup)

        # 백업 가져오기 버튼 생성
        restoreButton = QPushButton('-1. 백업 가져오기', self)
        restoreButton.move(400, 150)
        restoreButton.clicked.connect(self.restore)

        # 1. 객체 아이디 확인 버튼 생성
        checkObjIdButton = QPushButton('아이디 확인', self)
        checkObjIdButton.move(50, 100)
        checkObjIdButton.clicked.connect(self.checkObjectId)

        # 2. 객체 아이디 변경 버튼 생성
        changeObjIdButton = QPushButton('아이디 변경', self)
        changeObjIdButton.move(50, 150)
        changeObjIdButton.clicked.connect(self.changeObjectId)
        
        # 3. 객체 박스 크기 변경 버튼 생성
        changeDimButton = QPushButton('박스 크기 변경', self)
        changeDimButton.move(50, 200)
        changeDimButton.clicked.connect(self.changeDimension)

        # 4. 객체 박스 각도 변경 버튼 생성
        changeDegreeButton = QPushButton('각도 변경', self)
        changeDegreeButton.move(50, 250)
        changeDegreeButton.clicked.connect(self.changeAngle)

        # # 5. 버그 아이디 수정 버튼 생성
        # changeBugIdButton = QPushButton('5. 버그 아이디 수정', self)
        # changeBugIdButton.move(50, 300)
        # changeBugIdButton.clicked.connect(self.changeBugId)
        
        # 6. 불러오기 확인 버튼 생성
        checkLoadingFiles = QPushButton('불러오기 확인', self)
        checkLoadingFiles.move(150, 100)
        checkLoadingFiles.clicked.connect(self.checkLoadingFiles)
        
        # 7. 카테고리 수정 버튼 생성
        changeCategoryButton = QPushButton('카테고리 수정', self)
        changeCategoryButton.move(150, 150)
        changeCategoryButton.clicked.connect(self.changeCategory)
        
        # 8. 파일 자동 생성 버튼 생성
        autoMakeFiles = QPushButton('파일 자동 생성', self)
        autoMakeFiles.move(150, 200)
        autoMakeFiles.clicked.connect(self.autoMakeFiles)
        
        # 9. 객체 복사 버튼 생성
        copyObjectButton = QPushButton('객체 복사', self)
        copyObjectButton.move(150, 250)
        copyObjectButton.clicked.connect(self.copyObject)
        
        # 10. 파일명 최신화 버튼 생성
        refreshFileNameButton = QPushButton('파일명 최신화', self)
        
        # # 10 파일명 통일 기능 버튼 생성
        # renameFileNameButton = QPushButton('9. 파일명 통일', self)
        # renameFileNameButton.move(150, 300)
        # renameFileNameButton.clicked.connect(self.renameFileName)

        # menubar 생성
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFolderAction)

        self.show()
    
    # 8. 파일 자동 생성 버튼 생성    
    def autoMakeFiles(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return False
        else:
            file_list = glob.glob(self.filepath + r'\*.json')
            file_list.sort()
            try:
                first_file = file_list[0]
            except:
                print("파일 구성이 잘못되었거나 json파일이 없습니다.")
                self.statusBarMessage('파일 구성이 잘못되었거나 json파일이 없습니다.')
            first_file_num = int(first_file.split('_')[-1].split('.')[0])
            extra_file_name = '_'.join(first_file.split('_')[:-1])
            for idx in range(1, 100 -1):
                cur_file = r'{}_{:03d}.json'.format(extra_file_name, idx)
                old_file = r'{}_{:04d}.json'.format(extra_file_name, idx)
                if os.path.isfile(old_file):
                    os.rename(old_file, cur_file)
                    print("파일명을 {}에서 \n{}로 변경하였습니다.".format(old_file, cur_file))
                    continue
                if os.path.isfile(cur_file):
                    continue
                else:
                    json_data = {"frame_no": idx, "annotation": []}
                    with open(cur_file, 'w') as f:
                        json.dump(json_data, f, indent=4)
                        print('{} 파일 생성 완료'.format(cur_file))
        self.editResult.set_json_list(self.filepath)
        print('----------------------------------------------------')
        return True
                        
    # 10. 파일명 통일 기능 버튼 생성
    def renameFileName(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            print('파일 경로를 설정하세요.')
            return False
        
    
    # 6. 불러오기 확인
    def checkLoadingFiles(self)->bool:
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            print('파일 경로를 설정하세요.')
            return False
        else:
            file_list = glob.glob(self.filepath + r'\*.json')
            file_list.sort()
            self.editResult.set_json_list(file_list)
            print("파일 개수 : {}".format(len(file_list)))
            with open(file_list[0], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
                print(json_data)
                print("파일 불러오기 성공")
            return True

    # result 폴더 경로 설정
    def openFolder(self):
        filepath = str(QFileDialog.getExistingDirectory(self, 'Open Folder', './'))
        try:
            if os.path.isfile(glob.glob(filepath + r'\*.json')[0]) or not (filepath == '' or filepath == None):
                self.filepath = filepath
                print(f'{self.filepath}에서 시작합니다.')
                self.statusBar().showMessage(f'{self.filepath}에서 시작합니다.')
                self.editResult = EditLabel(self.filepath)
            else:
                print('잘못된 경로입니다. 경로를 다시 설정해주세요.')
                self.statusBar().showMessage('잘못된 경로입니다. 경로를 다시 설정해주세요.')
        except:
            print('잘못된 경로입니다. 경로를 다시 설정해주세요.')
            self.statusBar().showMessage('잘못된 경로입니다. 경로를 다시 설정해주세요.')

    # 상태 바 메세지 출력
    def statusBarMessage(self, message = None):
        if message is None:
            self.statusBar().showMessage('경로 설정 안됨')
            print('경로 설정 안됨')
        else:
            self.statusBar().showMessage(message)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def inputFilePath(self):
        filepath, ok = QInputDialog.getText(self, '파일 경로', '파일 경로를 설정하세요.:')
        
        # check if the filepath is valid
        if ok and os.path.isfile(glob.glob(filepath + r'\*.json')[0]):
            self.statusBarMessage(filepath)
            self.filepath = filepath
            self.editResult = EditLabel(self.filepath)
        else:
            self.statusBarMessage('파일 경로 오류')
            self.filepath = None

    # 0. 파일 백업
    def backup(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로 설정 안됨')
            return
        else:
            self.editResult.makeBackup()
            self.statusBarMessage('파일 백업 완료')

    def restore(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로 설정 안됨')
            return
        else:
            count = self.editResult.restoreBackup()
            if count == 0:
                self.statusBarMessage('백업 파일이 없습니다.')
            else:
                self.statusBarMessage('{}개 파일 복원 완료'.format(count))

    # 1. 객체 아이디 확인
    def checkObjectId(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return
        else:
            objId, ok = QInputDialog.getText(self, '객체 아이디 확인', '확인하려는 객체 아이디를 입력하세요:')
            try:
                objId = int(objId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            if ok:
                frame_idExist = self.editResult.checkObjectId(objId)
                unique_frame_num = len(np.unique(frame_idExist))
                if frame_idExist:
                    if len(frame_idExist) >= 10:
                        # unique frame_id 출력
                        
                        self.statusBarMessage(f'객체 id {objId}가 프레임 {frame_idExist[0]} ~ {frame_idExist[-1]} 사이 {unique_frame_num}개의 프레임에 {len(frame_idExist)}개 있습니다.')
                    else:
                        self.statusBarMessage(f'객체 id {objId}가 프레임 {frame_idExist}에 {len(frame_idExist)}개 있습니다.')
                else:
                    self.statusBarMessage(f'객체 id {objId}가 존재하지 않습니다.')
            else:
                self.statusBarMessage('취소됨')
    
    # 6. 카테고리 수정
    def changeCategory(self)->bool:
        CATEGORY_0 = {1: 'CAR', 2: 'TRUCK', 3: 'PEDESTRIAN', 4: 'MOTOCYCLE', 
                      5: 'BUS', 6: 'BICYCLE', 7: 'ETC'}
        CATEGORY_1 = {1: 'MEDIAN_STRIP', 2: 'SOUND_BARRIER', 3: 'OVERPASS', 
                      4: 'RAMP_SECT', 5:'ROAD_SIGN', 6: 'STREET_TREES', 7: 'TUNNEL'}
        
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return False
        else:
            objId, ok1 = QInputDialog.getText(self, '카테고리 변경', '카데고리를 수정하려는 객체의 아이디를 입력하세요:')
            try:
                objId = int(objId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return False
            
            objType, ok2 = QInputDialog.getText(self, '카테고리 변경', '객체 타입은? 동적 객체: 0, 주행환경 객체: 1')
            if objType == '0':
                objType = 0
                category, ok3 = QInputDialog.getText(self, '카테고리 변경', "카테고리 입력 1: 'CAR', 2: 'TRUCK', 3: 'PEDESTRIAN', 4: 'MOTOCYCLE', 5: 'BUS', 6: 'BICYCLE', 7: 'ETC'")
                try:
                    if int(category) > 7 or int(category) < 1:
                        self.statusBarMessage('잘못된 카테고리입니다.')
                        return False
                except:
                    self.statusBarMessage('잘못된 카테고리입니다.')
                if ok1 and ok2 and ok3:
                    category = CATEGORY_0[int(category)]
                    self.editResult.changeCategory(objId, objType, category)
                    self.statusBarMessage('카테고리 변경 완료')
                    return True
            elif objType == '1':
                objType = 1
                category, ok3 = QInputDialog.getText(self, '카테고리 변경', "카테고리 입력 1: 'MEDIAN_STRIP', 2: 'SOUND_BARRIER', 3: 'OVERPASS', 4: 'RAMP_SECT', 5:'ROAD_SIGN', 6: 'STREET_TREES', 7: 'TUNNEL'")
                try:
                    if int(category) > 7 or int(category) < 1:
                        self.statusBarMessage('잘못된 카테고리입니다.')
                        return False
                except:
                    self.statusBarMessage('잘못된 카테고리입니다.')
                if ok1 and ok2 and ok3:
                    category = CATEGORY_1[int(category)]
                    self.editResult.changeCategory(objId, objType, category)
                    self.statusBarMessage('카테고리 변경 완료')
                    return True
            else:
                self.statusBarMessage("잘못된 객체 타입입니다. 동적 객체: 1, 주행환경 객체: 2 둘중 하나를 입력해주세요.")

    # 9. 객체 복사 버튼 생성
    def copyObject(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return False
        else:
            print("복사 기능 사용 전에 백업을 권장합니다.")
            file_list = glob.glob(self.filepath + '/*.json')
            if len(file_list) < 100:
                print("파일이 100개 미만입니다. 누락된 파일을 확인하세요.")
                self.statusBarMessage('파일이 100개 미만입니다. 누락된 파일을 확인하세요.')
                return False
            elif len(file_list) > 100:
                print("파일이 100개 초과입니다. 파일 구성을 확인하세요.")
                self.statusBarMessage('파일이 100개 초과입니다. 파일 구성을 확인하세요.')
                return False
            else:
                objId, ok1 = QInputDialog.getText(self, '객체 복사', '복사하려는 객체의 아이디를 입력하세요. 복사 기능 사용 전에 백업을 권장합니다.')
                pickFrame, ok2 = QInputDialog.getText(self, '객체 복사', '복사하려는 객체가 있는 프레임중 하나의 값을 입력하세요(1 ~ 100).')
                startFrame, ok3 = QInputDialog.getText(self, '객체 복사', '객체를 복사하려는 프레임 범위의 처음을 입력하세요(1 ~ 100).')
                endFrame, ok4 = QInputDialog.getText(self, '객체 복사', '객체를 복사하려는 프레임 범위의 마지막을 입력하세요(1 ~ 100).')
                isChange, ok5 = QInputDialog.getText(self, '객체 복사', '객체 복사를 설정한 프레임 범위 내에 같은 아이디의 객체 정보를 변경하시겠습니까? 예: 1, 아니오: 0')
                try:
                    if int(isChange) != 1 and int(isChange) != 0:
                        print("잘못된 입력입니다.")
                        self.statusBarMessage('잘못된 입력입니다.')
                        return False
                    objId = int(objId)
                    pickFrame = int(pickFrame)
                    startFrame = int(startFrame)
                    endFrame = int(endFrame)
                    #chage ischange to bool
                    isChange = bool(int(isChange))
                except:
                    print("잘못된 입력입니다.")
                    self.statusBarMessage('잘못된 입력입니다.')
                    return False

                if ok1 and ok2 and ok3 and ok4 and ok5:
                    self.editResult.copyObject(objId, pickFrame, startFrame, endFrame, isChange)
                    self.statusBarMessage('객체 복사 완료')
                    return True

    def wr_input(self):
        print("잘못된 입력입니다.")
        self.statusBarMessage('잘못된 입력입니다.')
        return False
    
    def ckIn100(self, input):
        if input.isdigit():
            if input > 100 or input < 1:
                return False
            else:
                return True
        else:
            return False

    # 2. 객체 아이디 변경 버튼
    def changeObjectId(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return
        else:
            objId, ok1 = QInputDialog.getText(self, '객체 아이디 변경', '변경하려는 객체 아이디를 입력하세요:')
            try:
                objId = int(objId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            changedId, ok2 = QInputDialog.getText(self, '객체 아이디 변경', '변경될 객체 아이디를 입력하세요:')
            try:
                changedId = int(changedId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            if ok1 and ok2:
                print(objId, changedId)
                self.editResult.changeId(objId, changedId)
                self.statusBar().showMessage('객체 아이디 {}를 {}로 변경'.format(objId, changedId))
    
    # 3. 객체 박스 크기 변경 버튼
    def changeDimension(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return
        else:
            objId, ok1 = QInputDialog.getText(self, '객체 박스 크기 변경', '변경하려는 객체 아이디를 입력하세요:')
            try:
                objId = int(objId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            width, ok2 = QInputDialog.getText(self, '객체 박스 크기 변경', '변경할 너비(Width)를 입력하세요(0: no change):')
            height, ok3 = QInputDialog.getText(self, '객체 박스 크기 변경', '변경할 높이(Height)를 입력하세요(0: no change):')
            length, ok4 = QInputDialog.getText(self, '객체 박스 크기 변경', '변경할 길이(Length)를 입력하세요(0: no change):')
            if ok1 and ok2 and ok3 and ok4:
                print('ID: ', objId, ' dim: ', (width, height, length))
                box = self.editResult.changeDim(objId, width, height, length)
                self.statusBar().showMessage('객체 아이디 {}의 박스 크기를 {}으로 변경'.format(objId, box))

    # 4. 객체 박스 각도 변경 버튼
    def changeAngle(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return
        else:
            objId, ok1 = QInputDialog.getText(self, '객체 박스 각도 변경', '변경하려는 객체 아이디를 입력하세요:')
            try:
                objId = int(objId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            angle, ok2 = QInputDialog.getText(self, '객체 박스 각도 변경', '변경할 각도를 입력하세요(degree):')
            try:
                angle = float(angle)
            except:
                self.statusBarMessage('잘못된 각도입니다.')
                return
            if angle > 360 or angle < 0:
                self.statusBarMessage('잘못된 각도입니다.')
                return
            if ok1 and ok2:
                print('ID: ', objId, ' angle: ', angle)
                self.editResult.changeAngle(objId, angle)
                self.statusBar().showMessage('객체 아이디 {}의 박스 각도를 {}도로 변경'.format(objId, angle))

    # 5. 버그 아이디 변경 버튼
    def changeBugId(self):
        if self.filepath is None:
            self.statusBarMessage('파일 경로를 설정하세요.')
            return
        else:
            maxId, ok2 = QInputDialog.getText(self, '버그 아이디 변경', '변경하지 않을 가장 큰 아이디를 입력하세요:')
            try:
                maxId = int(maxId)
            except:
                self.statusBarMessage('잘못된 아이디입니다.')
                return
            if ok2:
                print('maxId: ', maxId)
                count = self.editResult.changeBuggedId(maxId)

                self.statusBar().showMessage('크기 {} 이상의 버그 아이디 {}개를 변경 완료'.format(maxId, count))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())