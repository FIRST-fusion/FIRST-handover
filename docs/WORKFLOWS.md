# 兩條獨立流程：輸入、執行、輸出

本套件教的是 **固定輸入 → 真正跑 solver → 檢查收斂 → 新產生介面 → 真正跑 DCON → 比對參考**，不是把保存的 INP1／dcon_test.txt 直接當成這次平衡求解結果。兩條路徑不是互相轉換，也不是相同物理平衡的跨 solver 驗證。

```mermaid
flowchart LR
  C[CHEASE: namelist + EXPEQ + NIN] --> CR[CHEASE 容器求平衡]
  CR --> CI[本次新產生 INP1]
  CI --> CD[DCON 容器 n=1]
  V[VMEC: input.test] --> VR[VMEC 容器求平衡]
  VR --> VI[本次新產生 dcon_test.txt]
  VI --> VD[DCON 容器 n=1]
  CD --> A[summary + 原始輸出 + 比對]
  VD --> A
```

## CHEASE → DCON

範例 `chease_c50`、`chease_c51` 分別來自已封存的 `cl50_000`、`cl50_001`。兩者是同一歷史迭代鏈中不同的固定剖面快照，不是兩個已完成 bootstrap 自洽的穩定解。

- `namelist`：NS=NT=64、NPSI=200、NTNOVA=128、NOPT=-2、EPSLON=1e-10。
- `EXPEQ`：邊界及剖面輸入；`NIN`：restart，不可少。二進位採 FIRST 的 `chease_linliu.x`（有 Lin-Liu 診斷修改），不是聲稱原廠未修改版。
- CHEASE 容器使用 Ubuntu 22 runtime；由 stdin 讀 namelist。
- `run.log`：末次 RESIDU 應不超過 EPSLON，且須有 MKSA 摘要；不能只看 exit 0。
- 新生成 `INP1` 是 Fortran 二進位介面；保留原始 bytes，不用文字編輯器改它。
- DCON 在另一個 Ubuntu 20 runtime 讀 `eq_type="chease"` 與該 INP1。

容器內實際執行的兩個命令（掛載由 runner 準備，勿在原始碼目錄直接跑）：

```sh
# CHEASE container, cwd=/work
exec timeout 300 /opt/solver < namelist
# DCON container, cwd=/work
exec timeout 300 /opt/solver
```

## VMEC → DCON

- `vmec_lowbeta`：本交接新寫的簡單軸對稱、固定邊界、低壓教學輸入；R=1.5m、水平半徑0.5m、垂直半徑0.65m。不是老師 A≈1.2 的目標案例。
- `vmec_smooth`：歷史 `vmec_smooth225/input.test`。電流形狀源於舊平滑處理流程；沒有在本次執行 bootstrap，自洽性不在本例保證範圍。
- 兩者 NTOR=0。FIRST 的 PARVMEC 9.0 patch 才會輸出本套 DCON 介面，不能任意換 upstream VMEC。
- `input.test` → `wout_test.nc`（平衡）、`threed1.test`（診斷）、`dcon_test.txt`（DCON 介面）。
- 最後一層網格的 FSQR、FSQZ、FSQL 都須達到指定容差，並檢查正常結束與 aborting；`ier_flag=0` 本身不足以證明收斂。
- DCON 讀 `eq_type="vmec"` 和新生成的 `dcon_test.txt`。

```sh
# VMEC container, cwd=/work
exec timeout 300 /opt/solver input.test
# DCON container, cwd=/work
exec timeout 300 /opt/solver
```

完整 docker 命令、映像 ID、binary SHA、exit code、耗時都記錄在每次 `summary.json` 的 `stages` 與 `runtime`。兩個階段使用獨立工作目錄與新容器；`dcon/` 的介面檔是從本次 `equilibrium/` 複製，不是從 reference 複製。

## 共同 DCON 條件與限制

- DCON 3.80 既有 binary；n=1，hamada Jacobian，mpsi=mtheta=128。
- psilow=1e-4、psihigh=.99；不是完整磁軸與最邊界驗證。
- delta_mlow=8、delta_mhigh=12；tol_nr=tol_r=1e-8；singfac_min=1e-3、ucrit=10。
- vac.in 保留 ishape=6 的既有 conformal-wall 設定、a=0.2；**不是 no-wall 結論**。幾何細節以保存的 vac.in 及此版本來源為準。
- n=2、3、解析度加密、壁面掃描、完整 ballooning 面覆蓋、bootstrap 閉合與第二穩定分支都不在此小型入門驗收中。

## 「跑對」與「穩定」是兩個答案

`valid=true` 僅表示本套流程必要輸出與門檻通過；`compare.py` 通過再表示與保存的數值／標籤一致。`scientific_acceptance` 一律明列 NOT_CERTIFIED。

