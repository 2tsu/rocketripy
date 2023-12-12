#Data Calculation Library
import pandas as pd
import numpy as np
from math import atan, log, tan, pi, cos
#GIS Library
import pyproj
#To read json
from PIL import Image, ImageDraw, ImageFont
import os
from mypackages.for_pre_processing import Constants





PATH_MAP = "./2_Map/noshiro.png"
LAUNCHER_LON, LAUNCHER_LAT = Constants.launcher()["Longitude"], Constants.launcher()["Latitude"]


class SafetyZone:
    """
    草案
    
    保安区域を描画する必要があるが、その情報を別クラスで管理する。
    """
    def __init__(self) -> None:
        raise NotImplementedError



class ResultViewer:    
    def __init__(self, size = (3000, 3000),zoom = 16,path_result:str = "./4_Results/2023-1205-083923/", wind = [1,2], deg=[0, 45, 90, 135, 180, 225, 270]) -> None:
        if isinstance(wind, int):
            self.wind = np.arange(0, wind)
        elif isinstance(wind, list):
            self.wind = wind
        else:
            raise TypeError("wind must be int or list.")
        
        if isinstance(deg, int):
            self.deg = np.arange(0, deg, 45)
        elif isinstance(deg, list):
            self.deg = deg  
        else:
            raise TypeError("deg must be int or list.")
        
        self.path = path_result
        
        #座標変換に使用するクラス変数
        self.center = (LAUNCHER_LON, LAUNCHER_LAT)
        self.zoom = zoom
        self.x_center = self._lon_to_x(self.center[0], self.zoom)
        self.y_center = self._lat_to_y(self.center[1], self.zoom)
        self.tile_size = 256
        self.width = size[0]
        self.height =size[1]
        
        #実行
        self.image = self.get_image()
        self.draw = ImageDraw.Draw(self.image)
        self.landings = self.get_landings(self.wind, self.deg, self.path)
    
    def get_image(self, path = PATH_MAP):
        """
        画像を取得する。
        """
        return Image.open(path)
    
    def get_result_path(self):
        """
        未実装
        """
        filelist = os.listdir(self.path+"/Summaries_History")	
        return filelist

    def get_landing_full_path(self, path):
        df = pd.read_csv(path)
        return list(zip(df["Landing_longitude"], df["Landing_latitude"]))  # Create an array of tuples
    def get_landings(self, wind, angle, path):
        landings = []
        for w in wind:
            wind_landings = []
            for a in angle:
                loc = path+ "Summaries_History/wind_"+str(w)+"_ang_"+str(a)+".csv"
                df = pd.read_csv(loc)
                lonlat = list(zip(df["Landing_longitude"], df["Landing_latitude"]))  # Create an array of tuples
                wind_landings.extend(lonlat)  # Extend the wind_landings array with the tuples
            landings.append(wind_landings)  # Append the wind_landings array to the landings array
        return landings
    
    def calc_azimuth_dist(self, simulator_coordinate):
        """
        素データではx-y-zは右手系でxが高度になっている。
        simulator_coordinate にはy,zの順番で渡す。
        北をy軸正方向としy軸を始線反時計回りを正とする。
        coord = (x, y)
        must be right-handed coordinate system
        原点から点の距離と方位を計算する。
        例
        100, 100地点は北西に45°の方向に100√2の距離にある。
        """
        distance = np.sqrt(np.square(simulator_coordinate[0]) + np.square(simulator_coordinate[1]))

        #画像座標における方向に変換。
        #これはz軸を基準にどれだけ角度があるかを計算。時計回りを正としている。
        
        #zerodivision errorを防ぐために分岐
        #z軸が0のとき
        if simulator_coordinate[1] == 0:
            #y軸が正なら北、負なら南
            if simulator_coordinate[0] > 0:
                azimuth = 0.
            else:
                azimuth = 180.
        
        else:
            azimuth = np.rad2deg(atan(simulator_coordinate[0]/simulator_coordinate[1])) + 270.
        
        return azimuth, distance
    
    def simulator_coordinates_to_coordinates(self, coordinate):
        grs80 = pyproj.Geod(ellps = "GRS80")
        azi, dis = self.calc_azimuth_dist(coordinate)#azimuthは北を0°時計回りを正と定義
        
        lon, lat, _ = grs80.fwd(self.center[0], self.center[1], azi, dis)
        return (lon, lat)
    
    def simulator_coordinates_to_pixels(self, coordinate):
        lonlat = self.simulator_coordinates_to_coordinates(coordinate)
        return (self.lon2px_x(lonlat[0]), self.lat2px_y(lonlat[1]))

        
    def _lon_to_x(self, lon, zoom):
        
        if not (-180 <= lon <= 180):
            lon = (lon + 180) % 360 - 180
            
        return ((lon + 180.) / 360) * pow(2, zoom)


    def _lat_to_y(self, lat, zoom):
        
        if not (-90 <= lat <= 90):
            lat = (lat + 90) % 180 - 90
            
        return (1 - log(tan(lat * pi / 180) + 1 / cos(lat * pi / 180)) / pi) / 2 * pow(2, zoom)


    def lon2px_x(self, lon):
        
        if not (-180 <= lon <= 180):
            lon = (lon + 180) % 360 - 180
        
        x = ((lon + 180.) / 360) * pow(2, self.zoom)
        
        pixel_x = (x - self.x_center) * self.tile_size + self.width / 2
        
        return pixel_x
    
    def lat2px_y(self, lat):
        
        if not (-90 <= lat <= 90):
            lat = (lat + 90) % 180 - 90
        
        y = (1 - log(tan(lat * pi / 180) + 1 / cos(lat * pi / 180)) / pi) / 2 * pow(2, self.zoom)
        
        pixel_y = (y - self.y_center) * self.tile_size + self.height / 2
        
        return pixel_y

    def coordinate_to_pixel(self, coordinate):
        return self.lon2px_x(coordinate[0]), self.lat2px_y(coordinate[1])

    def coordinates_to_pixels(self, list_of_coordinates):
        return [[self.coordinate_to_pixel(coordinate) for coordinate in coordinates] for coordinates in list_of_coordinates]


    """
    以降フィーチャーの描画に与える変数はすべて緯度経度を基本とする。
    """


    def draw_circle(self, lonlat, r, color ="black",fill = None, width=1):
        """
        Draws a circle on the canvas.
        
        Args:
            lonlat (tuple): The longitude and latitude coordinates of the circle's center.
            r (float): The horizontal radius of the circle.
            color (str): The color of the circle.
            width (int): The width of the circle's outline.
        """
        #converter
        grs80 = pyproj.Geod(ellps='GRS80')
        # Calculate the top left and bottom right coordinates of the ellipse
        lon_top_left, lat_top_left, _ = grs80.fwd(lonlat[0], lonlat[1], 315, r * np.sqrt(2))
        lon_bottom_right, lat_bottom_right, _ = grs80.fwd(lonlat[0], lonlat[1], 135, r * np.sqrt(2))
        
        # Convert the coordinates to pixel values
        pix_top_left = (self.lon2px_x(lon_top_left), self.lat2px_y(lat_top_left))
        pix_bottom_right = (self.lon2px_x(lon_bottom_right), self.lat2px_y(lat_bottom_right))
        
        self.draw.ellipse([pix_top_left, pix_bottom_right], fill=fill, outline=color, width=width)
        return "ellipse"


    def draw_polygon(self, lonlat, color, fill = None, width=1):
        """
        coordinates are assumed to be an array of tuples [(x1, y1), (x2, y2), ...] representing longitude and latitude.
        
        """        

        if isinstance(lonlat, list):
            pix = [(self.lon2px_x(lonlat[i-1][0]), self.lat2px_y(lonlat[i-1][1])) for i in range(len(lonlat)+1)]
            self.draw.polygon(pix, fill=fill, outline=color, width=width)
            return "polygon"
        else:
            raise TypeError("lonlat must be a tuple or a list of tuples.")


    def draw_line(self, lonlat1, lonlat2, color, width=1, pix_mode = False):
        if pix_mode == True:
            self.draw.line([lonlat1, lonlat2], fill=color, width=width)
            return "line"
        else:
            pix1 = (self.lon2px_x(lonlat1[0]), self.lat2px_y(lonlat1[1]))
            pix2 = (self.lon2px_x(lonlat2[0]), self.lat2px_y(lonlat2[1]))
            self.draw.line([pix1, pix2], fill=color, width=width)
            return "line"


    def draw_text(self, lonlat, text, color, size=12):
        """
        複数テキストの同時描画にアップデート予定
        """
        pix = (self.lon2px_x(lonlat[0]), self.lat2px_y(lonlat[1]))
        font = ImageFont.truetype("arial.ttf", size)
        self.draw.text(pix, text, fill=color, font=font)
        return "text"


    def draw_image(self, lonlat ,image, pix_mode = False):
        if pix_mode == True:
            self.image.paste(image, lonlat)
            return "image"

        else:
            pix = (self.lon2px_x(lonlat[0]), self.lat2px_y(lonlat[1]))
            self.image.paste(image, pix)
            return "image"
        

    def save(self, name):
        path = f"{self.path}/Graphs/"+name+".png"
        self.image.save(path)
        return path

    def draw_grid(self):
        #距離円と目盛り
        for r in np.arange(0, 5000, 250):
            self.draw_circle(self.center, r, color = "black")
            
            temp = self.simulator_coordinates_to_coordinates((r,0))
            self.draw_text(temp, str(r)+"m", "black")
        
        #軸線
        self.draw_line((self.width/2, 0), (self.width/2, self.height), "black", pix_mode=True)
        self.draw_line((0, self.height/2), (self.width, self.height/2), "black", pix_mode=True)
    
    def draw_safety_zone(self):
        return NotImplementedError
    def draw_landing(self):
        for i in range(len(self.wind)):
            self.draw_polygon(self.landings[i], "red")
            for j in range(len(self.deg)):
                self.draw_circle(self.landings[i][j], 2, "red", fill = "red")

    def draw_info():
        """
        マップの右下や左下にコピーライトや国土地理院の使用許諾などを描画する。
        """
        raise NotImplementedError

    def draw_legend():
        """
        シミュレーター条件などを描画して、マップの左上に表示する。
        必要事項
        ・風速
        ・風向き
        ・ランチャーの位置
        ・ランチャーの向き
        など。自由に考えてください。
        map画像に直接描画しても、別画像に描画した後に貼り付けても構いません。
        """
        raise NotImplementedError
    
    def draw_colorbar():
        """
        落下分散は今のところ赤単色ですがわかりやすいように風速ごとに色を変えるなどの工夫をしてください。
        またその色に対応した風速がわかるようにカラーバーをマップ画像の右端に描画してください。
        map画像に直接描画しても、別画像に描画した後に貼り付けても構いません。
        """
        raise NotImplementedError


if __name__ == "__main__":
    a = ResultViewer((140.0091,40.23767), zoom = 16)
    a.draw_grid()
    a.draw_landing()
    a.save("test")