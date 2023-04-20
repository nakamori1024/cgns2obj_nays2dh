"""
MIT License

Copyright (c) 2023 Shinsuke Nakamori

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# v2.0.0
import os
import shutil
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import numpy as np
import pandas as pd
from iRIC_class import Nays2DH

def judge_depth(depth, min_depth, down_h):
    """
    水深の値をチェックし、補正後の値を返す。\n
    Args:
        depth : 水深
        min_depth : 最小水深[m]
        down_h : 補正高さ[m]
    """
    if depth <= min_depth:
        depth += down_h
    return depth

def adjust_list(depth_list, min_depth, down_h):
    """
    水深の一次元配列を読み込み、補正する。\n
    Args:
        depth_list : 水深の一次元配列
        min_depth : 最小水深[m]
        down_h : 補正高さ[m]
    """
    # リストの長さ
    length = len(depth_list)

    # 最小水深のリスト
    min_list = [min_depth] * length

    # 補正値のリスト
    ad_list = [down_h] * length

    depth_list = list(map(judge_depth, depth_list, min_list, ad_list))
    return depth_list

def adjust_depth(depth, min_depth, down_h):
    """
    最小水深以下の格子点の水深を補正する。\n
    Args:
        depth : 水深の二次元配列
        min_depth : 最小水深[m]
        down_h : 補正高さ[m]
    Returns:
        ad_depth : 補正後の水深の二次元配列
    """
    ad_depth = np.apply_along_axis(adjust_list, 1, depth, min_depth, down_h)

    return ad_depth

def get_v(x_coords, y_coords, z_coords, scale, reverse):
    """
    x, y, z座標値を含む二次元配列からobjの頂点情報を取得する。\n
    Args:
        x_coords : x座標の二次元配列
        y_coords : y座標の二次元配列
        z_coords : z座標の二次元配列
        scale : 座標値の等倍
        reverse : Y軸の反転有無（True:反転する、False:反転しない）
    Returns:
        v_text : obj形式の頂点情報
    """
    # 一次元配列に変換
    x_coords = x_coords.flatten()
    y_coords = y_coords.flatten()
    z_coords = z_coords.flatten()

    # 倍率変更
    x_coords = list(map(lambda x: x*scale, x_coords))
    y_coords = list(map(lambda x: x*scale, y_coords))
    z_coords = list(map(lambda x: x*scale, z_coords))

    # Y軸の反転
    if reverse is True:
        y_coords = list(map(lambda x: x*(-1), y_coords))

    # Dataframe
    df = pd.DataFrame(index=[], columns=["key", "x", "y", "z"])
    df["key"] = ["v"] * len(z_coords)
    df["x"] = x_coords
    df["y"] = z_coords # objファイルはy軸が上下方向となる
    df["z"] = y_coords

    # ファイルに一時保存
    temp_file = "./zzz_temp.txt"
    df.to_csv(temp_file, encoding="utf8", header=None, index=None)

    # テキスト情報として取得
    with open(temp_file, "r") as f:
        v_text = f.read()
        v_text = v_text.replace(",", " ")
    
    # 一時ファイルの削除
    os.remove(temp_file)

    return v_text

def get_vt(x_coords, y_coords):
    """
    x,y座標値を含む二次元配列からテクスチャ座標情報を取得する。\n
    Args:
        x_coords : x座標の二次元配列
        y_coords : y座標の二次元配列
    Returns:
        vt_text : obj形式のテクスチャ座標情報
    """
    # 戻り値の定義
    vt_text = ""

    # 一次元配列に変換
    x_coords = x_coords.flatten()
    y_coords = y_coords.flatten()

    # 最大値&最小値の取得
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    for i in range(len(x_coords)):
        # テクスチャ座標
        xt = (x_coords[i] - x_min)/(x_max - x_min)
        yt = (y_coords[i] - y_min)/(y_max - y_min)

        # テクスチャ座標の定義
        text = "vt " + str(xt) + " " + str(yt) + "\n"

        vt_text += text

    return vt_text

def get_f(ni, nj, grid_num, step, reverse):
    """
    格子形状からobjのメッシュ情報を取得する。\n
    Args:
        ni : 縦断方向の分割数
        nj : 横断方向の分割数
        grid_num : 計算格子の格子点の数
        step : 出力結果のステップ数（出力開始時をstep1とし、出力間隔毎に1ずつ増える）
        reverse : Y軸の反転有無（True:反転する、False:反転しない）
    Returns:
        f_text : obj形式のメッシュ情報
    """
    # 戻り値の定義
    f_text = ""

    for j in range(nj + 1):
        for i in range(ni):
            # 格子点番号
            n1  = (ni + 1) * j + i + 1 + grid_num * (step - 1)
            n2  = (ni + 1) * j + i + 2 + grid_num * (step - 1)
            n3b = (ni + 1) * (j - 1) + i + 2 + grid_num * (step - 1)
            n3a = (ni + 1) * (j + 1) + i + 1 + grid_num * (step - 1)

            # 垂直方向情報
            h = 1

            # 三角形メッシュの構成要素
            p1  = str(n1) + "/" + str(n1) + "/" + str(h)
            p2  = str(n2) + "/" + str(n2) + "/" + str(h)
            p3b = str(n3b) + "/" + str(n3b) + "/" + str(h)
            p3a = str(n3a) + "/" + str(n3a) + "/" + str(h)

            # 上から見て時計回りになるように格子点を指定
            if reverse is True:
                if j == 0:
                    text = "f " + p1 + " " + p2 + " " + p3a + "\n"
                elif j == nj:
                    text = "f " + p2 + " " + p1 + " " + p3b + "\n"
                else:
                    text = "f " + p2 + " " + p1 + " " + p3b + "\n" + "f " + p1 + " " + p2 + " " + p3a + "\n"
            else:
                if j == 0:
                    text = "f " + p2 + " " + p1 + " " + p3a + "\n"
                elif j == nj:
                    text = "f " + p1 + " " + p2 + " " + p3b + "\n"
                else:
                    text = "f " + p1 + " " + p2 + " " + p3b + "\n" + "f " + p2 + " " + p1 + " " + p3a + "\n"
            
            f_text += text

    return f_text

def wsurf_obj(cgns_land, cgns_depth, reverse=False):
    """
    iRICの計算結果から水位の3Dモデル（.obj）を作成する。\n
    Args:
        cgns_land : 地形を読み込むiRICの計算結果ファイル
        cgns_depth : 水深を読み込むiRICの計算結果ファイル
        reverse : Y軸の反転有無（True:反転する、False:反転しない）
    """
    # -------パラメータ設定------- #
    # 格子サイズの倍率
    scale = 0.1

    # 最小水深未満の格子点への補正高さ[m]
    down_h = -2.0
    # --------------------------- #

    # iRIC結果ファイルの読み込み
    iRland = Nays2DH(cgns_land)
    iRdepth = Nays2DH(cgns_depth)

    # 格子の分割数
    gridsize = iRland.GridSize()
    ni = gridsize[0] # 縦断方向
    nj = gridsize[1] # 横断方向

    # 格子点の数
    grid_num = (ni + 1) * (nj + 1)

    # 計算格子の座標値
    x_coords = iRland.CoordX()
    y_coords = iRland.CoordY()

    # 出力している計算結果の数
    nstep = iRdepth.Results()

    # 最小水深+1mm
    min_depth = iRdepth.MinDepth() + 0.001

    # objファイルの名前
    obj_file = "./output/wsurf.obj"

    with open(obj_file, "w") as f:
        # マテリアル定義ファイル
        obj_text = "# mtl file" + "\n"
        obj_text += "mtllib water.mtl" + "\n" + "\n"

        # 書き込み
        f.write(obj_text)

    for step in range(nstep):
        # 地形（標高）
        land = iRland.Elevation(1)

        # 水深
        depth = iRdepth.Depth(step + 1)

        # 水深の補正
        depth = adjust_depth(depth, min_depth, down_h)

        # 水位
        wsurf = land + depth

        # 頂点情報
        v_text = get_v(x_coords, y_coords, wsurf, scale, reverse)

        # テクスチャ座標情報
        vt_text = get_vt(x_coords, y_coords)

        # メッシュ情報
        f_text = get_f(ni, nj, grid_num, step + 1, reverse)

        # objファイル
        with open(obj_file, "w") as f:
            # グループ名
            obj_text += "# Group Name" + "\n"
            obj_text += "g step" + str(step + 1) + "\n" + "\n"

            # MAT
            obj_text += "# Material Infomation" + "\n"
            obj_text += "usemtl water" + "\n" + "\n"

            # 格子点情報
            obj_text += "# Node Coordinate" + "\n"
            obj_text += v_text + "\n"

            # テクスチャ座標情報
            obj_text += "# Texture Coordinate" + "\n"
            obj_text += vt_text + "\n"

            # 垂直方向情報
            obj_text += "# Vertical Infomation" + "\n"
            obj_text += "vn 0.0 1.0 0.0" + "\n" + "\n"

            # メッシュ情報
            obj_text += "# Mesh Infomaition" + "\n"
            obj_text += f_text + "\n"

            # 書き込み
            f.write(obj_text)
    
    return 0

def land_obj(cgns_land, reverse=False):
    """
    iRICの計算結果から水位の3Dモデル（.obj）を作成する。\n
    Args:
        cgns_land : 地形を読み込むiRICの計算結果ファイル
        reverse : Y軸の反転有無（True:反転する、False:反転しない）
    """
    # -------パラメータ設定------- #
    # 格子サイズの倍率
    scale = 0.1
    # --------------------------- #

    # iRIC結果ファイルの読み込み
    iRland = Nays2DH(cgns_land)

    # 格子の分割数
    gridsize = iRland.GridSize()
    ni = gridsize[0] # 縦断方向
    nj = gridsize[1] # 横断方向
    
    # 格子点の数
    grid_num = (ni + 1) * (nj + 1)

    # 計算格子の座標値
    x_coords = iRland.CoordX()
    y_coords = iRland.CoordY()

    # 地形（標高）
    land = iRland.Elevation(1)

    # 頂点情報
    v_text = get_v(x_coords, y_coords, land, scale, reverse)

    # テクスチャ座標情報
    vt_text = get_vt(x_coords, y_coords)

    # メッシュ情報
    f_text = get_f(ni, nj, grid_num, 1, reverse)

    # objファイルの名前
    obj_file = "./output/land_step=" + str(1) + ".obj"

    # objファイル
    with open(obj_file, "w") as f:
        # マテリアル定義ファイル
        obj_text = "# mtl file" + "\n"
        obj_text += "mtllib land.mtl" + "\n" + "\n"

        # グループ名
        obj_text += "# Group Name" + "\n"
        obj_text += "g step" + str(1) + "\n" + "\n"

        # MAT
        obj_text += "# Material Infomation" + "\n"
        obj_text += "usemtl land" + "\n" + "\n"

        # 格子点情報
        obj_text += "# Node Coordinate" + "\n"
        obj_text += v_text + "\n"

        # テクスチャ座標情報
        obj_text += "# Texture Coordinate" + "\n"
        obj_text += vt_text + "\n"

        # 垂直方向情報
        obj_text += "# Vertical Infomation" + "\n"
        obj_text += "vn 0.0 1.0 0.0" + "\n" + "\n"

        # メッシュ情報
        obj_text += "# Mesh Infomaition" + "\n"
        obj_text += f_text

        # 書き込み
        f.write(obj_text)
    
    return 0

def open_file_command(edit_box, file_type_list):
    file_path = fd.askopenfilename(filetypes = file_type_list)
    edit_box.delete(0, tk.END)
    edit_box.insert(tk.END, file_path)

def set_file_frame(parent_frame, label_text, file_type):
    # フレームの定義
    file_frame = ttk.Frame(parent_frame)

    # フレームのラベル
    tk.Label(file_frame, text = label_text).pack(side = tk.LEFT)

    # テキストボックス
    file_frame.edit_box = tk.Entry(file_frame, width = 50)
    file_frame.edit_box.pack(side = tk.LEFT)

    # ファイル選択ボタン
    file_button = tk.Button(file_frame,
                            text="選択",
                            width=5,
                            command = lambda:open_file_command(file_frame.edit_box, file_type))
    file_button.pack(side = tk.LEFT)

    return file_frame

def convert_obj(land_frame, water_frame):
    # 地形、および水深のパス
    land_path = land_frame.edit_box.get()
    water_path = water_frame.edit_box.get()

    # ファイルの選択確認
    if not os.path.exists(land_path):
        print("地形ファイルを選択してください")
        return 0
    elif not os.path.exists(water_path):
        print("水深ファイルを選択してください")
        return 0
    
    # outputフォルダのリセット
    if os.path.exists("./output"):
        shutil.rmtree("./output")
    os.mkdir("./output")

    # 水位のOBJファイル作成
    wsurf_obj(land_path, water_path, True)

    # 地形のOBJファイル作成
    land_obj(land_path, True)

    print("変換完了")

    return 0

def convert_window():
    # ウィンドウの定義
    root = tk.Tk()
    root.title("計算結果ファイルの指定")
    root.geometry("500x100")

    # 地形ファイル選択
    land_select = set_file_frame(root, "地形ファイル", [("CGNSファイル", "*.cgn")])
    land_select.pack(pady=5)

    # 水深ファイル選択
    water_select = set_file_frame(root, "水深ファイル", [("CGNSファイル", "*.cgn")])
    water_select.pack()

    # 実行ボタン
    convert_button = tk.Button(root, text="変換", width=5, command=lambda:convert_obj(land_select, water_select))
    convert_button.pack(pady=5)

    # ウィンドウの表示
    tk.mainloop()

    return 0

def main():
    # 変換ウィンドウ
    convert_window()

    return 0

if __name__ == "__main__":
    print("-----start-----")
    main()
    print("------end------")
