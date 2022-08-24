import os
import json
import glob
import pandas as pd
import numpy as np
from datetime import date

PASS = 0
REJECT = -1

CATEGORY_D = ["BICYCLE", "CAR", "BUS", "ETC", "MOTORCYCLE", "PEDESTRIAN", "TRUCK"]
CATEGORY_S = ["MEDIAN_STRIP", "OVERPASS", "RAMPSECT", "ROAD_SIGN", "SOUND_BARRIER", "STREET_TREES", "TUNNEL"]
CATEGORY_ATYP = ["MEDIAN_STRIP", "OVERPASS", "RAMPSECT", "SOUND_BARRIER", "TUNNEL"]

CATEGORY_CAR = ["CAR", "BUS", "ETC", "TRUCK"]


COLUMNS = ["clip 이름", "프레임 번호", "객체 id", "반려사유"]
SUM_COL = ["clip 이름", "검수결과", "반려사유"]

FILE_NUM_ERROR, FRAME_ERROR, CATEGORY_ERROR, ATYP_ERROR, LOC_ERROR, PCD_ERROR, POLYGON_ERROR, DIM_ERROR, GROUP_ERROR, SCENCE_ERROR = list(range(1,11))

dic = {
    PASS: "통과",
    REJECT: "반려",                     
    
    FILE_NUM_ERROR: "프레임 개수 오류",     ##  .json 파일 개수 부족
    FRAME_ERROR: "빈 프레임 확인필요",      ##  프레임에 아무 객체도 없음
    CATEGORY_ERROR: "동적/주행환경 오류",   ##  category가 동적인데 주행환경이라고 함
    ATYP_ERROR: "비정형/정형 오류",         ##  category가 정형인데 비정형이라고 함
    LOC_ERROR: "박스 위치 오류",            ##  가공 범위 밖에 박스를 생성함
    PCD_ERROR: "PCD 부족 오류",             ##  빈 곳에 박스를 생성함
    POLYGON_ERROR: "폴리곤 미작업",         ##  비정형인데 폴리곤을 생성하지 않음
    DIM_ERROR: "박스 크기 오류",            ##  크기가 부적합 (차량과 나머지만 구분)
    GROUP_ERROR: "그룹화 오류",             ##  정형인데 분리라벨링
    SCENCE_ERROR: "시나리오 오류"           ##  동적 시나리오인데 주행환경객체가 존재함
}


class ErrorLogger:
    
    def __init__(self, clip_name):
        
        self.clip_name = clip_name
        self.is_reject = PASS
        self.err_type = []
        self.err_logging = pd.DataFrame(columns=COLUMNS)
    
    def set_clip_name(self, name):
        self.clip_name = name
    def set_reject(self, reject):
        self.is_reject = reject
        
    def add_err_type(self, err):
        self.err_type.append(err)
    def add_err_log(self, frame, object_id, err_type):
        row = [[self.get_clip_name(), frame, object_id, dic.get(err_type)]]
        l = pd.DataFrame(row, columns=COLUMNS)
        self.err_logging = pd.concat([self.get_err_log(), l], ignore_index=True)
        self.set_reject(REJECT)
        self.add_err_type(err_type)
        del l
    def add_pass_log(self):
        row = [[self.get_clip_name(), -1, -1, dic.get(PASS)]]
        l = pd.DataFrame(row, columns=COLUMNS)
        self.err_logging = pd.concat([self.get_err_log(), l], ignore_index=True)
        self.set_reject(PASS)
        self.add_err_type(PASS)
        del l
    
        
    def get_clip_name(self):
        return self.clip_name
    def get_reject(self):
        return self.is_reject
    def get_err_type(self):
        return set(self.err_type)
    def get_err_log(self):
        return self.err_logging
    
    def get_summary(self):
        root_clip = self.get_clip_name()
        res = dic.get(self.get_reject())
        
        err_type_list = list(self.get_err_type())
        err_type_list.sort()
        
        for i in range(len(err_type_list)):
            tmp = dic.get(err_type_list[i])
            err_type_list[i] = tmp
        err_type = ', '.join(err_type_list)
        row = [[root_clip, res, err_type]]
        ret = pd.DataFrame(row, columns=SUM_COL)
        return ret

