import numpy as np
from scipy.spatial.transform import Rotation as R
import math

PT_IDX_DICT = {
    "1": [1,1,8,7,2,5],
    "2": [2,2,7,8,1,6],
    "3": [3,3,6,5,4,7],
    "4": [4,4,5,6,3,8]
} ##//val: [ x_t, y_t, x_b, y_b, intercept_uppper, intercept_lower ]

CAM_FOV_DICT = {
    "S_former": [0.97307786,0.002598030572050547, -0.98814101,-0.001989300997648158],
    "S_recent": [0.90035597, 0.026340484628278205, -1.06257365, -0.012752284734313335],
    "A": [0.96583887, -0.19539506935009143, -0.99438957, 0.15072875651308948]
    
} ##//val: [ coeff_ypos, intercept_ypos, coeff_yneg, intercept_yneg ]



S_CLIP_PIVOT = 28493


class Cuboid:
    def __init__(self, center, size, rotation):
        self.center = center
        self.size = size       
        self.rotation = rotation*180/math.pi
    
    def get_center(self):
        return self.center
    def get_size(self):
        return self.size
    def get_rotation(self):
        return self.rotation    
    def set_rotation(self, rotation):
        self.rotation = rotation 

    def rotate_pt(self, pt):
        euler_angle = [0,0, self.get_rotation()]
        x_pt,y_pt,z_pt = pt                                 #// 큐보이드 꼭지점
        x3d, y3d, z3d = self.get_center()
        
        
        tmp_x, tmp_y, tmp_z = [ x_pt-x3d, y_pt-y3d, z_pt-z3d ]
        temp = R.from_euler('xyz', euler_angle, degrees=True)  # type: ignore
        rmat = np.array(temp.as_matrix())
        tmp_pt = np.array([[tmp_x, tmp_y, tmp_z]]).reshape((3,1))
        ret = (rmat @ tmp_pt).reshape((3,))
        ret = ret + np.array(self.get_center()).reshape((3,))
        
        return ret
    
    def get_cuboid_pts(self):
        center = self.get_center()
        size = self.get_size()
        x3d, y3d, z3d = center
    
        w, h, l = size ##//큐보이드 전체 // 반으로 나눠야 중심점으로부터의 거리가 됨
        """
        rot == 0
          3----4
         /|   /|
        1----2 |
        | 7--|-8
        |/   |/
        5----6

        rot == 180
          2----1
         /|   /|
        4----3 |
        | 6--|-5
        |/   |/
        8----7

        """
        p1 = [x3d-(l/2), y3d+(w/2), z3d+(h/2)]
        p2 = [x3d-(l/2), y3d-(w/2), z3d+(h/2)]
        p3 = [x3d+(l/2), y3d+(w/2), z3d+(h/2)]
        p4 = [x3d+(l/2), y3d-(w/2), z3d+(h/2)]
        
        p5 = [x3d-(l/2), y3d+(w/2), z3d-(h/2)]
        p6 = [x3d-(l/2), y3d-(w/2), z3d-(h/2)]
        p7 = [x3d+(l/2), y3d+(w/2), z3d-(h/2)]
        p8 = [x3d+(l/2), y3d-(w/2), z3d-(h/2)]
        
        p1 = self.rotate_pt(p1)
        p2 = self.rotate_pt(p2)
        p3 = self.rotate_pt(p3)
        p4 = self.rotate_pt(p4)
        
        p5 = self.rotate_pt(p5)
        p6 = self.rotate_pt(p6)
        p7 = self.rotate_pt(p7)
        p8 = self.rotate_pt(p8)
        
        return p1, p2, p3, p4, p5, p6, p7, p8
        
    def get_cuboid_pts_close(self):
        center = self.get_center()
        size = self.get_size()
        x3d, y3d, z3d = center
        ## l, w, h
        w, h, l = size ##//큐보이드 전체 // 반으로 나눠야 중심점으로부터의 거리가 됨
        p1 = [x3d-(l/2)+1, y3d+(w/2), z3d+(h/2)]
        p2 = [x3d-(l/2)+1, y3d-(w/2), z3d+(h/2)]
        p3 = [x3d+(l/2)-1, y3d+(w/2), z3d+(h/2)]
        p4 = [x3d+(l/2)-1, y3d-(w/2), z3d+(h/2)]
        
        p5 = [x3d-(l/2)+1, y3d+(w/2), z3d-(h/2)]
        p6 = [x3d-(l/2)+1, y3d-(w/2), z3d-(h/2)]
        p7 = [x3d+(l/2)-1, y3d+(w/2), z3d-(h/2)]
        p8 = [x3d+(l/2)-1, y3d-(w/2), z3d-(h/2)]
        
        p1 = self.rotate_pt(p1)
        p2 = self.rotate_pt(p2)
        p3 = self.rotate_pt(p3)
        p4 = self.rotate_pt(p4)
        
        p5 = self.rotate_pt(p5)
        p6 = self.rotate_pt(p6)
        p7 = self.rotate_pt(p7)
        p8 = self.rotate_pt(p8)
        
        return p1, p2, p3, p4, p5, p6, p7, p8
        

