import sys
import zipfile
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QInputDialog, QDesktopWidget, QFileDialog, QMessageBox, QPushButton
from editLabel import EditLabel
from analyzeLabel import AnalyzeLabel
from pyqtDesign.pyqtDesigner import Ui_MainWindow
from datetime import datetime

import glob
import json
import os
import time
import numpy as np

now = datetime.now()

WRONG_PATH_MESSAGE = '잘못된 경로입니다. 경로를 다시 설정해주세요.'
WRONG_CLIP_MESSAGE = '클립 경로를 설정하세요.'
NO_RESULT_FOLDER_MESSAGE = 'result 폴더가 없습니다. 라벨링 파일을 담은 정상적인 result 폴더를 생성해주세요.'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.saveOpendFolder = './'
        self.pathInit()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.statusBarMessage()
        self.mainWindow()

    def pathInit(self, input_path=None):
        self.inputPath = None
        self.clipPath = None
        self.upperPath = None

        if input_path:
            base_path = os.path.basename(input_path)

            if base_path == 'result':
                self.inputPath = input_path
                self.clipPath = os.path.dirname(input_path)
                self.upperPath = os.path.dirname(self.clipPath)

    # 6. 불러오기 확인
    def checkLoadingFiles(self) -> bool:
        if self.inputPath is None:
            self.statusBarMessage(WRONG_CLIP_MESSAGE)
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        else:
            self.editLabel.set_path(self.inputPath)
            file_list = self.editLabel.get_result_list()
            self.printText("파일 개수 : {}".format(len(file_list)))
            with open(file_list[0], 'r') as f:
                json_data = json.load(f)  # json 데이터 불러옴
                self.printText(json_data)
                self.printText("파일 불러오기 성공")
            return True

    # result 폴더 경로 설정
    def openFolder(self):
        path = str(QFileDialog.getExistingDirectory(
            self, 'Open Folder', self.saveOpendFolder))

        try:
            if(path == '' or path == None):
                self.printText(WRONG_PATH_MESSAGE)
                if not self.inputPath:
                    self.statusBar().showMessage(WRONG_PATH_MESSAGE)
            else:
                self.saveOpendFolder = path  # 다음 폴더 열기 경로 저장
                self.inputPath = path
                self.resultPath = path + r'\result'
                self.editLabel = EditLabel(self.inputPath)
                self.analyzeLabel = AnalyzeLabel(self.inputPath)
                self.printText('****************폴더 경로 설정 완료.')
                self.printText(f'클립 경로 {self.inputPath}에서 작업을 시작합니다.')
                if not os.path.isdir(self.resultPath):
                    self.printText(NO_RESULT_FOLDER_MESSAGE)
                self.statusBar().showMessage(
                    f'클립 경로 {self.inputPath}에서 작업을 시작합니다.')

        except:
            self.printText(WRONG_PATH_MESSAGE)
            self.statusBar().showMessage(WRONG_PATH_MESSAGE)

    # 파일명 일괄 수정
    def refreshFileName(self):
        extract_path = self.ui.lineEdit.text()

        if extract_path:
            self.analyzeLabel = AnalyzeLabel(extract_path=extract_path)
            clip_path_list = glob.glob(self.analyzeLabel.extract_path + r'\*')
            clip_path_list.sort()
            # clipPathList에서 Clip 폴더만 추출
            clip_path_list = [
                clipPath for clipPath in clip_path_list if 'Clip' in clipPath and os.path.isdir(clipPath)]
            self.analyzeLabel.clipPath_list = clip_path_list

            for clip in clip_path_list:
                self.analyzeLabel.fix_filenames(clip)
            # self.editLabel.setPath(self.inputPath) # result 경로 파일 목록 새로고침
            self.printText('파일명 일괄 수정 완료')
            self.printText(
                '----------------------------------------------------')
        else:
            self.printText('잘못된 경로입니다. 클립 경로로 다시 설정해주세요.')
            self.statusBar().showMessage('잘못된 경로입니다. 클립 경로로 다시 설정해주세요.')

    def __center(self):
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
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False
        else:
            self.printText('백업 시작')
            backup_file_num, backup_file_list = self.editLabel.make_backup()
            for idx, backup_file in enumerate(backup_file_list):
                self.printText(
                    f'{idx+1}/{backup_file_num} {backup_file} 백업 완료')
            self.printText(f'{backup_file_num}개 파일 백업 완료')
            return True

    def restore(self):
        if self.inputPath is None:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.editLabel.backupfolder) is False:
            self.printText('백업 폴더가 없습니다. 백업 폴더를 확인해주세요.')
        else:
            self.printText('파일 복원 시작')
            count, cur_file_list = self.editLabel.restore_backup()
            if count == 0:
                self.printText('백업할 파일이 없습니다.')
            else:
                for idx, cur_file in enumerate(cur_file_list):
                    self.printText(f'{idx+1}/{count} {cur_file} 복원 완료')
                self.printText('{}개 파일 복원 완료'.format(count))

    # 1. 객체 아이디 확인
    def check_object_id(self):
        if self.inputPath is None:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
        else:
            obj_id = self.ui.spinBoxfromIdchange_2.value()

            if obj_id:
                frame_id_exist = self.editLabel.check_object_id(obj_id)
                unique_frame_num = len(np.unique(frame_id_exist))
                if frame_id_exist:
                    if len(frame_id_exist) >= 100:
                        # unique frame_id 출력

                        self.printText(
                            f'객체 id {obj_id}가 프레임 {frame_id_exist[0]} ~ {frame_id_exist[-1]} 사이 {unique_frame_num}개의 프레임에 {len(frame_id_exist)}개 있습니다.')
                    else:
                        self.printText(
                            f'객체 id {obj_id}가 프레임 {frame_id_exist}에 {len(frame_id_exist)}개 있습니다.')

                    self.printText(
                        f'프레임 {frame_id_exist[0]} 내 객체 id {obj_id}의 정보:')
                    firstframe = frame_id_exist[0]
                    for obj in self.editLabel[firstframe]['annotation']:
                        if int(obj['id']) == obj_id:
                            self.printText(f'{obj}')
                            continue
                else:
                    self.printText(f'객체 id {obj_id}가 존재하지 않습니다.')
            else:
                self.printText('잘못된 객체 아이디입니다.')

    # 2. 객체 아이디 변경 버튼

    def changeObjectId(self):
        if self.inputPath is None:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
        else:
            obj_id = self.ui.spinBoxfromIdchange.value()
            changed_id = self.ui.spinBoxToIdchange.value()
            if obj_id and changed_id:
                frames = self.editLabel.change_id(obj_id, changed_id)
                self.printText(f'객체 아이디 변경. {obj_id} -> {changed_id}')
                self.printText(f'객체 변경 프레임: \n{frames}')
            else:
                self.printText('수정할 ID나 변경될 ID를 확인해주세요. 0은 입력할 수 없습니다.')

    # 3. 객체 박스 크기 변경 버튼
    def changeDimension(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False
        else:
            obj_id = self.ui.spinBoxfromIdchange_3.value()
            width = self.ui.doubleSpinBox.value()
            height = self.ui.doubleSpinBox_2.value()
            length = self.ui.doubleSpinBox_3.value()
            if obj_id:
                box, frames = self.editLabel.change_dim(
                    obj_id, width, height, length, os.path.basename(self.inputPath)) # 2022-12-14 클립명 추가
                self.printText(
                    f'ID: {obj_id}의 크기를 (width:{box[0]:.03f}, height:{box[1]:.03f}, length:{box[2]:.03f})로 변경 완료')
                self.printText(f'객체 변경 프레임: \n{frames}')
                print("----------------------------------------------------")
                return True
            else:
                self.printText('수정할 ID를 확인해주세요. 0은 입력할 수 없습니다.')
                return False

    # 4. 객체 박스 각도 변경 버튼
    def changeAngle(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False
        else:
            obj_id = self.ui.spinBoxfromIdchange_3.value()
            angle = self.ui.doubleSpinBox_4.value()
            try:
                angle = float(angle)
            except ValueError:
                self.printText('잘못된 각도입니다.')
                return False
            if angle > 360 or angle < 0:
                self.printText('잘못된 각도입니다.')
                return False
            if obj_id and angle >= 0:
                frames, former_angle = self.editLabel.change_angle(
                    obj_id, angle)
                self.printText(
                    '객체 id({})의 각도 변경 완료. {}˚ -> {}˚'.format(obj_id, former_angle, angle))
                self.printText('객체 변경 프레임: \n{}'.format(frames))
                return True
            else:
                self.printText('객체 아이디 혹은 각도를 다시 확인해주세요.')

    def changeAngle180(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False
        else:
            obj_id = self.ui.spinBoxfromIdchange_3.value()
            if obj_id:
                frames, cur_angle_degree, changed_angle_degree = self.editLabel.change_angle180(
                    obj_id)
                self.printText('객체 id({})의 각도 변경 완료. {:.3f} -> {:.3f}'.format(
                    obj_id, cur_angle_degree, changed_angle_degree))
                self.printText('객체 변경 프레임: \n{}'.format(frames))
                return True
            else:
                self.printText('객체 아이디 혹은 각도를 다시 확인해주세요.')

    # 6. 카테고리 수정
    def changeCategory(self) -> bool:
        _CATEGORY = {1: 'CAR', 2: 'TRUCK', 3: 'PEDESTRIAN', 4: 'MOTORCYCLE',
                     5: 'BUS', 6: 'BICYCLE', 7: 'ETC', 8: 'MEDIAN_STRIP', 9: 'SOUND_BARRIER', 10: 'OVERPASS', 11: 'RAMP_SECT', 12: 'ROAD_SIGN',
                     13: 'STREET_TREES', 14: 'TURNNEL'}
        _OBJTYPE = {0: "동적객체", 1: "주행환경 객체"}

        if self.inputPath is None:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False

        obj_id = self.ui.spinBoxfromIdCategory.value()
        obj_category = self.ui.comboBox.currentIndex()

        if obj_id and obj_category:
            # objCategory1 ~ 7: 동적객체(0), 8 ~ 14: 주행환경 객체(1)
            if obj_category < 8:
                obj_type = 0
            else:
                obj_type = 1
            frames = self.editLabel.change_category(obj_id, obj_type, _CATEGORY[obj_category])
            self.printText('객체 {}의 카테고리를 {}({})로 변경 완료'.format(
                obj_id, _OBJTYPE[obj_type], _CATEGORY[obj_category]))
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
            self.statusBarMessage(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False
        else:
            file_list = self.editLabel.result_list
            try:
                first_file = file_list[0]
            except IndexError:
                self.printText('result 폴더에 라벨링 파일이 없습니다.')
                self.printText("파일 구성이 잘못되었거나 json파일이 없습니다.")
                self.statusBarMessage('파일 구성이 잘못되었거나 json파일이 없습니다.')
            extra_file_name = '_'.join(first_file.split('_')[:-1])
            for idx in range(1, 100 + 1):
                cur_file = r'{}_{:03d}.json'.format(extra_file_name, idx)
                old_file = r'{}_{:04d}.json'.format(extra_file_name, idx)
                if os.path.isfile(old_file):
                    os.rename(old_file, cur_file)
                    self.printText(
                        "파일명을 {}에서 \n{}로 변경하였습니다.".format(old_file, cur_file))
                    continue
                if os.path.isfile(cur_file):
                    continue
                else:
                    json_data = {"frame_no": idx, "annotation": []}
                    with open(cur_file, 'w') as f:
                        json.dump(json_data, f, indent=4)
                        self.printText('{} 파일 생성 완료'.format(cur_file))
        self.editLabel.set_path(self.inputPath)
        self.printText('----------------------------------------------------')
        return True

    # 9. 객체 복사 기능
    def copy_object(self):
        if self.inputPath is None or os.path.isdir(self.resultPath) is False:
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        elif os.path.isdir(self.resultPath) is False:
            self.printText(NO_RESULT_FOLDER_MESSAGE)
            return False
        else:
            self.printText("복사 기능 사용 전에 백업을 권장합니다.")
            self.editLabel.set_path(self.inputPath)

            if self.editLabel.result_num > 100:
                self.printText(
                    "result폴더 내 파일 개수가 100를 초과합니다. 잘못된 파일이 없는지 확인하세요.")
                return False
            else:
                if self.editLabel.result_num < 100:
                    self.autoMakeFiles()
                obj_id = self.ui.spinBoxfromIdchange_4.value()
                pick_frame = self.ui.spinBoxfromIdchange_5.value()
                start_frame = self.ui.spinBoxfromIdchange_6.value()
                end_frame = self.ui.spinBoxfromIdchange_7.value()

                messagebox = QMessageBox()
                messagebox.setWindowTitle('객체 붙여넣기 확인')
                messagebox.addButton(QPushButton('예'), QMessageBox.YesRole)
                messagebox.addButton(QPushButton('아니오'), QMessageBox.NoRole)
                messagebox.setText('프레임 범위 내에 같은 아이디의 객체 정보를 변경(붙여넣기)하시겠습니까?')
                button = messagebox.exec_()

                # button:0 예, 1 아니오
                if button == 0:
                    is_change, ok = 1, True
                elif button == 1:
                    is_change, ok = 0, True
                else:
                    ok = False

                try:
                    # chage ischange to bool
                    is_change = bool(int(is_change))
                except:
                    self.printText("잘못된 입력입니다.")
                    return False

                if obj_id and pick_frame and start_frame and end_frame and ok:
                    frame_copy, frame_paste = self.editLabel.copy_object(
                        obj_id, pick_frame, start_frame, end_frame, is_change)
                    self.printText('복사 객체 id: {} 프레임: {} ~ {}'.format(
                        obj_id, start_frame, end_frame))
                    self.printText('객체 복사된 프레임: {}'.format(frame_copy))
                    self.printText('객체 붙여넣기된 프레임: {}'.format(frame_paste))
                    self.printText('객체 복사 완료')
                    return True

    # 10. 객체 삭제 기능
    def removeObj(self):
        if self.inputPath is None:  # 클립 경로 미설정
            self.statusBarMessage(WRONG_CLIP_MESSAGE)
            self.printText(WRONG_CLIP_MESSAGE)
            return False

        obj = {'id': self.ui.spinBoxfromIdchange_9.value(),  # obj 사전에 객체 수정 정보 저장
               'startFrame': self.ui.spinBoxfromIdchange_10.value(),
               'endFrame': self.ui.spinBoxfromIdchange_11.value(), }

        messagebox = QMessageBox()  # 삭제 진행 여부 확인 메시지 박스
        messagebox.setWindowTitle(f'객체 {obj["id"]} 삭제 여부 확인')
        messagebox.addButton(QPushButton('예'), QMessageBox.YesRole)
        messagebox.addButton(QPushButton('아니오'), QMessageBox.NoRole)
        messagebox.setText(
            f'{obj["startFrame"]} ~ {obj["endFrame"]} 프레임 범위 내 객체 ID({obj["id"]}) 삭제를 진행하시겠습니까?')
        button = messagebox.exec_()  # button:0 예, 1: 아니오

        if button == 0:
            removed_frames = self.editLabel.remove_obj(obj)
        else:
            self.printText("객체 삭제를 취소했습니다.")
            return False

        if not removed_frames:
            self.printText('객체 아이디가 0보다 커야합니다.')
            return False

        self.printText(f'객체 삭제된 프레임 : {removed_frames}')
        self.printText('선택한 객체 삭제 완료')

    # 10. 파일명 통일 기능 버튼 생성
    def rename_result_files(self):
        if self.inputPath is None:
            self.statusBarMessage(WRONG_CLIP_MESSAGE)
            self.printText(WRONG_CLIP_MESSAGE)
            return False

    def statusBarMessage(self, *args):
        r'''
            args: (str, int) 입력된 변수들을 텍스트 창에 출력
        '''
        # change tuple to string
        message = ' '.join(args)
        now = datetime.now()  # 출력된 시간
        if message:
            self.statusBar().showMessage(f'[{now.time():%H:%M:%S}] ' + message)
        else:
            self.statusBar().showMessage(
                f'[{now.time():%H:%M:%S}] ' + "경로를 설정해주세요")

    def printText(self, *args):
        r'''
        *args: string in tuple
        '''
        message_list = []
        for arg in args:
            # check if arg is int or float
            if isinstance(arg, int) or isinstance(arg, float):
                message_list.append(str(arg))
            else:
                message_list.append(arg)

        message = ' '.join(message_list)
        now = datetime.now()
        if message:
            self.ui.textBrowser.append(f'[{now.time():%H:%M:%S}] ' + message)
        print(f'[{now.time():%H:%M:%S}] ' + message)

    def checkIfFileRefreshedOld(self):
        root_path = os.path.dirname(self.editLabel.clip_path)
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

            print(
                f'{clip} : {lc_cal} {lr_cal} {all(c)} {all(l)} {all(r)} [{elapsed:.4f} s]')
        print(f'dir : lidar_camera cal / lidar_radar cal / cam / lidar / radar')
        print(f'all clips checked')

    def checkresult(self):
        self.printText('지정된 경로를 확인합니다.')
        if self.inputPath is None:
            self.statusBarMessage(WRONG_CLIP_MESSAGE)
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        self.printText(f'클립 경로 : {self.inputPath}')
        self.printText(f'클립 내 폴더 목록 : {os.listdir(self.inputPath)}')
        if os.path.isdir(self.editLabel.result_path):
            if len(self.editLabel.result_list) > 0:
                self.printText(
                    f'result 폴더 내 파일 개수: {self.editLabel.result_num}')
                self.printText('첫 프레임 객체 정보:')
                frame_num_first = self.editLabel[0]['frame_no']  # 첫 프레임 번호
                obj_num_first = len(
                    self.editLabel[0]['annotation'])  # 첫 프레임 객체 수
                self.printText(f'첫 프레임 번호 : {frame_num_first}')
                self.printText(f'첫 프레임 객체 수 : {obj_num_first}')
                self.printText('첫 프레임 객체 정보 : ')
                for obj in self.editLabel[0]['annotation']:
                    self.printText(f'ID : {obj["id"]}')
                    self.printText(f'카테고리 : {obj["category"]}')
                    for box in obj['3d_box']:
                        self.printText(
                            f'박스 크기(width, height, length) : {box["dimension"][0]:.3f}, {box["dimension"][1]:.3f}, {box["dimension"][2]:.3f} sub_id: {box["sub_id"]}')

                if self.editLabel.result_num > 1:
                    # 마지막 프레임 번호
                    frame_num_last = self.editLabel[-1]['frame_no']
                    obj_num_last = len(
                        self.editLabel[-1]['annotation'])  # 마지막 프레임 객체 수
                    self.printText(f'마지막 프레임 번호 : {frame_num_last}')
                    self.printText(f'마지막 프레임 객체 수 : {obj_num_last}')
                    self.printText('마지막 프레임 객체 정보 : ')
                    for obj in self.editLabel[-1]['annotation']:
                        self.printText(f'ID : {obj["id"]}')
                        self.printText(f'카테고리 : {obj["category"]}')
                        for box in obj['3d_box']:
                            self.printText(
                                f'박스 크기(width, height, length) : {box["dimension"][0]:.3f}, {box["dimension"][1]:.3f}, {box["dimension"][2]:.3f} sub_id: {box["sub_id"]}')
            else:
                self.printText('result 폴더 내 파일 개수: 0')
        else:
            self.printText('result 폴더가 없습니다.')

        self.printText('확인 완료')

    def extractZip(self):
        try:
            with zipfile.ZipFile(self.editLabel.clip_path + '/result.zip', 'r') as zip_ref:
                zip_ref.extractall(self.editLabel.clip_path)
            self.editLabel.set_path(self.editLabel.clip_path)
            self.printText('압축 풀기 완료')
        except FileNotFoundError:
            self.printText('압축 풀기 실패')
            self.printText('해당 클립 폴더 내에 result.zip 파일이 없습니다.')

    def openCurrentFolder(self):
        if self.inputPath is None:
            self.statusBarMessage(WRONG_CLIP_MESSAGE)
            self.printText(WRONG_CLIP_MESSAGE)
            return False
        else:
            os.startfile(self.inputPath)
            self.printText('현재 클립 경로로 이동')

    def mainWindow(self):
        self.__center()
        self.ui.pushButton_4.clicked.connect(
            self.openFolder)               # 클립 폴더 열기
        self.ui.pushButton_15.clicked.connect(
            self.checkresult)             # result 폴더 확인
        self.ui.pushButton_11.clicked.connect(
            self.check_object_id)           # 객체 아이디 체크
        self.ui.pushButton_5.clicked.connect(
            self.backup)                   # result 백업
        self.ui.pushButton_6.clicked.connect(
            self.restore)                  # result 복원
        self.ui.pushButton_10.clicked.connect(
            self.changeObjectId)          # 객체 아이디 변경
        self.ui.pushButton_9.clicked.connect(
            self.changeCategory)           # 카테고리 변경
        self.ui.pushButton.clicked.connect(
            self.changeDimension)            # 크기 변경
        self.ui.pushButton_7.clicked.connect(
            self.changeAngle)              # 각도 변경
        self.ui.pushButton_16.clicked.connect(
            self.changeAngle180)              # 압축 풀기
        self.ui.pushButton_8.clicked.connect(
            self.copy_object)               # 객체 복사
        self.ui.pushButton_3.clicked.connect(
            self.refreshFileName)          # 폴더명 최신화
        self.ui.pushButton_2.clicked.connect(
            self.autoMakeFiles)            # result 빈 파일 자동 생성
        self.ui.pushButton_13.clicked.connect(
            self.checkIfFileRefreshedOld)  # 파일 새로고침 체크
        # self.ui.pushButton_12.clicked.connect(self.autoMakeFilesOld)
        self.ui.pushButton_14.clicked.connect(
            self.extractZip)              # 압축 풀기
        self.ui.pushButton_17.clicked.connect(
            self.openCurrentFolder)       # 현재 클립 경로 열기
        self.ui.pushButton_18.clicked.connect(
            self.removeObj)               # 객체 제거


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
