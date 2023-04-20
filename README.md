# cgns2obj_nays2dh
iRIC Softwareで計算されたNays2DHの結果ファイル(.cgn)を基に

3Dファイル（.obj）に変換するPythonプログラムです。

# DEMO
（後日追加予定）

# License
MIT
Copyright (c) 2023 Shinsuke Nakamori

# Requirement
- numpy 1.24.2
- pandas 1.5.3
- iRIC_class

# Usage
```
git clone git@github.com:nakamori1024/cgns2obj_nays2dh.git
cd cgns2obj_nays2dh
python cgns2obj_nays2dh.py
```

# Release Note
## v2.0.0
水面のobjファイルは時刻毎の別ファイルではなく、一つのファイルで出力するように変更。

（後方互換性が無いため、v2とする）

Date:2023/04/20
- 水面のobjファイル名を"wsurf.obj"に変更
- *get_f*の引数に「格子点の数」と「ステップ数」を追加
- *wsurf_obj*および*land_obj*にて、格子点の数を導出する式を追加
- *wsurf_obj*にて、objファイル定義部分をステップループの前に移動

## v1.0.0
Date：2023/04/13
- ライセンス付与（MIT）
- Readme作成
