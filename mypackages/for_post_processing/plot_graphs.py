"""
外部からデータをうけとり、グラフを描画する
審査書用テンプレートを作成する

加えて、手っ取り早くグラフを描画できるようなものもほしい。

/4_Results/2023-1205-083923/Histories/wind_1_ang_45.xlsx
"""

def create_graph():
    """
    4_Results/...から指定した風速、角度のエクセルファイルを読み取り、
    指定したx,y軸のグラフを作成し、表示する。
    次のようなことにも対応させること。
    x=時間でy= V_x, v_y, v_z
    のようにして一つのグラフに3本の曲線が描画できると良い。
    """
    raise NotImplementedError
def create_graph_template():
    """
    4_Results/...から審査書に求められる風速、角度のエクセルファイルを読み取り、
    指定したx,y軸のグラフを作成し、Graphsに保存する。この際きれいなグラフを心掛けること
    例
    グラフのアスペクト比
    タイトル
    凡例
    線の太さ、色
    """
    raise NotImplementedError

def create_3dgraph():
    """
    4_Results/...から指定した風速、角度のエクセルファイルを読み取り、
    指定したx,y,z軸のグラフを作成し、表示する。
    以下の工夫などを自由にしてください。
    落下モード事に色を分けて見やすく。
    """
    raise NotImplementedError