class Proj_2d_Wrapper:
    def __init__(self, clipname, cuboid):
        self.clipname = clipname
        self.cuboid = cuboid
        self.s_calib_former = {
            "fx": 1044.406012,
            "fy": 1045.640421,
            "cx": 977.767781,
            "cy": 603.580310,

            "k1": -0.120864,
            "k2": 0.057409,
            "p1/k3": 0.000536,
            "p2/k4": -0.000143,

            "rvec": [3.154468,0.041137,0.000315],
            
            "translation_vector": [0.075625,0.000664,-0.224375]
            # "translation_vector": [0.075625,5.000664,-0.224375]
        }
        self.s_calib_recent = {
            "fx": 1059.514412,
            "fy": 1067.573213,
            "cx": 971.806871,
            "cy": 594.326128,

            "k1": -0.143152,
            "k2": 0.063014,
            "p1/k3": -0.000618,
            "p2/k4": 0.000417,

            "rvec": [3.189968,0.035137,0.000565],
            
            "translation_vector": [0.005625,0.000664,-0.204375]
        }
        
        self.a_calib_dict = {
            "fx": 1055.996538,
            "fy": 1053.221700,
            "cx": 950.922296,
            "cy": 587.765542,

            "k1": -0.142402,
            "k2": 0.059090,
            "p1/k3": 0.000053,
            "p2/k4": 0.000071,

            "rvec": [-21.990831, -0.001500, -0.003801],
            "translation_vector": [0.245000,0.037000,-0.177801]
        }
        self.proj_module = self.select_module()

    def select_module(self):
        if self.clipname[0]=="S":
            clipnum_int = int(self.clipname.split('_')[2])
            if clipnum_int<=S_CLIP_PIVOT:
                return Proj2dBox_S_d(self.cuboid, self.s_calib_former, False, CAM_FOV_DICT.get("S_former")) 
            else:
                return Proj2dBox_S_d(self.cuboid, self.s_calib_recent, True, CAM_FOV_DICT.get("S_recent"))
        elif self.clipname[0]=="A":
            return Proj2dBox_A_d(self.cuboid, self.a_calib_dict, CAM_FOV_DICT.get("A"))
        return None

