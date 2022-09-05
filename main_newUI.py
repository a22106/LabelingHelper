import sys, zipfile
from PyQt5.QtWidgets import QApplication, QMainWindow, \
     QInputDialog, QDesktopWidget, QFileDialog, QMessageBox, QPushButton
from editLabel import EditLabel
from analyzeLabel import AnalyzeLabel
from pyqtDesign.pyqtDesigner import Ui_MainWindow
from datetime import datetime

import glob, json, os, time
import numpy as np

now = datetime.now()

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
            self.editLabel.setPath(self.inputPath)
            file_list = self.editLabel.getResultList()
            self.printText("파일 개수 : {}".format(len(file_list)))
            with open(file_list[0], 'r') as f:
                json_data = json.load(f) # json 데이터 불러옴
                self.printText(json_data)
                self.printText("파일 불러오기 성공")
            return True

    # result 폴더 경로 설정
    def openFolder(self):
        path = str(QFileDialog.getExistingDirectory(self, 'Open Folder', self.saveOpendFolder))
        
        try:
            if(path == '' or path == None):
                self.printText('잘못된 경로입니다. 경로를 다시 설정해주세요.')
                if not self.inputPath:
                    self.statusBar().showMessage('잘못된 경로입니다. 경로를 다시 설정해주세요.')
            else:
                self.saveOpendFolder = path # 다음 폴더 열기 경로 저장
                self.inputPath = path
                self.resultPath = path + r'\result'
                self.editLabel = EditLabel(self.inputPath)
                self.analyzeLabel = AnalyzeLabel(self.inputPath)
                self.printText('****************폴더 경로 설정 완료.')
                self.printText(f'클립 경로 {self.inputPath}에서 작업을 시작합니다.')
                if not os.path.isdir(self.resultPath):
                    self.printText('경고) result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
                self.statusBar().showMessage(f'클립 경로 {self.inputPath}에서 작업을 시작합니다.')
                
                
        except:
            self.printText('잘못된 경로입니다. 경로를 다시 설정해주세요.')
            self.statusBar().showMessage('잘못된 경로입니다. 경로를 다시 설정해주세요.')
    
    # 파일명 일괄 수정
    def refreshFileName(self):
        extract_path = self.ui.lineEdit.text()

        # extract_path = os.path.dirname(self.analyzeLabel.clipPath)
        if extract_path:
            self.analyzeLabel = AnalyzeLabel(extractPath=extract_path)
            clipPathList = glob.glob(self.analyzeLabel.extractPath + r'\*')
            clipPathList.sort()
            # clipPathList에서 Clip 폴더만 추출
            clipPathList = [clipPath for clipPath in clipPathList if 'Clip' in clipPath and os.path.isdir(clipPath)]
            self.analyzeLabel.clipPathList = clipPathList

            for clip in clipPathList:
                self.analyzeLabel.fix_filenames(clip)
            # self.editLabel.setPath(self.inputPath) # result 경로 파일 목록 새로고침
            self.printText('파일명 일괄 수정 완료')
            self.printText('----------------------------------------------------')
        else:
            self.printText('잘못된 경로입니다. 클립 경로로 다시 설정해주세요.')
            self.statusBar().showMessage('잘못된 경로입니다. 클립 경로로 다시 설정해주세요.')
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def inputFilePath(self):
        filepath, ok = QInputDialog.getText(self, '파일 경로', '클립 경로를 설정하세요.:')
        
        # check if the filepath is valid
        if ok and os.path.isfile(glob.glob(filepath + r'\*.json')[0]):
            self.statusBarMessage("클립 경로: ", filepath)
            self.inputPath = filepath
            self.editLabel = EditLabel(self.inputPath)
        else:
            self.statusBarMessage('파일 경로 오류')
            self.printText('파일 경로 오류')
            self.inputPath = None

    # 0. 파일 백업
    def backup(self):
        if self.inputPath is None:
            self.printText('클립 경로를 설정하세요.')
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
            return False
        else:
            self.printText('백업 시작')
            backupFileNum, backupFileList = self.editLabel.makeBackup()
            for idx, backupFile in enumerate(backupFileList):
                self.printText(f'{idx+1}/{backupFileNum} {backupFile} 백업 완료')
            self.printText(f'{backupFileNum}개 파일 백업 완료')
            return True

    def restore(self):
        if self.inputPath is None:
            self.printText('클립 경로를 설정하세요.')
            return
        elif os.path.isdir(self.editLabel.backupfolder) is False:
            self.printText('백업 폴더가 없습니다. 백업 폴더를 확인해주세요.')
        else:
            self.printText('파일 복원 시작')
            count, curFileList = self.editLabel.restoreBackup()
            if count == 0:
                self.printText('백업할 파일이 없습니다.')
            else:
                for idx, curFile in enumerate(curFileList):
                    self.printText(f'{idx+1}/{count} {curFile} 복원 완료')
                self.printText('{}개 파일 복원 완료'.format(count))

    # 1. 객체 아이디 확인
    def checkObjectId(self):
        if self.inputPath is None :
            self.printText('클립 경로를 설정하세요.')
            return
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
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
                        
                        self.printText(f'객체 id {objId}가 프레임 {frame_idExist[0]} ~ {frame_idExist[-1]} 사이 {unique_frame_num}개의 프레임에 {len(frame_idExist)}개 있습니다.')
                    else:
                        self.printText(f'객체 id {objId}가 프레임 {frame_idExist}에 {len(frame_idExist)}개 있습니다.')
                        
                    self.printText(f'프레임 {frame_idExist[0]} 내 객체 id {objId}의 정보:')
                    firstframe = frame_idExist[0]
                    for obj in self.editLabel[firstframe]['annotation']:
                        if int(obj['id']) == objId:
                            self.printText(f'{obj}')
                            continue
                else:
                    self.printText(f'객체 id {objId}가 존재하지 않습니다.')
            else:
                self.printText('잘못된 객체 아이디입니다.')


    # 2. 객체 아이디 변경 버튼
    def changeObjectId(self):
        if self.inputPath is None:
            self.printText('클립 경로를 설정하세요.')
            return
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
        else:
            objId = self.ui.spinBoxfromIdchange.value()
            changedId = self.ui.spinBoxToIdchange.value()
            if objId and changedId:
                frames = self.editLabel.changeId(objId, changedId)
                self.printText('객체 아이디 변경. {} -> {}'.format(objId, changedId))
                self.printText('객체 변경 프레임: \n{}'.format(frames))
            else:
                self.printText('수정할 ID나 변경될 ID를 확인해주세요. 0은 입력할 수 없습니다.')
    
    # 3. 객체 박스 크기 변경 버튼
    def changeDimension(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText('클립 경로를 설정하세요.')
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
            return False
        else:
            objId = self.ui.spinBoxfromIdchange_3.value()
            width = self.ui.doubleSpinBox.value()
            height = self.ui.doubleSpinBox_2.value()
            length = self.ui.doubleSpinBox_3.value()
            if objId:
                box, frames = self.editLabel.changeDim(objId, width, height, length)
                self.printText(f'ID: {objId}의 크기를 (width:{box[0]:.03f}, height:{box[1]:.03f}, length:{box[2]:.03f})로 변경 완료')
                self.printText(f'객체 변경 프레임: \n{frames}')
                print("----------------------------------------------------")
                return True
            else:
                self.printText('수정할 ID를 확인해주세요. 0은 입력할 수 없습니다.')
                return False

    # 4. 객체 박스 각도 변경 버튼
    def changeAngle(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText('클립 경로를 설정하세요.')
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
            return False
        else:
            objId = self.ui.spinBoxfromIdchange_3.value()
            angle = self.ui.doubleSpinBox_4.value()
            try:
                angle = float(angle)
            except:
                self.printText('잘못된 각도입니다.')
                return False
            if angle > 360 or angle < 0:
                self.printText('잘못된 각도입니다.')
                return False
            if objId and angle>=0:
                frames, formerAngle = self.editLabel.changeAngle(objId, angle)
                self.printText('객체 id({})의 각도 변경 완료. {}˚ -> {}˚'.format(objId, formerAngle, angle))
                self.printText('객체 변경 프레임: \n{}'.format(frames))
                return True
            else:
                self.printText('객체 아이디 혹은 각도를 다시 확인해주세요.')
    
    def changeAngle180(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText('클립 경로를 설정하세요.')
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
            return False
        else:
            objId = self.ui.spinBoxfromIdchange_3.value()
            if objId:
                frames, curAngleDeg, changedAngleDeg = self.editLabel.changeAngle180(objId)
                self.printText('객체 id({})의 각도 변경 완료. {:.3f} -> {:.3f}'.format(objId, curAngleDeg, changedAngleDeg))
                self.printText('객체 변경 프레임: \n{}'.format(frames))
                return True
            else:
                self.printText('객체 아이디 혹은 각도를 다시 확인해주세요.')

    # # 5. 버그 아이디 변경 버튼
    # def changeBugId(self):
    #     if self.inputPath is None or os.path.isdir(self.resultPath) is False:
    #         self.printText('클립 경로를 설정하세요.')
    #         return
    #     else:
    #         maxId, ok2 = QInputDialog.getText(self, '버그 아이디 변경', '변경하지 않을 가장 큰 아이디를 입력하세요:')
    #         try:
    #             maxId = int(maxId)
    #         except:
    #             self.statusBarMessage('잘못된 아이디입니다.')
    #             return
    #         if ok2:
    #             self.printText('maxId: ', maxId)
    #             count = self.editLabel.changeBuggedId(maxId)

    #             self.statusBar().showMessage('크기 {} 이상의 버그 아이디 {}개를 변경 완료'.format(maxId, count))

    #6. 카테고리 수정
    def changeCategory(self)->bool:
        _CATEGORY = {1: 'CAR', 2: 'TRUCK', 3: 'PEDESTRIAN', 4: 'MOTORCYCLE', 
                      5: 'BUS', 6: 'BICYCLE', 7: 'ETC', 8:'MEDIAN_STRIP', 9:'SOUND_BARRIER', 10:'OVERPASS', 11:'RAMP_SECT', 12: 'ROAD_SIGN', 
                      13:'STREET_TREES', 14:'TURNNEL'}
        _OBJTYPE = {0: "동적객체", 1: "주행환경 객체"}
        
        if self.inputPath is None:
            self.printText('클립 경로를 설정하세요.')
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
            return False
        
        objId = self.ui.spinBoxfromIdCategory.value()
        
        objCategory = self.ui.comboBox.currentIndex()
            
        if objId and objCategory:
            # objCategory1 ~ 7: 동적객체(0), 8 ~ 14: 주행환경 객체(1)
            if objCategory < 8:
                objType = 0
            else:
                objType = 1
            frames = self.editLabel.changeCategory(objId, objType, _CATEGORY[objCategory])
            self.printText('객체 {}의 카테고리를 {}({})로 변경 완료'.format(objId, _OBJTYPE[objType], _CATEGORY[objCategory]))
            self.printText('카테고리 변경 프레임: {}'.format(frames))
            return True
        else:
            self.printText("객체 아이디 설정 및 카테고리 타입 설정을 다시 해주세요.")
        

    def wr_input(self):
        self.printText("잘못된 입력입니다.")
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
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
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
    
    # 9. 객체 복사 기능
    def copyObject(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText('클립 경로를 설정하세요.')
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText('result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.')
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
                self.printText("result폴더 내 파일 개수가 100를 초과합니다. 잘못된 파일이 없는지 확인하세요.")
                return False
            else:
                if self.editLabel.resultNum < 100:
                    self.autoMakeFiles()
                objId = self.ui.spinBoxfromIdchange_4.value()
                pickFrame = self.ui.spinBoxfromIdchange_5.value()
                startFrame = self.ui.spinBoxfromIdchange_6.value()
                endFrame = self.ui.spinBoxfromIdchange_7.value()
                
                messagebox = QMessageBox()
                messagebox.setWindowTitle('객체 붙여넣기 확인')
                messagebox.addButton(QPushButton('예'), QMessageBox.YesRole)
                messagebox.addButton(QPushButton('아니오'), QMessageBox.NoRole)
                messagebox.setText('프레임 범위 내에 같은 아이디의 객체 정보를 변경(붙여넣기)하시겠습니까?')
                button = messagebox.exec_()
                
                # button:0 예, 1 아니오
                if button == 0:
                    isChange, ok = 1, True
                elif button == 1:
                    isChange, ok = 0, True
                else:
                    ok = False
                    
                try:
                    #chage ischange to bool
                    isChange = bool(int(isChange))
                except:
                    self.printText("잘못된 입력입니다.")
                    return False

                if objId and pickFrame and startFrame and endFrame and ok:
                    frame_copy, frame_paste = self.editLabel.copyObject(objId, pickFrame, startFrame, endFrame, isChange)
                    self.printText('복사 객체 id: {} 프레임: {} ~ {}'.format(objId, startFrame, endFrame))
                    self.printText('객체 복사된 프레임: {}'.format(frame_copy))
                    self.printText('객체 붙여넣기된 프레임: {}'.format(frame_paste))
                    self.printText('객체 복사 완료')
                    return True

    # 10. 객체 삭제 기능
    def removeObj(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return False
        obj = {'id': self.ui.spinBoxfromIdchange_9.value(),
               'startFrame': self.ui.spinBoxfromIdchange_10.value(),
               'endFrame': self.ui.spinBoxfromIdchange_11.value(),}
        
        removed_frames = self.editLabel.removeObj(obj)
        self.printText(f'객체 삭제된 프레임 : {removed_frames}')
        self.printText('선택한 객체 삭제 완료')
                        
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

    def statusBarMessage(self, *args):
        # change tuple to string
        message = ' '.join(args)
        now = datetime.now()
        if message:
            self.statusBar().showMessage(f'[{now.time():%H:%M:%S}] ' + message)
        else:
            self.statusBar().showMessage(f'[{now.time():%H:%M:%S}] ' + "경로를 설정해주세요")
    
    def printText(self, *args):
        r'''
        *args: string in tuple
        '''
        messageList = []
        for arg in args:
            # check if arg is int or float
            if isinstance(arg, int) or isinstance(arg, float):
                messageList.append(str(arg))
            else:
                messageList.append(arg)
        
        message = ' '.join(messageList)
        now = datetime.now()
        if message:
            self.ui.textBrowser.append(f'[{now.time():%H:%M:%S}] ' + message)
        print(f'[{now.time():%H:%M:%S}] ' + message)
        
    
    def checkIfFileRefreshedOld(self):
        root_path = os.path.dirname(self.editLabel.clipPath)
        clips_path = glob.glob(os.path.join(root_path, '*', '*'))

        for clip in clips_path:
            start = time.time()
            clip_num = os.path.basename(clip).replace('Clip_', '')
            
            # calib 체크
            lc_cal_dist = os.path.join(clip, 'calib', 'Lidar_camera_calib',
                                    f'2-048_{clip_num}_LCC_CF.txt')
            lr_cal_dist = os.path.join(clip, 'Calib', 'Lidar_radar_calib', 
                                    f'2-048_{clip_num}_LRC_RF.txt')
            
            # 카메라, 라이다, 레이다 체크
            camera_dist = [os.path.join(clip, 'Camera', 'CameraFront', 'blur',
                                        f'2-048_{clip_num}_CF_{str(i):0>3s}.png')
                        for i in range(1, 101)]
            lidar_dist = [os.path.join(clip, 'Lidar',
                                    f'2-048_{clip_num}_LR_{str(i):0>3s}.pcd')
                        for i in range(1, 101)]
            radar_dist = [os.path.join(clip, 'Radar', 'RadarFront',
                                    f'2-048_{clip_num}_RF_{str(i):0>3s}.pcd')
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
        
    def checkresult(self):
        self.printText('지정된 경로를 확인합니다.')
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return False
        self.printText(f'클립 경로 : {self.inputPath}')
        self.printText(f'클립 내 폴더 목록 : {os.listdir(self.inputPath)}')
        if os.path.isdir(self.editLabel.resultPath):
            if len(self.editLabel.resultList) > 0:
                self.printText(f'result 폴더 내 파일 개수: {self.editLabel.resultNum}')
                self.printText('첫 프레임 객체 정보:')
                frameNum_first = self.editLabel[0]['frame_no'] # 첫 프레임 번호
                objNum_first = len(self.editLabel[0]['annotation']) # 첫 프레임 객체 수
                self.printText(f'첫 프레임 번호 : {frameNum_first}')
                self.printText(f'첫 프레임 객체 수 : {objNum_first}')
                self.printText('첫 프레임 객체 정보 : ')
                for obj in self.editLabel[0]['annotation']:
                    self.printText(f'ID : {obj["id"]}')
                    self.printText(f'카테고리 : {obj["category"]}')
                    for box in obj['3d_box']:
                        self.printText(f'박스 크기(width, height, length) : {box["dimension"][0]:.3f}, {box["dimension"][1]:.3f}, {box["dimension"][2]:.3f} sub_id: {box["sub_id"]}')
                    
                if self.editLabel.resultNum > 1:
                    frameNum_last = self.editLabel[-1]['frame_no'] # 마지막 프레임 번호
                    objNum_last = len(self.editLabel[-1]['annotation']) # 마지막 프레임 객체 수
                    self.printText(f'마지막 프레임 번호 : {frameNum_last}')
                    self.printText(f'마지막 프레임 객체 수 : {objNum_last}')
                    self.printText('마지막 프레임 객체 정보 : ')
                    for obj in self.editLabel[-1]['annotation']:
                        self.printText(f'ID : {obj["id"]}')
                        self.printText(f'카테고리 : {obj["category"]}')
                        for box in obj['3d_box']:
                            self.printText(f'박스 크기(width, height, length) : {box["dimension"][0]:.3f}, {box["dimension"][1]:.3f}, {box["dimension"][2]:.3f} sub_id: {box["sub_id"]}')
            else:
                self.printText('result 폴더 내 파일 개수: 0')
        else:
            self.printText('result 폴더가 없습니다.')
        
        self.printText('확인 완료')
        
        
    def extractZip(self):
        try:
            with zipfile.ZipFile(self.editLabel.clipPath + '/result.zip', 'r') as zip_ref:
                zip_ref.extractall(self.editLabel.clipPath + '/result')
            self.editLabel.setPath(self.editLabel.clipPath)
            self.printText('압축 풀기 완료')
        except:
            self.printText('압축 풀기 실패')
            self.printText('해당 클립 폴더 내에 result.zip 파일이 없습니다.')
    
    def openCurrentFolder(self):
        if self.inputPath is None:
            self.statusBarMessage('클립 경로를 설정하세요.')
            self.printText('클립 경로를 설정하세요.')
            return False
        else:
            os.startfile(self.inputPath)
            self.printText('현재 클립 경로로 이동')
    

    def mainWindow(self):
        self.center()
        self.ui.pushButton_4.clicked.connect(self.openFolder)               # 클립 폴더 열기
        self.ui.pushButton_15.clicked.connect(self.checkresult)             # result 폴더 확인
        self.ui.pushButton_11.clicked.connect(self.checkObjectId)           # 객체 아이디 체크
        self.ui.pushButton_5.clicked.connect(self.backup)                   # result 백업
        self.ui.pushButton_6.clicked.connect(self.restore)                  # result 복원
        self.ui.pushButton_10.clicked.connect(self.changeObjectId)          # 객체 아이디 변경
        self.ui.pushButton_9.clicked.connect(self.changeCategory)           # 카테고리 변경
        self.ui.pushButton.clicked.connect(self.changeDimension)            # 크기 변경
        self.ui.pushButton_7.clicked.connect(self.changeAngle)              # 각도 변경
        self.ui.pushButton_16.clicked.connect(self.changeAngle180)              # 압축 풀기
        self.ui.pushButton_8.clicked.connect(self.copyObject)               # 객체 복사
        self.ui.pushButton_3.clicked.connect(self.refreshFileName)          # 폴더명 최신화
        self.ui.pushButton_2.clicked.connect(self.autoMakeFiles)            # result 빈 파일 자동 생성
        self.ui.pushButton_13.clicked.connect(self.checkIfFileRefreshedOld) # 파일 새로고침 체크
        # self.ui.pushButton_12.clicked.connect(self.autoMakeFilesOld)
        self.ui.pushButton_14.clicked.connect(self.extractZip)              # 압축 풀기
        self.ui.pushButton_17.clicked.connect(self.openCurrentFolder)       # 현재 클립 경로 열기
        self.ui.pushButton_18.clicked.connect(self.removeObj)               # 객체 제거
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())