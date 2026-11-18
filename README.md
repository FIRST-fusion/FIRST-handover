# FIRST 交接：改 input、執行、看結果

**日常操作看這一頁即可。** 可以用範例建立自己的 input，也可以換成自己寫的檔案；每次執行都保存新結果及五張 profile 圖。

## 1. 登入與進入專案

```sh
ssh ouvic@140.116.16.7
cd /home/ouvic/first-handover-20261118
```

這個目錄已備好工具。需有 FIRST 帳號與既有 solver 的使用權限；其他帳號的設定見頁末「首次安裝」。

## 2. 選起點，建立自己的案例（只做一次）

第一次建議用簡單的 VMEC：

```sh
python3 tools/case.py init my-case --from vmec_lowbeta
```

要換起點，替換 `--from` 後面的名稱；要另開案例，將 `my-case` 換成新名字。

| 想做什麼 | `--from` 名稱 | 要編輯的檔案 | 執行內容 |
|---|---|---|---|
| VMEC 入門，建議先選 | `vmec_lowbeta` | `input.test` | 平衡＋五圖＋DCON |
| CHEASE 入門 | `chease_c50` | `namelist`、`EXPEQ`、`NIN` | 平衡＋五圖＋DCON |
| CHEASE 高 bootstrap p80 | `freep80_high256` | `namelist`、`EXPEQ`、`NIN` | 平衡＋五圖＋重算 fBS |
| VMEC 高 bootstrap p80 | `vmec_p80_513` | `input.test` | 平衡＋五圖＋重算 fBS |

另有教學例 `vmec_smooth`、`chease_c51`；其他研究起點見[研究案例表](research-inputs/bootstrap99/README.md)。高 bootstrap 路徑**不跑 DCON、不做自洽外迭代**；改過 input 後不保證仍有 99%。

## 3. 修改 input 並存檔

檔案都在 `inputs/my-case/`。可以用 VS Code Remote SSH 開啟，也可以：

```sh
nano inputs/my-case/input.test
```

VMEC 最簡單的練習：把 `PRES_SCALE=2000` 改成 `PRES_SCALE=1500`，觀察壓力曲線。`nano` 存檔按 Ctrl+O、Enter，離開按 Ctrl+X。

CHEASE 則編輯同目錄的 `namelist` 等檔案；例如 `B0EXP=1.` 改成 `.95` 是磁場尺度練習。形狀／剖面是否生效還取決於 restart 與輸入選項，不能只改任意一個數字。詳細欄位集中在[輸入參數與流程](docs/WORKFLOWS.md#input-reference)。

**自己的新 input 也能使用**：先選同 solver 的起點，再替換副本中的檔案。VMEC 命名為 `input.test`；CHEASE 使用 `namelist` 及所需的 `EXPEQ/NIN`。原範例保留作對照，不必修改 manifest 或參考雜湊。

## 4. 每次改好後，只執行這一行

```sh
python3 tools/case.py run my-case
```

工具會使用你現在的 input，將當次快照及結果放進 `runs/my-case-<時間戳>/`。**之後再改檔、再跑同一行即可，不用再次 init，也不會覆寫上一輪。**

常用選項：

```sh
python3 tools/case.py run my-case --preflight  # 只檢查環境與input
python3 tools/case.py run my-case --timeout 600
```

教學例預設每個 solver 階段300秒，高 bootstrap 平衡預設3600秒。每個容器最多2 CPU／8 GB、單執行緒，不需要 GPU；順序執行即可。

## 5. 跑完看這些檔案

終端機會顯示本次結果目錄；在 VS Code Remote SSH 開啟其中的 `profiles/overview.png` 就能看圖。

| 結果目錄內的位置 | 內容 |
|---|---|
| `profiles/overview.png` | **五圖總覽：q、pressure、⟨J·B⟩、極向／環向加權電流** |
| `profiles/profiles.pdf` | 五頁圖；同目錄另有各張 PNG／PDF |
| `profiles/profiles.csv`、`metadata.json` | 逐點數值、來源檔、SHA-256 與單位換算 |
| `equilibrium/` | 本次實際 input、求解輸出及 `run.log` |
| `summary.json` | 是否完成、錯誤、診斷、圖檔路徑；研究案例另有 `fbs_percent` |
| `dcon/` | 教學路徑的 DCON 設定與診斷；研究路徑沒有此步驟 |

`fbs_percent=98.7676` 就是 **98.7676%**；`fbs_total_hirshman=0.987676` 是比例。兩張電流圖是加權剖面 [A]，不是局部電流密度；完整來源和定義見[圖表說明](docs/PROFILES.md)。

`valid=true` 代表流程檢查通過，**不代表物理穩定**。修改後不應要求與舊範例數字相同。高 bootstrap 案例的 fBS 會重新計算；缺少 closure seed 時不宣稱閉合通過。

### 遇到問題

- `init` 說目錄已存在：直接編輯原副本，或換新案例名。
- 自選 `--output` 已存在：換名字，或省略讓工具自動命名。
- 未完成：先看 `summary.json` 的 `error`、`equilibrium/run.log`；出圖錯誤看 `profiles.log`。未收斂不算成功。
- 平衡完成但 DCON 失敗：平衡圖仍會保留，整條流程仍標為失敗。
- 只有出圖失敗：保留計算結果，按[圖表說明](docs/PROFILES.md)單獨重畫，不必重跑 solver。
- SSH 中斷：先核對該次輸出與容器狀態，不直接重送。

<details>
<summary>已有自己的 input 資料夾，想直接指定</summary>

```sh
python3 tools/run_case.py vmec_lowbeta --input-dir /home/ouvic/my-inputs
python3 tools/run_bootstrap_case.py freep80_high256 --input-dir /home/ouvic/my-chease-inputs
```

案例名選擇 solver／runtime／診斷流程，實際 input 來自指定資料夾。研究 CHEASE 使用 highres binary；不要拿教學 standard binary 讀高解析度 restart。本交接支援固定邊界、軸對稱流程，不保證任意外部輸入所需的額外 runtime 都已備妥。

</details>

<details>
<summary>首次安裝、原始範例重播與工具測試</summary>

需要 FIRST Linux x86_64、Python ≥3.10、Docker 與授權 binary/image。solver 不在 Git，也不會自動下載。其他帳號先查[帳號與權限](docs/MULTIUSER.md)；私人 GitHub 認證使用組織核准方式，不把 token 寫進 URL。

```sh
git clone https://github.com/FIRST-fusion/FIRST-handover.git
cd FIRST-handover
python3 tools/check_reference.py
python3 tools/run_case.py --preflight
```

ouvic 已有科學 Python；其他環境須具備 `requirements-plot.txt` 的套件，可用 `--plot-python /path/to/python` 指定。binary、image 與 hash 由 `runtime/first.json` 記錄。

只想原封不動重跑與比對基準：

```sh
python3 tools/run_case.py vmec_lowbeta --output runs/replay-01
python3 tools/compare.py runs/replay-01/summary.json reference/vmec_lowbeta/expected.json
```

原始高 bootstrap 重播可用 `python3 tools/run_bootstrap_case.py freep80_high256`。`--output` 必須是新目錄；不要對自訂 input 使用原始 reference 驗收。

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