class Proj2dBox_S_d:
    def __init__(self, cuboid, cal_dict, is_recent, cam_fov_val):
        self.cuboid = cuboid
        
        self.calib = cal_dict
        self.is_recent = is_recent
        self.K, self.D, self.euler, self.tvec = self.parse_cal(self.calib)
        self.cam_fov_val = cam_fov_val
        
        self.cuboid_pts = self.mk_cuboid_pts()
        self.cuboid_close_pts = self.mk_cuboid_close_pts()
        self.pts_2d = self.mk_pts_2d()
        
    def set_cuboid(self, cuboid):
        self.cuboid = cuboid
    def get_cuboid(self):
        return self.cuboid

    def get_K(self):
        return self.K
    def get_D(self):
        return self.D
    def get_euler(self):
        return self.euler
    def get_tvec(self):
        return self.tvec
    def get_cuboid_pts(self):
        return self.cuboid_pts
    def get_cuboid_close_pts(self):
        return self.cuboid_close_pts
    def get_pts_2d(self):
        return self.pts_2d

    def mk_cuboid_pts(self):
        cb = self.get_cuboid()
        return cb.get_cuboid_pts()
    def mk_cuboid_close_pts(self):
        cb = self.get_cuboid()
        return cb.get_cuboid_pts_close()
    def mk_pts_2d(self):
        pts_arr = self.get_cuboid_pts()
        pts_close_arr = self.get_cuboid_close_pts()
        
        xi_2d = []
        yi_2d = []
        xi_close_2d = []
        yi_close_2d = []
        
        for pt, pt_close in zip(pts_arr, pts_close_arr):
            x, y, z = pt
            x_close, y_close, z_close = pt_close
            xy_2d = self.zxy_to_xy(z, x, y, self.get_tvec(), self.get_euler(), self.get_K(), self.get_D())
            xy_2d_close = self.zxy_to_xy(z_close, x_close, y_close, self.get_tvec(), self.get_euler(), self.get_K(), self.get_D())
            xi_2d.append(xy_2d[0][0])
            yi_2d.append(xy_2d[0][1])
            xi_close_2d.append(xy_2d_close[0][0])
            yi_close_2d.append(xy_2d_close[0][1])

        return [xi_2d, yi_2d, xi_close_2d, yi_close_2d]    

    def get_border_pt(self, x1, y1, x2, y2):
        a, b = 0, 0
        if x1 != x2:
            a = (y2-y1)/(x2-x1)
            b = y1 - (a*x1)
        return a, b
    
    def limit_val(self, k, maxres, minres=0):
        if k < minres: k = minres
        elif k>maxres: k = maxres
        return k
    
    def proj_2d_normal(self):
        """_summary_
        발산 보정 미적용 2d box 값  
        Returns:
            _list_: _[[x,y,w,h], area]_
        """        
        cb = self.get_cuboid()
        loc, dim, rot = cb.get_center(), cb.get_size(), abs(cb.get_rotation())
        
        box_2d, area_2d = [], 0
        pts_2d = self.get_pts_2d()
        xi_2d = pts_2d[0]
        yi_2d = pts_2d[1]
        xmin, xmax, ymin, ymax = self.limit_val(min(xi_2d), 1920), self.limit_val(max(xi_2d), 1920), \
                                 self.limit_val(min(yi_2d), 1200), self.limit_val(max(yi_2d), 1200)
        center_x, center_y, w, h = (xmax+xmin)/2, (ymax+ymin)/2, abs(xmax-xmin), abs(ymax-ymin)
        box_2d = [center_x, center_y, w, h]
        area_2d = w*h
        
        return [box_2d, area_2d]
    
    def correct_2d_indev(self, semantical=False):
        """_summary_

        Args:
            semantical (bool, optional): _True:근거리 의미적 보정 적용; False:단순 발산 보정만 적용_. Defaults to False.

        Returns:
            _list_: _[[x,y,w,h], area]_
        """
        cb = self.get_cuboid()
        
        loc, dim, rot = cb.get_center(), cb.get_size(), abs(cb.get_rotation()) 
        pt_idx = self.select_pt(loc, rot)
        xi_2d, yi_2d, xi_close_2d, yi_close_2d = self.get_pts_2d()

        # 이 트리거도 바꾸자.... 아니면 주행엔 적용 안하든지
        # x2d_pivot = 10
        # trg_val = loc[0]+(dim[2]/2)
        # coeff0 = x2d_pivot-trg_val
        # coeff1 = 30        
        # if coeff0<0: coeff0=0
        
        val_idxs = PT_IDX_DICT.get(str(pt_idx))
        ##//val: [ x_t, y_t, x_b, y_b, intercept_uppper, intercept_lower ]
        x_t, y_t = xi_2d[val_idxs[0] -1], yi_2d[val_idxs[1] -1]
        x_b, y_b = xi_2d[val_idxs[2] -1], yi_2d[val_idxs[3] -1]
        
        if semantical:
            x_t = xi_2d[val_idxs[0] -1] #- coeff0*coeff1
            a_upper, b_upper = self.get_border_pt(xi_2d[val_idxs[4] -1], yi_2d[val_idxs[4] -1], xi_close_2d[val_idxs[4] -1], yi_close_2d[val_idxs[4] -1])
            a_lower, b_lower = self.get_border_pt(xi_2d[val_idxs[5] -1], yi_2d[val_idxs[5] -1], xi_close_2d[val_idxs[5] -1], yi_close_2d[val_idxs[5] -1])
            if loc[1] > 0: 
                y_t = b_upper
                y_b = b_lower
            else:
                y_t = 1920*a_upper + b_upper
                y_b = 1920*a_lower + b_lower
        
        x_edge=1920
        if loc[1] > 0: x_edge = 0
        if y_t < 0 or y_t > 1200: y_t = 1200
        if y_b < 0 or y_b > 1200: y_b = 1200
        if x_t < 0 or x_t > 1920: x_t = x_edge
        if x_b < 0 or x_b > 1920: x_b = x_edge

        center_x, center_y =self.limit_val((x_t + x_b)/2, 1920), self.limit_val((y_t + y_b)/2, 1200)         
        w, h = self.limit_val(abs(x_t - x_b), 1920), self.limit_val(abs(y_t - y_b), 1200) 
        area_2d = self.limit_val(w*h, 1920*1200)
        box_2d = [center_x, center_y, w, h]
        return [box_2d, area_2d]
    
    def select_pt(self, loc, rot):
        if loc[1] > 0:
            if rot < 90: return 4
            else: return 1
        else:
            if rot < 90: return 3
            else: return 2
    
    def pt2d_outofbound(self, xi_2d, yi_2d):
        #2d 변환 좌표값 중 하나라도 카메라 좌표 밖일 시 True
        if any([x<0 or x>1920 for x in xi_2d]):
            return True
        if any([y<0 or y>1200 for y in yi_2d]):
            return True
        return False
    
    def mk_trigger(self):
        cb = self.get_cuboid()
        loc = cb.get_center()
        pts_arr = self.get_cuboid_pts()
        
        min_x_3d =min(list(np.array(pts_arr)[:,0]))
        fov_edge_x = 0.0
        loc_1 = loc[1]
        if loc_1>0: fov_edge_x = loc_1 / self.cam_fov_val[0] 
        else: fov_edge_x = loc_1 / self.cam_fov_val[2]
        interval = min_x_3d - fov_edge_x
        if interval < 0: return True
            
        """
        solve min_x_3d =min(list(np.array(pts_arr)[:,0]))
        
        init fov_edge_x
        case loc_y > 0
            fov_edge_x = loc_y / self.cam_fov_val[0]
        case loc_y < 0
            fov_edge_x = loc_y / self.cam_fov_val[2]
            
        interval = min_x_3d - fov_edge_x 
        if interval < CONSTANT
            return True 
        """
        """
        rot == 0
          3----4
         /|   /|
        1----2 |
        | 7--|-8
        |/   |/
        5----6

        rot == 180
          2----1
         /|   /|
        4----3 |
        | 6--|-5
        |/   |/
        8----7
        
        1: 4 
        2: 3
        3: 2
        4: 1
        
        pt[pt idx opposite] is out of bounds
        # if loc[0] < -10 or loc[0]-(dim[2]/2) > 6: return False
        # if loc[0] < -10 or loc[0]-(dim[2]/2) > 30: return False
        
        # pts_2d = self.get_pts_2d()
        # xi_2d = pts_2d[0]
        # yi_2d = pts_2d[1]
        # if self.pt2d_outofbound(xi_2d, yi_2d): return True
        """
        return False
    
    
    ##//======== calib calculation ========
    def zxy_to_xy(self, z, x, y, tvec, euler, K, D):
        fx, fy, cx, cy = K
        k1, k2, p1, p2 = D
        xyz_e_mat = self.get_xyz_euler(x, -y, -z, tvec, euler) 
        xy_u_mat = self.get_xy_u(xyz_e_mat)
        sqr = self.get_sqr(xy_u_mat)
        xy_d_mat = self.get_xy_d(sqr, xy_u_mat, k1, k2, p1, p2)
        xy_p_mat = self.get_xy_p(xy_d_mat, fx, fy, cx, cy)
        
        if self.is_recent==False:
            return np.array([ [ xy_p_mat[0][0]-60, xy_p_mat[1][0] - 40 ]   ])
        else:
            return np.array([ [ xy_p_mat[0][0]-100, xy_p_mat[1][0] + 4 ]   ])
    
    def get_xyz_euler(self, x, y, z, tvec, euler):
        tx, ty, tz = tvec
        ud, lr, rot = euler
        op1 = np.asarray([
            [0, 1, 0],
            [0, 0, -1],
            [-1, 0, 0]
        ])
        op2 = np.asarray([
            [1, 0, 0],
            [0, math.cos(rot), -math.sin(rot)],
            [0, math.sin(rot), math.cos(rot)]
        ])
        op3 = np.asarray([
            [math.cos(ud), 0, math.sin(ud)],
            [0, 1, 0],
            [-math.sin(ud), 0, math.cos(ud)]
        ])
        op4 = np.asarray([
            [math.cos(lr), -math.sin(lr), 0],
            [math.sin(lr), math.cos(lr), 0],
            [0,0, 1]
        ])
        op5 = np.asarray([
            [x - tx],
            [y - ty],
            [z - tz]
        ])

        ret = np.matmul(op1, op2)
        ret = np.matmul(ret, op3)
        ret = np.matmul(ret, op4)
        ret = np.matmul(ret, op5)
        return ret

    def get_xy_u(self, xyz_e_mat):
        xe = xyz_e_mat[0][0]
        ye = xyz_e_mat[1][0]
        ze = xyz_e_mat[2][0]
        if ze !=0: return np.asarray([[xe/ze],[ye/ze]])
        else: return np.asarray([[ 0 ],[ 0 ]])

    def get_sqr(self, xy_u_mat): ##// (2,1)
        xu = xy_u_mat[0][0]
        yu = xy_u_mat[1][0]
        return xu*xu + yu*yu 
        
    def get_xy_d(self, sqr, xy_u_mat, k1, k2, p1, p2):
        op1_coeff = 1 + k1*sqr + k2*sqr*sqr
        xu = xy_u_mat[0][0]
        yu = xy_u_mat[1][0]
        op1 = np.asarray([
            [xu * op1_coeff],
            [yu * op1_coeff]
        ])
        op2 = np.asarray([
            [2*p1*xu*yu + p2*(sqr + 2*xu*xu)],
            [p1*(sqr + 2*yu*yu) + 2*p2*xu*yu]
        ])
        return op1 + op2
        
    def get_xy_p(self, xy_d_mat, fx, fy, cx, cy):
        xd = xy_d_mat[0][0]
        yd = xy_d_mat[1][0]
        
        op1 = np.asarray([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 0]
        ])
        op2 = np.asarray([
            [xd],
            [yd],
            [1]
        ])
        ret = np.matmul(op1, op2)
        return np.asarray( [[ ret[0][0] ],[ ret[1][0] ]] )

    def parse_cal(self, calib):
        fx = float(calib['fx'])
        fy = float(calib['fy'])
        cx = float(calib['cx'])
        cy = float(calib['cy'])
        k1 = float(calib['k1'])
        k2 = float(calib['k2'])
        p1 = float(calib['p1/k3'])
        p2 = float(calib['p2/k4'])
        euler = calib["rvec"]
        tvec = calib['translation_vector']
        K = [fx, fy, cx, cy]
        D = [k1, k2, p1, p2]
        return K, D, euler, tvec
            
    def rotate_2d(self, target_pt, base_pt, theta, is_deg=True):
        ##// 2차원 평면에서 회전
        if is_deg == True:
            theta = theta*math.pi / 180
        x, y = target_pt[0], target_pt[1]
        base_x, base_y = base_pt[0], base_pt[1]
        ret_x = (x-base_x)*math.cos(theta) - (y-base_y)*math.sin(theta) + base_x
        ret_y = (x-base_x)*math.sin(theta) + (y-base_y)*math.cos(theta) + base_y
        ret_pt = np.array([ret_x, ret_y])
        return ret_pt
    

