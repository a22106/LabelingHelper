import sys, zipfile
from PyQt5.QtWidgets import QApplication,QPushButton, QMainWindow, \
    QAction, QInputDialog, QDesktopWidget, QFileDialog
from editLabel import EditLabel
from analyzeLabel import AnalyzeLabel
from pyqtDesign.pyqtDesigner import Ui_MainWindow

import glob, json, os, time
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.saveOpendFolder = './'
        self.pathInit()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.setWindowTitle("json파일 편집 프로그램")
        self.statusBarMessage()
        #self.centerWindow()
        self.mainWindow()

    def pathInit(self, inputPath = None):
        self.inputPath = None
        self.clipPath = None
        self.upperPath = None

        if inputPath:
            basePath = os.path.basename(inputPath)

            if basePath == 'result':
                self.inputPath = inputPath
                self.clipPath = os.path.dirname(inputPath)
                self.upperPath = os.path.dirname(self.clipPath)
    
    # 6. 불러오기 확인
    def checkLoadingFiles(self)->bool:
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return False
        else:
            file_list = glob.glob(self.inputPath + r'\*.json')
            file_list.sort()
            self.editLabel.setPath(self.inputPath)
            self.printText("파일 개수 : {}".format(len(file_list)))
            with open(file_list[0], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
                self.printText(json_data)
                self.printText("파일 불러오기 성공")
            return True

    # result 폴더 경로 설정
    def openFolder(self):
        path = str(QFileDialog.getExistingDirectory(self, 'Open Folder', self.saveOpendFolder))
        self.saveOpendFolder = path
        try:
            
            if(path == '' or path == None):
                self.printText('잘못된 경로입니다. 경로를 다시 설정해주세요.')
                self.statusBar().showMessage('잘못된 경로입니다. 경로를 다시 설정해주세요.')
            # elif not os.path.isfile(glob.glob(path + r'\*.json')[0]):
            #     self.printText("")    
            else:
                self.inputPath = path
                self.editLabel = EditLabel(self.inputPath)
                self.analyzeLabel = AnalyzeLabel(self.inputPath)
                self.printText(f'{self.inputPath}에서 시작합니다.')
                self.statusBar().showMessage(f'{self.inputPath}에서 시작합니다.')
                
                
        except:
            self.printText('잘못된 경로입니다. 경로를 다시 설정해주세요.')
            self.statusBar().showMessage('잘못된 경로입니다. 경로를 다시 설정해주세요.')
    
    # 파일명 일괄 수정
    def refreshFileName(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return
        extract_path = os.path.dirname(self.analyzeLabel.clipPath)
        
        # create clip list only is folder
        clip_list = os.listdir(extract_path)
        clip_list.sort()

        clip_list_path = [os.path.join(extract_path, clip_) for clip_ in clip_list if os.path.isdir(os.path.join(extract_path, clip_))]
        for clip in clip_list_path:
            self.analyzeLabel.fix_filenames(clip)
        self.editLabel.setPath(self.inputPath) # result 경로 파일 목록 새로고침
        self.printText('파일명 일괄 수정 완료')
        self.printText('----------------------------------------------------')
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def inputFilePath(self):
        filepath, ok = QInputDialog.getText(self, '파일 경로', '클립 경로를 설정하세요.:')
        
        # check if the filepath is valid
        if ok and os.path.isfile(glob.glob(filepath + r'\*.json')[0]):
            self.statusBarMessage(filepath)
            self.inputPath = filepath
            self.editLabel = EditLabel(self.inputPath)
        else:
            self.statusBarMessage('파일 경로 오류')
            self.inputPath = None

    # 0. 파일 백업
    def backup(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return
        else:
            self.editLabel.makeBackup()
            self.statusBarMessage('파일 백업 완료')

    def restore(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return
        else:
            count = self.editLabel.restoreBackup()
            if count == 0:
                self.statusBarMessage('백업 파일이 없습니다.')
                self.printText('백업 파일이 없습니다.')
            else:
                self.statusBarMessage('{}개 파일 복원 완료'.format(count))

    # 1. 객체 아이디 확인
    def checkObjectId(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return
        else:
            #objId, ok = QInputDialog.getText(self, '객체 아이디 확인', '확인하려는 객체 아이디를 입력하세요:')
            # get QSpinBox number
            objId = self.ui.spinBoxfromIdchange_2.value()
            
            if objId:
                frame_idExist = self.editLabel.checkObjectId(objId)
                unique_frame_num = len(np.unique(frame_idExist))
                if frame_idExist:
                    if len(frame_idExist) >= 100:
                        # unique frame_id 출력
                        
                        self.statusBarMessage(f'객체 id {objId}가 프레임 {frame_idExist[0]} ~ {frame_idExist[-1]} 사이 {unique_frame_num}개의 프레임에 {len(frame_idExist)}개 있습니다.')
                    else:
                        self.statusBarMessage(f'객체 id {objId}가 프레임 {frame_idExist}에 {len(frame_idExist)}개 있습니다.')
                else:
                    self.statusBarMessage(f'객체 id {objId}가 존재하지 않습니다.')
            else:
                self.statusBarMessage('취소됨')


    # 2. 객체 아이디 변경 버튼
    def changeObjectId(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            return
        else:
            objId = self.ui.spinBoxfromIdchange.value()
            try:
                objId = int(objId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            changedId = self.ui.spinBoxToIdchange.value()
            try:
                changedId = int(changedId)
            except:
                self.statusBarMessage('잘못된 객체 아이디입니다.')
                return
            if objId and changedId:
                
                self.editLabel.changeId(objId, changedId)
                self.printText('객체 아이디 {}를 {}로 변경'.format(objId, changedId))
                self.statusBar().showMessage('객체 아이디 {}(을)를 {}로 변경'.format(objId, changedId))
    
    # 3. 객체 박스 크기 변경 버튼
    def changeDimension(self):
        if self.inputPath is None:
            self.printText('클립 경로를 설정하세요.')
            return
        else:
            objId = self.ui.spinBoxfromIdchange_3.value()
            width = self.ui.doubleSpinBox.value()
            height = self.ui.doubleSpinBox_2.value()
            length = self.ui.doubleSpinBox_3.value()
            if objId:
                self.printText(f'ID: {objId}의 크기를 dim(width:{width}, height:{height}, length:{length})로 변경')
                box = self.editLabel.changeDim(objId, width, height, length)
                self.statusBar().showMessage('객체 아이디 {}의 박스 크기를 {}으로 변경'.format(objId, box))

    # 4. 객체 박스 각도 변경 버튼
    def changeAngle(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            return
        else:
            objId = self.ui.spinBoxfromIdchange_3.value()
            angle = self.ui.doubleSpinBox_4.value()
            try:
                angle = float(angle)
            except:
                self.printText('잘못된 각도입니다.')
                self.statusBarMessage('잘못된 각도입니다.')
                return
            if angle > 360 or angle < 0:
                self.printText('잘못된 각도입니다.')
                self.statusBarMessage('잘못된 각도입니다.')
                return
            if objId and angle>=0:
                self.editLabel.changeAngle(objId, angle)
                self.printText('객체 아이디 {}의 박스 각도를 {}도로 변경'.format(objId, angle))
                self.statusBar().showMessage('객체 아이디 {}의 박스 각도를 {}도로 변경'.format(objId, angle))

    # 5. 버그 아이디 변경 버튼
    def changeBugId(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            return
        else:
            maxId, ok2 = QInputDialog.getText(self, '버그 아이디 변경', '변경하지 않을 가장 큰 아이디를 입력하세요:')
            try:
                maxId = int(maxId)
            except:
                self.statusBarMessage('잘못된 아이디입니다.')
                return
            if ok2:
                self.printText('maxId: ', maxId)
                count = self.editLabel.changeBuggedId(maxId)

                self.statusBar().showMessage('크기 {} 이상의 버그 아이디 {}개를 변경 완료'.format(maxId, count))

    #6. 카테고리 수정
    def changeCategory(self)->bool:
        _CATEGORY = {1: 'CAR', 2: 'TRUCK', 3: 'PEDESTRIAN', 4: 'MOTOCYCLE', 
                      5: 'BUS', 6: 'BICYCLE', 7: 'ETC', 8:'MEDIAN_STRIP', 9:'SOUND_BARRIER', 10:'OVERPASS', 11:'RAMP_SECT', 12: 'ROAD_SIGN', 
                      13:'STREET_TREES', 14:'TURNNEL'}
        _OBJTYPE = {0: "동적객체", 1: "주행환경 객체"}
        
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return False
        
        objId = self.ui.spinBoxfromIdCategory.value()
        
        objCategory = self.ui.comboBox.currentIndex()
            
        if objId and objCategory:
            # objCategory1 ~ 7: 동적객체(0), 8 ~ 14: 주행환경 객체(1)
            if objCategory < 8:
                objType = 0
            else:
                objType = 1
            
            
            self.editLabel.changeCategory(objId, objType, _CATEGORY[objCategory])
            self.statusBarMessage('카테고리 변경 완료')
            self.printText('카테고리 변경 완료')
            self.printText('ID: {}, type: {}, category: {}'.format(objId, _OBJTYPE[objType], _CATEGORY[objCategory]))
            return True
        else:
            self.statusBarMessage("객체 아이디 설정 및 카테고리 타입 설정을 다시 하세요.")
        

    def wr_input(self):
        self.printText("잘못된 입력입니다.")
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

    # 8. 파일 자동 생성 버튼 생성    
    def autoMakeFiles(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            return False
        else:
            file_list = self.editLabel.resultList
            try:
                first_file = file_list[0]
            except:
                self.printText("파일 구성이 잘못되었거나 json파일이 없습니다.")
                self.statusBarMessage('파일 구성이 잘못되었거나 json파일이 없습니다.')
            first_file_num = int(first_file.split('_')[-1].split('.')[0])
            extra_file_name = '_'.join(first_file.split('_')[:-1])
            for idx in range(1, 100 +1):
                cur_file = r'{}_{:03d}.json'.format(extra_file_name, idx)
                old_file = r'{}_{:04d}.json'.format(extra_file_name, idx)
                if os.path.isfile(old_file):
                    os.rename(old_file, cur_file)
                    self.printText("파일명을 {}에서 \n{}로 변경하였습니다.".format(old_file, cur_file))
                    continue
                if os.path.isfile(cur_file):
                    continue
                else:
                    json_data = {"frame_no": idx, "annotation": []}
                    with open(cur_file, 'w') as f:
                        json.dump(json_data, f, indent=4)
                        self.printText('{} 파일 생성 완료'.format(cur_file))
        self.editLabel.setPath(self.inputPath)
        self.printText('----------------------------------------------------')
        return True
    
    # 9. 객체 복사 버튼 생성
    def copyObject(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            return False
        else:
            self.printText("복사 기능 사용 전에 백업을 권장합니다.")
            self.editLabel.setPath(self.inputPath)
            self.editLabel.resultNum
            # if self.editLabel.resultNum < 100:
            #     self.printText("파일이 100개 미만입니다. 누락된 파일을 확인하세요.")
            #     self.statusBarMessage('파일이 100개 미만입니다. 누락된 파일을 확인하세요.')
            #     return False
            if self.editLabel.resultNum > 100:
                self.printText("파일이 100개 초과입니다. 파일 구성을 확인하세요.")
                self.statusBarMessage('파일이 100개 초과입니다. 파일 구성을 확인하세요.')
                return False
            else:
                if self.editLabel.resultNum < 100:
                    self.autoMakeFiles()
                objId = self.ui.spinBoxfromIdchange_4.value()
                pickFrame = self.ui.spinBoxfromIdchange_5.value()
                startFrame = self.ui.spinBoxfromIdchange_6.value()
                endFrame = self.ui.spinBoxfromIdchange_7.value()
                isChange, ok5 = QInputDialog.getText(self, '객체 복사', '객체 복사를 설정한 프레임 범위 내에 같은 아이디의 객체 정보를 변경하시겠습니까? 예: 1, 아니오: 0')
                try:
                    #chage ischange to bool
                    isChange = bool(int(isChange))
                except:
                    self.printText("잘못된 입력입니다.")
                    self.statusBarMessage('잘못된 입력입니다.')
                    return False

                if objId and pickFrame and startFrame and endFrame and ok5:
                    self.editLabel.copyObject(objId, pickFrame, startFrame, endFrame, isChange)
                    self.statusBarMessage('객체 복사 완료')
                    self.printText('객체 복사 완료')
                    return True
                        
    # 10. 파일명 통일 기능 버튼 생성
    def renameFileName(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return False

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def statusBarMessage(self, message = None):
        if message:
            self.statusBar().showMessage(message)
        else:
            self.statusBar().showMessage("경로를 설정해주세요")
    
    def printText(self, text = None):
        self.ui.textBrowser.append(text)
        print(text)
        
    
    def printOnBarBrowser(self, text = None): ## 추후 적용
        self.printText(text)
        self.statusBar().showMessage(text)
    
    def checkIfFileRefreshedOld(self):
        root_path = os.path.dirname(self.editLabel.clipPath)
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
        
    def extractZip(self):
        try:
            with zipfile.ZipFile(self.editLabel.clipPath + '/result.zip', 'r') as zip_ref:
                zip_ref.extractall(self.editLabel.clipPath + '/result')
            self.editLabel.setPath(self.editLabel.clipPath)
            self.printText('압축 풀기 완료')
            self.statusBarMessage('압축 풀기 완료')
        except:
            self.printText('압축 풀기 실패')
            self.printText('해당 클립 폴더 내에 result.zip 파일이 없습니다.')
            self.statusBarMessage('해당 클립 폴더 내에 result.zip 파일이 없습니다.')

    def mainWindow(self):
        self.center()
        self.ui.pushButton_4.clicked.connect(self.openFolder)
        self.ui.pushButton_11.clicked.connect(self.checkObjectId)
        self.ui.pushButton_5.clicked.connect(self.backup)
        self.ui.pushButton_6.clicked.connect(self.restore)
        self.ui.pushButton_10.clicked.connect(self.changeObjectId)
        self.ui.pushButton_9.clicked.connect(self.changeCategory)
        self.ui.pushButton.clicked.connect(self.changeDimension)
        self.ui.pushButton_7.clicked.connect(self.changeAngle)
        self.ui.pushButton_8.clicked.connect(self.copyObject)
        self.ui.pushButton_3.clicked.connect(self.refreshFileName)
        self.ui.pushButton_2.clicked.connect(self.autoMakeFiles)
        self.ui.pushButton_13.clicked.connect(self.checkIfFileRefreshedOld)
        # self.ui.pushButton_12.clicked.connect(self.autoMakeFilesOld)
        self.ui.pushButton_14.clicked.connect(self.extractZip)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())