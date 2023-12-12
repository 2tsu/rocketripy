"""
インターネット接続が必要です。
地図画像を作成し、2_Mapに保存。
"""

from staticmap import StaticMap, CircleMarker


def get_map(lon, lat, zoom, path, size = (3000,3000),color="red", marker_size=6, marker_label="Oshima Island"):
    #地図タイルを国土地理院から取得
    m = StaticMap(size[0], size[1], url_template='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png')
    #ランチャーマーカーを作成    
    marker = CircleMarker((lon, lat), color, marker_size)
    m.add_marker(marker)
    #画像を作成
    img = m.render(zoom = zoom, center = (lon, lat))
    img.save(path)
    return path

if __name__ == "__main__":
    #大島ランチャー座標　139.438373,34.679730
    get_map(139.438373,34.679730,16, path="./2_Map/oshima.png")
    #能代ランチャー座標
    get_map(140.0091,40.23767, 16, path = "./2_Map/noshiro.png")