# FIRST 交接：改 input、執行、看結果

**日常操作看這一頁即可。** 可以用範例建立自己的 input，也可以換成自己寫的檔案；每次執行都保存新結果及五張 profile 圖。

## 1. 登入與進入專案

```sh
ssh ouvic@140.116.16.7
cd /home/ouvic/first-handover-20261118
```

這個目錄已備好工具。需有 FIRST 帳號與既有 solver 的使用權限；其他帳號的設定見頁末「首次安裝」。

## 2. 已有自己的 input：直接執行

**只用 `run_case.py`，不需要先 init、不需要範例名稱，也不需要 case.json。**

```sh
# VMEC：可以指定任何檔名，內容須為 &INDATA
python3 run_case.py /home/ouvic/my-inputs/input.test

# CHEASE：指定 namelist；需要的 EXPEQ/NIN 放同一資料夾
python3 run_case.py /home/ouvic/my-chease/namelist

# 也能直接指定資料夾（內有 input.test 或 namelist）
python3 run_case.py /home/ouvic/my-inputs
```

上面的路徑請換成你自己的檔案。工具按 **input 內容**辨識 CHEASE／VMEC，會先印出實際讀取的完整路徑。資料夾若同時有兩種 input，請直接指定其中一個檔案。指定 `input.mine` 時會讀它，不會偷換成同資料夾的舊 `input.test`。

檔案在其他位置也沒問題：可以從任意目錄用 `python3 /home/ouvic/first-handover-20261118/run_case.py /你的/input路徑` 執行。

## 3. 還沒有 input：複製一份範例，再修改

第一次建議使用 VMEC lowbeta。以下 `my-vmec` 請選一個尚未存在的新資料夾名：

```sh
mkdir -p inputs
mkdir inputs/my-vmec && cp examples/vmec_lowbeta/input.test inputs/my-vmec/
nano inputs/my-vmec/input.test
```

例如把 `PRES_SCALE=2000` 改成 `PRES_SCALE=1500`。`nano` 存檔按 Ctrl+O、Enter，離開按 Ctrl+X；也能用 VS Code Remote SSH 編輯。之後每次存檔，只跑這行：

```sh
python3 run_case.py inputs/my-vmec/input.test
```

