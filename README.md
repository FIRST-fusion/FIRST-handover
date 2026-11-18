# FIRST 操作指令

## 1. 登入

```sh
ssh ouvic@140.116.16.7
cd /home/ouvic/first-handover-20261118
```

## 2. 準備 input

已有自己的 input，直接用其路徑執行。要從範例修改，先複製到新名稱：

**VMEC**

```sh
mkdir -p inputs
cp -R examples/vmec_lowbeta inputs/my-vmec
nano inputs/my-vmec/input.test
```

**CHEASE**

```sh
mkdir -p inputs
cp -R examples/chease_c50 inputs/my-chease
nano inputs/my-chease/namelist
```

| Solver | 指定的 input | 同資料夾檔案 |
|---|---|---|
| VMEC | `input.test` 或自訂檔名，內容為 `&INDATA` | 本交接範例只需主 input |
| CHEASE | `namelist`，內容為 `&EQDATA`／`$EQDATA` | 依 input 設定準備 `EXPEQ`、`NIN`；上述複製已包含 |

VMEC 範例可修改 `PRES_SCALE=2000` 後存檔執行。

## 3. 執行

**平衡＋五張 profile＋bootstrap＋DCON，一行完成：**

```sh
# VMEC
python3 run_case.py inputs/my-vmec/input.test --bootstrap --dcon

# CHEASE
python3 run_case.py inputs/my-chease/namelist --bootstrap --dcon
```

改完 input、存檔後，重跑同一行即可。每次結果另存新目錄。

以下 `INPUT` 換成你的檔案或資料夾路徑：

| 要執行的項目 | 指令 |
|---|---|
| 平衡＋五圖＋bootstrap＋DCON | `python3 run_case.py INPUT --bootstrap --dcon` |
| 平衡＋五圖＋bootstrap | `python3 run_case.py INPUT --bootstrap` |
| 平衡＋五圖＋DCON（一般自訂 input） | `python3 run_case.py INPUT` |
| 只檢查環境與 input | `python3 run_case.py INPUT --preflight` |

直接跑既有高 bootstrap 範例，含 DCON：

```sh
python3 run_case.py vmec_p80_513 --dcon
python3 run_case.py freep80_high256 --dcon
```

## 4. 參數

| 參數 | 用途 |
|---|---|
| `INPUT` | input 檔案、資料夾或範例名稱；省略則讀目前資料夾。資料夾內使用 `input.test` 或 `namelist`。 |
| `--bootstrap` | 自訂 input 計算 Hirshman bootstrap current／fBS，不做自洽外迭代；研究範例預設已啟用。 |
| `--dcon` | 加跑同一份平衡的 DCON，`n=1`；一般教學流程預設已啟用。 |
| `--timeout SECONDS` | 平衡時限，1–14400秒；一般流程預設300秒，bootstrap流程3600秒。DCON固定300秒。 |
| `--output DIR` | 指定尚不存在的結果目錄；預設自動建立 `runs/<名稱>-<時間戳>/`。 |
| `--preflight` | 只檢查，不計算。 |
| `--solver chease`／`--solver vmec` | 資料夾同時有兩種 input 時指定 solver；其餘自動辨識。 |
| `--input PATH` | 用具名參數代替位置參數 `INPUT`。 |
| `--input-dir DIR` | 指定 input 資料夾；不能與 `--input` 同用。 |
| `--plot-python PYTHON` | 指定繪圖 Python，需 numpy／scipy／matplotlib；ouvic 已備好，通常不用填。 |
| `-h`／`--help` | 顯示參數。 |

例如延長平衡時限並指定結果目錄：

```sh
python3 run_case.py inputs/my-vmec/input.test --bootstrap --dcon --timeout 3600 --output runs/my-result-01
```

## 5. 查看結果

終端機會印出本次結果目錄；開啟其中的檔案：

| 檔案 | 內容 |
|---|---|
| `profiles/overview.png` | 五圖總覽：q、pressure、⟨J·B⟩、極向／環向加權電流 |
| `profiles/profiles.pdf` | 五張圖的 PDF |
| `summary.json` | 執行狀態、`fbs_percent`（百分比）、DCON 各項判斷 |
| `equilibrium/bootstrap.json` | bootstrap 診斷 |
| `dcon/run.log` | DCON 完整輸出 |
| `profiles/profiles.csv`、`profiles/metadata.json` | 繪圖數值與來源檔案 |

[專案目標](docs/PROJECT.md) · [研究 input 清單](research-inputs/bootstrap99/README.md) · [驗收紀錄](evidence/ACCEPTANCE.md)