DCON 的 `reported_*` 是程式印出的判斷，不是交接者重新證明的物理結論。此版本會留下 IEEE_DIVIDE_BY_ZERO／OVERFLOW／UNDERFLOW 等旗標；旗標會保存並納入比對，不隱藏。若無明確固定邊界判斷字串，`reported_fixed` 是 unknown，不把沒有印 unstable 當成 stable。

NaN／Inf、缺檔、殘差不達標、timeout、ODE 錯誤使工具失敗。對原版有限但有警訊的輸出，本套允許做**可重現的流程教學**，不允許稱「已驗證穩定」。欲取得科學結論，另做數值警訊追因、完整磁面與原生解析度驗證。

## 調整參數時

日常建立／修改／執行步驟統一見[交接首頁](../README.md)。直接用 `run_case.py` 指定自己的 input 檔案／資料夾，runner 保存當次 input hash；原始 examples/reference 保留作對照。提高 β、變更電流／壁面／模式數會改變物理問題；放寬 FTOL 或比對容差不是修復。此 repository 不自動啟動參數搜尋。

各程式的 beta 定義／正規化可能不同。`equilibrium.beta_vac` 是 CHEASE 的 B0 真空場正規化量；`dcon.betat`、`dcon.betan` 是該版 DCON 診斷，不可把不同路徑的 beta 數字直接當成研究成果排名。參考例的高 βN 不代表達成老師 A≈1.2／高bootstrap／第二穩定分支的聯合目標。

<a id="input-reference"></a>

## 輸入參數參考


### VMEC：`input.test`

- `PRES_SCALE`：壓力整體倍率；lowbeta 範例使用 `AM=1,-1`，因此原本軸壓力為 2000 Pa，改為1500可看到壓力曲線改變。未列出的 `PRES_SCALE` 可在 `&INDATA` 之後加入；p80 的 spline 壓力資料不需要一起改。
- `AM`／`AM_AUX_S`、`AM_AUX_F`：依壓力 profile 類型決定函數或 spline 資料，不可混用。
- `NCURR=0` 時使用 `AI` 或 `AI_AUX_*` 指定 rotational transform；不要誤以為改 `AC` 就一定會生效。
- `RBC`、`ZBS`：邊界形狀；`PHIEDGE`：總環向磁通。
- `NS_ARRAY`、`MPOL`、`FTOL_ARRAY`：解析度與收斂要求。工具讀取最後有效 `NS_ARRAY` 對應的 `FTOL_ARRAY`，不是沿用範例公差。

### CHEASE：`namelist`、`EXPEQ`、`NIN`

- `namelist`：求解控制、解析度 `NS/NT/NPSI/NCHI`、收斂 `EPSLON`、物理尺度 `R0EXP/B0EXP`，以及 profile／restart 的選擇。
- `EXPEQ`：邊界與 profile 資料；不是任意文字表格，請保留格式和點數。
- `NIN`：此批範例的 restart 資料。**改 namelist 的某個形狀數字，不保證啟用 restart／外部邊界時就會採用它**；要同時理解 `NOPT/NSURF/NFUNC/NPPFUN` 等選項及實際輸入來源。
- 最小尺度練習：`B0EXP=1.` 改成 `.95`，檢查新圖中的 SI 壓力與電流。這是尺度修改，不等於改出另一個無因次壓力形狀。

自訂 CHEASE 的 `bootstrap-settings.json` 若為 `{}`，表示**未指定 closure seed**，`closure_below_1e-3=null`。要評估指定 seed 的閉合，明確填入三個數值 `seed_axis`、`seed_center`、`seed_width`（width > 0）；A=1.2 起點會複製其既有 seed 供你檢視修改。這不會自動調整平衡到自洽。


數值 namelist 支援逗號、換行、D exponent、重複值及單一索引；VMEC 每個有效 grid 都需明列 tolerance。不支援的索引／slice 會報錯，不會忽略後繼續執行。

## 比對與失敗判讀

原始範例 `compare.py` 比較輸入／runtime／控制檔 hash、分類與數值；公差為 `abs(actual-reference) <= atol + rtol*abs(reference)`，主要量目前 rtol=5e-4、atol=1e-8，以各 `expected.json` 為準。殘差另外檢查收斂門檻，不要求列印的最後一位相同。自訂 input 不適用原始 reference，工具會明確拒絕混用。

平衡收斂後先出五圖，再做 DCON 或 bootstrap audit；`run_case.py INPUT --bootstrap --dcon` 可從同一次平衡做兩項診斷，研究範例用 `run_case.py CASE --dcon`。這不會回灌bootstrap反覆求自洽，DCON仍為既有教學n=1設定。後處理失敗仍保留已完成診斷、圖及原始輸出，但整體 `valid=false`。比對失敗不可自行更新 reference 或放寬容差。`profiles.log`、`equilibrium/run.log`、`dcon/run.log` 與 `summary.json` 應一起保留。