class RejectModule:
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.curr_clip = ""
        self.rejecter_name = ""
        self.reject_date = date.today().isoformat()
        
    def set_base_path(self, base_path):
        self.base_path = base_path
    def set_curr_clip(self, clip):
        self.curr_clip = clip
    def set_rejecter_name(self, name):
        self.rejecter_name
    
    def get_base_path(self):
        return self.base_path
    def get_curr_clip(self):
        return self.curr_clip
    def get_rejecter_name(self):
        return self.rejecter_name
    def get_reject_date(self):
        return self.reject_date
    
    
    def get_scene(self, clip):
        ## 클립명에서 목표 객체 (동적or주행환경) 추출
        ## 0: 동적, 1: 주행환경
        cat_code = int(clip[-2:])
        if cat_code < 10:
            return 0
        else:
            return 1

    def rej_single_res(self, base_path, clip):
        err_logger = ErrorLogger(clip)
        res = glob.glob(f'{base_path}/{clip}/*')
        scene_type = self.get_scene(clip) 
        
        if len(res) < 100: 
            print(f"{clip} reject labeling: not enough json number")
            err_logger.add_err_log(-1, -1, FILE_NUM_ERROR)
            return err_logger
        
        for r in res:
            with open(r, "r") as f:
                data = json.load(f)
                fnum = data["frame_no"]
                annot = data["annotation"]
                
                if annot == []:
                    print(f"{clip}: frame {fnum}: is empty")
                    err_logger.add_err_log(fnum, -1, FRAME_ERROR)
                    
                for obj in annot:
                    id = obj["id"]
                    cat = obj["category"]
                    type = obj["obj_type"]
                    is_atyp = obj["atypical_yn"]
                    box_list = obj["3d_box"]
                    # cam_vis = obj["camera_visibility"]
                    polygon = obj["2d_polygon"]
                    if type==0:
                        if cat not in CATEGORY_D: 
                            print(f"{clip}: frame {fnum}: object {id}: wrong category")
                            err_logger.add_err_log(fnum, id, CATEGORY_ERROR)
                    else:
                        if cat not in CATEGORY_S:
                            print(f"{clip}: frame {fnum}: object {id}: wrong category")
                            err_logger.add_err_log(fnum, id, CATEGORY_ERROR)
                    # if type != scene_type:
                    #     print(f"{clip}: frame {fnum}: object {id}: wrong type")
                    #     err_logger.add_err_log(fnum, id, SCENCE_ERROR)
                        
                            
                    if (cat in CATEGORY_ATYP): 
                        if is_atyp=="n":
                            print(f"{clip}: frame {fnum}: object {id}: wrong atypical_yn")
                            err_logger.add_err_log(fnum, id, ATYP_ERROR)
                        # else:
                        #     if polygon == []:
                        #         print(f"{clip}: frame {fnum}: object {id}: lack of polygon")
                        #         err_logger.add_err_log(fnum, id, POLYGON_ERROR)
                    else: 
                        if is_atyp=="y":
                            print(f"{clip}: frame {fnum}: object {id}: wrong atypical_yn")
                            err_logger.add_err_log(fnum, id, ATYP_ERROR)
                        
                        if len(box_list) > 1:
                            print(f"{clip}: frame {fnum}: object {id}: shoud not be multi_boxed")
                            err_logger.add_err_log(fnum, id, GROUP_ERROR)
                            
                        
                    for box in box_list:
                        loc = box["location"]
                        pcd_cnt = box["lidar_point_count"] + box["radar_point_count"]
                        dim = box["dimension"]
                        
                        if loc[0] < 0:
                            print(f"{clip}: frame {fnum}: object {id}: wrong location")
                            err_logger.add_err_log(fnum, id, LOC_ERROR)    
                        
                            
                        if pcd_cnt < 3:
                            print(f"{clip}: frame {fnum} object {id} lack of point cloud")
                            err_logger.add_err_log(fnum, id, PCD_ERROR)
                        
                        if cat in CATEGORY_D:
                            x_dim = dim[0]
                            y_dim = dim[1]    
                            if cat in CATEGORY_CAR:
                            ## dimension
                                if x_dim < 2 and y_dim < 1:
                                    print(f"{clip}: frame {fnum} object {id} dimension error")
                                    err_logger.add_err_log(fnum, id, DIM_ERROR)
                                pass
                            else:
                                if x_dim > 2 and y_dim > 1:
                                    print(f"{clip}: frame {fnum} object {id} dimension error")
                                    err_logger.add_err_log(fnum, id, DIM_ERROR)
                                pass
                        
        if err_logger.get_reject() == PASS:
            err_logger.add_pass_log()
            print(f"{clip}: PASS")
        
        return err_logger

        
    def iterate_all(self):
        clip_folders = [i for i in os.listdir(self.get_base_path()) 
                        if 'Clip_' in i]
        
        sum_log_df = pd.DataFrame(columns=SUM_COL)
        full_log_df = pd.DataFrame(columns=COLUMNS)
        
        rejected_clip = []
        for clip in clip_folders:
            print("========================================================")
            el = self.rej_single_res(self.get_base_path(), clip)
            
            sum_log = el.get_summary()
            sum_log_df = pd.concat([sum_log_df, sum_log], ignore_index=True)
            
            full_log = el.get_err_log()
            full_log_df = pd.concat([full_log_df, full_log], ignore_index=True)
            if el.get_reject() == REJECT:
                rejected_clip.append(clip)
            print("========================================================\n")
        return sum_log_df, full_log_df

            