CHEASE 可複製 `examples/chease_c50/` 的 `namelist`、`EXPEQ`、`NIN` 到自己的新資料夾，再直接指定 namelist 執行。形狀／剖面是否生效取決於 restart 與輸入選項，詳細欄位見[輸入參數](docs/WORKFLOWS.md#input-reference)。

原始範例留作對照。你可以任意編輯自己的副本、替換成新 input；不用更新 manifest 或參考雜湊。

## 4. 選擇診斷與執行選項

直接指定一般自訂 input，預設做 **平衡＋五張 profile＋教學 DCON**，**不執行額外的 bootstrap 診斷**。要計算 Hirshman bootstrap current 與其總電流比例，同一個入口加上 `--bootstrap`：

```sh
python3 run_case.py inputs/my-vmec/input.test --bootstrap
```

**同一次執行也要 DCON 檢驗**，再加上 `--dcon`：

```sh
python3 run_case.py inputs/my-vmec/input.test --bootstrap --dcon
```

這條指令只求**一次平衡**，從該次輸出產圖、計算 bootstrap，並把同一份平衡介面送入 DCON；不是分別求兩個不同平衡。原始研究範例也能用 `python3 run_case.py vmec_p80_513 --dcon`。

| 執行方式 | 平衡與五圖 | Bootstrap 診斷／fBS | DCON |
|---|---|---|---|
| 一般自訂 input，未加 `--bootstrap` | 有 | 不執行 | 有 |
| 自訂 input 加 `--bootstrap` | 有 | 從本次平衡重新計算 | 不執行 |
| 自訂 input 加 `--bootstrap --dcon` | 有，只求一次平衡 | 從本次平衡重新計算 | 有，同一份平衡介面 |
| 直接指定高 bootstrap 研究範例名稱 | 有 | 從本次平衡重新計算 | 不執行 |
| 高 bootstrap 研究範例名稱加 `--dcon` | 有，只求一次平衡 | 從本次平衡重新計算 | 有，同一份平衡介面 |

**Bootstrap 診斷不等於自洽電流求解。** 它計算本次平衡對應的 bootstrap current 與 fBS，不沿用舊的99%，但**不會把 bootstrap current 回灌給 solver 反覆求平衡**。目前五張圖中的電流仍是**總電流剖面**，尚未另外繪製 bootstrap current 剖面；有五張圖不代表已跑 bootstrap。

**DCON 的檢驗範圍：** 加上 `--dcon` 會執行既有教學設定（環向模數 `n=1`、`mpsi=mtheta=128`、正規化極向磁通範圍 `1e-4–0.99`、固定壁面設定），不是 n 掃描或解析度收斂研究。保留原始穩定／不穩定標籤與浮點警訊；流程完成不等於已證明物理穩定，也不能只由 fBS 判斷穩定。未加 `--dcon` 的 bootstrap-only 模式仍不做 DCON。

若資料夾保留先前建立的 `case.json`，工具會沿用其中選定的教學／研究流程；舊副本不必重建。執行時終端機會印出 `workflow`，可確認本次選用的流程。

只想跑原始範例，也用同一個入口：

| 起點 | 指令 | 內容 |
|---|---|---|
| VMEC 入門 | `python3 run_case.py vmec_lowbeta` | 平衡＋五圖＋DCON |
| CHEASE 入門 | `python3 run_case.py chease_c50` | 平衡＋五圖＋DCON |
| CHEASE 高 bootstrap p80 | `python3 run_case.py freep80_high256` | 平衡＋五圖＋重算 fBS |
| VMEC 高 bootstrap p80 | `python3 run_case.py vmec_p80_513` | 平衡＋五圖＋重算 fBS |

另有 `vmec_smooth`、`chease_c51` 及[研究案例表](research-inputs/bootstrap99/README.md)中的起點。

```sh
python3 run_case.py inputs/my-vmec/input.test --preflight  # 只檢查，不計算
python3 run_case.py inputs/my-vmec/input.test --timeout 3600
```

DCON路徑的平衡預設300秒，bootstrap路徑平衡預設3600秒；高解析度自訂input可用 `--timeout` 加長平衡時間。DCON階段固定300秒。每個容器最多2 CPU／8 GB、單執行緒，不需要GPU。直接讀CHEASE檔案且沒有既有案例設定時，使用較大容量的highres build。

每次都把當次 input 快照與新結果放進 `runs/<案例或資料夾名>-<時間戳>/`。**再次修改後跑同一行即可，不會覆寫上一輪。**

<details>
<summary>run_case.py 完整參數（args）速查</summary>

日常只需 `python3 run_case.py INPUT`；需要 bootstrap 時加 `--bootstrap`，兩項診斷一起做則加 `--bootstrap --dcon`。其餘參數按需使用：

| 參數 | 用途／預設 |
|---|---|
| `INPUT`（位置參數，help 中名為 `case`） | input 檔案、資料夾或範例名稱；省略則讀目前工作資料夾的 `input.test`／`namelist`。 |
| `--bootstrap` | 自訂 input 加入 Hirshman bootstrap／fBS；單獨使用不跑 DCON，可搭配 `--dcon`。不做自洽外迭代。研究範例原本就有 bootstrap；教學範例若要使用此選項，請指定其 input 路徑而非僅填範例名。 |
| `--dcon` | 在 bootstrap／研究流程加跑同一份平衡的 DCON（`n=1`），不重跑平衡。一般教學流程原本就有 DCON，加此參數不會重複執行。 |
| `--output DIR` | 指定**尚不存在**的結果目錄；省略則在專案 `runs/` 自動建立時間戳目錄。 |
| `--timeout SECONDS` | 平衡求解時限，整數 1–14400 秒；教學流程預設300秒，bootstrap流程預設3600秒。不改變 DCON 固定300秒時限。 |
| `--preflight` | 只做輸入／runtime／依賴檢查，不求解、不產圖；不指定 input 時可單獨檢查 runtime 與繪圖依賴。 |
| `--solver chease` 或 `--solver vmec` | 資料夾同時有兩種 input 時選擇 solver；通常可省略並自動辨識，指定值必須與 input 內容一致。 |
| `--input PATH` | 用具名參數指定 input 檔或資料夾，與直接填 `INPUT` 二選一即可。 |
| `--input-dir DIR` | 相容舊操作的 input 資料夾選項；新操作建議直接填路徑。不能與 `--input` 同時使用。 |
| `--plot-python PYTHON` | 指定具有 numpy／scipy／matplotlib 的繪圖 Python。ouvic 預設使用既有 `.venv_uv/bin/python`，找不到時用啟動 runner 的 Python；此選項不切換 bootstrap 診斷所用的既有科學 Python。 |
| `-h`、`--help` | 顯示程式實際支援的參數後離開。 |

例如自己的高解析度 input 要算 bootstrap 並給一小時：

```sh
python3 run_case.py inputs/my-vmec/input.test --bootstrap --dcon --timeout 3600
python3 run_case.py --help
```

</details>

## 5. 跑完看這些檔案

終端機會顯示本次結果目錄；在 VS Code Remote SSH 開啟其中的 `profiles/overview.png` 就能看圖。

| 結果目錄內的位置 | 內容 |
|---|---|
| `profiles/overview.png` | **五圖總覽：q、pressure、⟨J·B⟩、極向／環向加權電流** |
| `profiles/profiles.pdf` | 五頁圖；同目錄另有各張 PNG／PDF |
| `profiles/profiles.csv`、`metadata.json` | 逐點數值、來源檔、SHA-256 與單位換算 |
| `equilibrium/` | 本次實際 input、求解輸出及 `run.log` |
| `equilibrium/bootstrap.json` | bootstrap 流程的診斷、方法、來源雜湊與 fBS；一般教學流程不產生此檔 |
| `summary.json` | 是否完成、錯誤、診斷、圖檔路徑；bootstrap 流程另有 `fbs_total_hirshman` 與 `fbs_percent` |
| `dcon/` | 教學流程或研究流程加 `--dcon` 時的 DCON 介面副本、設定與診斷 |

`fbs_percent=98.7676` 就是 **98.7676%**；`fbs_total_hirshman=0.987676` 是比例。兩張電流圖是加權剖面 [A]，不是局部電流密度；完整來源和定義見[圖表說明](docs/PROFILES.md)。

整合流程的 `summary.json` 會分開記錄 `bootstrap_audit.completed` 與 `dcon.completed`。`dcon.reported_free` 只是 DCON 的自由邊界判斷，固定邊界／Mercier／ballooning 結果見 `labels` 的 `dcon.reported_*`，浮點警訊見 `warnings`。`dcon` 內另有來源介面、副本與控制檔的 SHA-256，供核對是否使用同一次平衡。失敗或未執行的步驟不能當成 stable。

`valid=true` 代表流程檢查通過，**不代表物理穩定**。修改後不應要求與舊範例數字相同。高 bootstrap 案例的 fBS 會重新計算；缺少 closure seed 時不宣稱閉合通過。

### 遇到問題

- `找不到 input`：核對你指定的路徑；不要把示範的 `/home/ouvic/my-inputs` 原樣當成自己的檔案。
- `python3: can’t open file ...run_case.py`：先進入本專案目錄，或使用上面的完整 script 路徑。
- 範例副本已存在：直接編輯，不必再次複製。
- 自選 `--output` 已存在：換名字，或省略讓工具自動命名。
- 未完成：先看 `summary.json` 的 `error`、`equilibrium/run.log`；出圖錯誤看 `profiles.log`。未收斂不算成功。
- 平衡完成但 DCON 失敗：平衡圖仍會保留，整條流程仍標為失敗。
- 整合流程中某項診斷失敗：保留已完成的 bootstrap／DCON 結果與五圖，整體 `valid=false`；不把其中一項成功當成兩項都通過。
- 只有出圖失敗：保留計算結果，按[圖表說明](docs/PROFILES.md)單獨重畫，不必重跑 solver。
- SSH 中斷：先核對該次輸出與容器狀態，不直接重送。

<details>
<summary>舊指令與相容範圍</summary>

`tools/run_case.py` 與根目錄 `run_case.py` 使用相同程式。舊的 `case.py init/run`、範例名稱加 `--input-dir` 仍保留相容，但新操作只需使用本頁的 `run_case.py`。

支援本交接的固定邊界、軸對稱輸入，不保證任意外部input所需的額外runtime都已備妥。資料夾自動辨識使用 `input.test`／`namelist`；其他檔名請直接指定檔案。CHEASE的EXPEQ/NIN仍按該input設定準備，不是省略它們也一定能算。

</details>

<details>
<summary>首次安裝、原始範例重播與工具測試</summary>

需要 FIRST Linux x86_64、Python ≥3.10、Docker 與授權 binary/image。solver 不在 Git，也不會自動下載。其他帳號先查[帳號與權限](docs/MULTIUSER.md)；私人 GitHub 認證使用組織核准方式，不把 token 寫進 URL。

```sh
git clone https://github.com/FIRST-fusion/FIRST-handover.git
cd FIRST-handover
python3 tools/check_reference.py
python3 run_case.py --preflight
```

ouvic 已有科學 Python；其他環境須具備 `requirements-plot.txt` 的套件，可用 `--plot-python /path/to/python` 指定。binary、image 與 hash 由 `runtime/first.json` 記錄。

只想原封不動重跑與比對基準：

```sh
python3 run_case.py vmec_lowbeta --output runs/replay-01
python3 tools/compare.py runs/replay-01/summary.json reference/vmec_lowbeta/expected.json
```

原始高 bootstrap 重播可用 `python3 run_case.py freep80_high256`。`--output` 必須是新目錄；不要對自訂 input 使用原始 reference 驗收。

不執行 solver 的本機工具檢查：

```sh
python3 -m venv .venv-plot
.venv-plot/bin/python -m pip install -r requirements-plot.txt
.venv-plot/bin/python -m unittest discover -s tests -v
python3 tools/check_reference.py
python3 tools/check_research_inputs.py
```

</details>

## 需要時再查

- [輸入參數、執行流程與數值驗收](docs/WORKFLOWS.md) · [圖表來源與換算](docs/PROFILES.md)
- [研究案例與 fBS 定義](research-inputs/bootstrap99/README.md) · [實跑證據與圖](evidence/ACCEPTANCE.md)
- [主機管理](docs/OPERATIONS.md) · [研究目標與待辦](docs/PROJECT.md) · [授權範圍](NOTICE.md)