class Proj2dBox_A_d:
    def __init__(self, cuboid, cal_dict, cam_fov_val):
        self.cuboid = cuboid
        
        self.calib = cal_dict
        self.K, self.D, self.euler, self.tvec = self.parse_cal(self.calib)
        self.cam_fov_val = cam_fov_val
        
        self.cuboid_pts = self.mk_cuboid_pts()
        self.cuboid_close_pts = self.mk_cuboid_close_pts()
        self.pts_2d = self.mk_pts_2d()
        
    def set_cuboid(self, cuboid):
        self.cuboid = cuboid
    def get_cuboid(self):
        return self.cuboid
    def get_K(self):
        return self.K
    def get_D(self):
        return self.D
    def get_euler(self):
        return self.euler
    def get_tvec(self):
        return self.tvec
    def get_cuboid_pts(self):
        return self.cuboid_pts
    def get_cuboid_close_pts(self):
        return self.cuboid_close_pts
    def get_pts_2d(self):
        return self.pts_2d

    def mk_cuboid_pts(self):
        cb = self.get_cuboid()
        return cb.get_cuboid_pts()
    def mk_cuboid_close_pts(self):
        cb = self.get_cuboid()
        return cb.get_cuboid_pts_close()
    def mk_pts_2d(self):
        pts_arr = self.get_cuboid_pts()
        pts_close_arr = self.get_cuboid_close_pts()
        
        xi_2d = []
        yi_2d = []
        xi_close_2d = []
        yi_close_2d = []
        
        for pt, pt_close in zip(pts_arr, pts_close_arr):
            x, y, z = pt
            x_close, y_close, z_close = pt_close
            xy_2d = self.zxy_to_xy(z, x, y, self.get_tvec(), self.get_euler(), self.get_K(), self.get_D())
            xy_2d_close = self.zxy_to_xy(z_close, x_close, y_close, self.get_tvec(), self.get_euler(), self.get_K(), self.get_D())
            xi_2d.append(xy_2d[0][0])
            yi_2d.append(xy_2d[0][1])
            xi_close_2d.append(xy_2d_close[0][0])
            yi_close_2d.append(xy_2d_close[0][1])

        return [xi_2d, yi_2d, xi_close_2d, yi_close_2d]    
        
    def get_border_pt(self, x1, y1, x2, y2):
        a = 0
        b = 0
        if x1!=x2:
            a = (y2-y1)/(x2-x1)
            b = y1 - (a*x1)
        return a, b
    def limit_val(self, k, maxres):
        if k < 0: k = 0
        elif k>maxres: k = maxres
        return k
    
    
    def proj_2d_normal(self):
        """_summary_
        발산 보정 미적용 2d box 값  
        Returns:
            _list_: _[[x,y,w,h], area]_
        """        
        box_2d, area_2d = [], 0
        pts_2d = self.get_pts_2d()
        xi_2d = pts_2d[0]
        yi_2d = pts_2d[1]
        xmin, xmax, ymin, ymax = self.limit_val(min(xi_2d), 1920), self.limit_val(max(xi_2d), 1920), \
                                 self.limit_val(min(yi_2d), 1200), self.limit_val(max(yi_2d), 1200)
        center_x, center_y, w, h = (xmax+xmin)/2, (ymax+ymin)/2, abs(xmax-xmin), abs(ymax-ymin)
        box_2d = [center_x, center_y, w, h]
        area_2d = w*h
        return [box_2d, area_2d]

    def correct_2d_indev(self, semantical=False):
        """_summary_

        Args:
            semantical (bool, optional): _True:근거리 의미적 보정 적용; False:단순 발산 보정만 적용_. Defaults to False.

        Returns:
            _list_: _[[x,y,w,h], area]_
        """        
        cb = self.get_cuboid()
        
        loc, dim, rot = cb.get_center(), cb.get_size(), abs(cb.get_rotation())
        pt_idx = self.select_pt(loc, rot)
        xi_2d, yi_2d, xi_close_2d, yi_close_2d = self.get_pts_2d()

        # x2d_pivot = 10
        # trg_val = loc[0]+(dim[2]/2)
        # coeff0 = x2d_pivot-trg_val
        # coeff1 = 30

        val_idxs = PT_IDX_DICT.get(str(pt_idx))
        ##//val: [ x_t, y_t, x_b, y_b, intercept_uppper, intercept_lower ]
        x_t, y_t = xi_2d[val_idxs[0] -1], yi_2d[val_idxs[1] -1]
        x_b, y_b = xi_2d[val_idxs[2] -1], yi_2d[val_idxs[3] -1]
        if semantical:
            x_t = xi_2d[val_idxs[0] -1] #- coeff0*coeff1
            a_upper, b_upper = self.get_border_pt(xi_2d[val_idxs[4] -1], yi_2d[val_idxs[4] -1], xi_close_2d[val_idxs[4] -1], yi_close_2d[val_idxs[4] -1])
            a_lower, b_lower = self.get_border_pt(xi_2d[val_idxs[5] -1], yi_2d[val_idxs[5] -1], xi_close_2d[val_idxs[5] -1], yi_close_2d[val_idxs[5] -1])
            if loc[1] > 0: 
                y_t = b_upper
                y_b = b_lower
            else:
                y_t = 1920*a_upper + b_upper
                y_b = 1920*a_lower + b_lower
        x_edge=1920
        if loc[1] > 0: x_edge = 0
        if y_t < 0 or y_t > 1200: y_t = 1200
        if y_b < 0 or y_b > 1200: y_b = 1200
        if x_t < 0 or x_t > 1920: x_t = x_edge
        if x_b < 0 or x_b > 1920: x_b = x_edge

        center_x, center_y = self.limit_val((x_t + x_b)/2, 1920), self.limit_val((y_t + y_b)/2, 1200)         
        w, h = self.limit_val(abs(x_t - x_b), 1920), self.limit_val(abs(y_t - y_b), 1200) 
        area_2d =self.limit_val(w*h, 1920*1200)
        box_2d = [center_x, center_y, w, h]
        return [box_2d, area_2d]
        
    
    def select_pt(self, loc, rot):
        if loc[1] > 0:
            if rot < 90: return 4
            else: return 1
        else:
            if rot < 90: return 3
            else: return 2
    
    def pt2d_outofbound(self, xi_2d, yi_2d):
        if any([x<0 or x>1920 for x in xi_2d]): return True
        if any([y<0 or y>1200 for y in yi_2d]): return True
        return False
        
    def mk_trigger(self):
        cb = self.get_cuboid()
        loc = cb.get_center()
        pts_arr = self.get_cuboid_pts()
        
        min_x_3d =min(list(np.array(pts_arr)[:,0]))
        fov_edge_x = 0.0
        loc_1 = loc[1]
        if loc_1>0: fov_edge_x = loc_1 / self.cam_fov_val[0] 
        else: fov_edge_x = loc_1 / self.cam_fov_val[2]
        interval = min_x_3d - fov_edge_x
        if interval < 0: return True

        return False
    
    
    
    ##//======== calib calculation ========
    def zxy_to_xy(self, z, x, y, tvec, euler, K, D):
        fx, fy, cx, cy = K
        k1, k2, p1, p2 = D
        
        xyz_e_mat = self.get_xyz_euler(x, -z, y, tvec, euler)
        xy_u_mat = self.get_xy_u(xyz_e_mat)
        sqr = self.get_sqr(xy_u_mat)
        xy_d_mat = self.get_xy_d(sqr, xy_u_mat, k1, k2, p1, p2)
        xy_p_mat = self.get_xy_p(xy_d_mat, fx, fy, cx, cy)
        
        ret_pt = self.rotate_2d([xy_p_mat[0][0], xy_p_mat[1][0]], [960,600], -90)
        
        return np.array([[ ret_pt[0]-8, ret_pt[1]-32 ]])
        
    def get_xyz_euler(self, x, y, z, tvec, euler):
         
        tx, tz, ty = tvec
        lr, ud, rot = euler
        
        op1 = np.asarray([
            [0, 1, 0],
            [0, 0, -1],
            [-1, 0, 0]
        ])
        op2 = np.asarray([
            [1, 0, 0],
            [0, math.cos(rot), -math.sin(rot)],
            [0, math.sin(rot), math.cos(rot)]
        ])
        op3 = np.asarray([
            [math.cos(ud), 0, math.sin(ud)],
            [0, 1, 0],
            [-math.sin(ud), 0, math.cos(ud)]
        ])
        op4 = np.asarray([
            [math.cos(lr), -math.sin(lr), 0],
            [math.sin(lr), math.cos(lr), 0],
            [0,0, 1]
        ])
        op5 = np.asarray([
            [x - tx],
            [y - ty],
            [z + tz]
        ])
       
        ret = np.matmul(op1, op2)
        ret = np.matmul(ret, op3)
        ret = np.matmul(ret, op4)
        ret = np.matmul(ret, op5)
        return ret

    def get_xy_u(self, xyz_e_mat):
        xe = xyz_e_mat[0][0]
        ye = xyz_e_mat[1][0]
        ze = xyz_e_mat[2][0]
        if ze !=0: return np.asarray([[xe/ze],[ye/ze]])
        else: return np.asarray([[ 0 ],[ 0 ]])

    def get_sqr(self, xy_u_mat): ##// (2,1)
        xu = xy_u_mat[0][0]
        yu = xy_u_mat[1][0]
        return xu*xu + yu*yu 
        
    def get_xy_d(self, sqr, xy_u_mat, k1, k2, p1, p2):
        op1_coeff = 1 + k1*sqr + k2*sqr*sqr
        xu = xy_u_mat[0][0]
        yu = xy_u_mat[1][0]
        op1 = np.asarray([
            [xu * op1_coeff],
            [yu * op1_coeff]
        ])
        op2 = np.asarray([
            [2*p1*xu*yu + p2*(sqr + 2*xu*xu)],
            [p1*(sqr + 2*yu*yu) + 2*p2*xu*yu]
        ])
        return op1 + op2
        
    def get_xy_p(self, xy_d_mat, fx, fy, cx, cy):
        xd = xy_d_mat[0][0]
        yd = xy_d_mat[1][0]
        
        op1 = np.asarray([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 0]
        ])
        op2 = np.asarray([
            [xd],
            [yd],
            [1]
        ])
        
        ret = np.matmul(op1, op2)
        
        return np.asarray( [[ ret[0][0] ],[ ret[1][0] ]] )

    def parse_cal(self, calib):
        fx = float(calib['fx'])
        fy = float(calib['fy'])
        cx = float(calib['cx'])
        cy = float(calib['cy'])
        k1 = float(calib['k1'])
        k2 = float(calib['k2'])
        p1 = float(calib['p1/k3'])
        p2 = float(calib['p2/k4'])
        euler = calib["rvec"]
        tvec = calib['translation_vector']
        K = [fx, fy, cx, cy]
        D = [k1, k2, p1, p2]
        
        return K, D, euler, tvec

    def rotate_2d(self, target_pt, base_pt, theta, is_deg=True):
        ##// 2차원 평면에서 회전
        if is_deg == True:
            theta = theta*math.pi / 180
        x, y = target_pt[0], target_pt[1]
        base_x, base_y = base_pt[0], base_pt[1]
        ret_x = (x-base_x)*math.cos(theta) - (y-base_y)*math.sin(theta) + base_x
        ret_y = (x-base_x)*math.sin(theta) + (y-base_y)*math.cos(theta) + base_y
        ret_pt = np.array([ret_x, ret_y])
        return ret_pt
    


