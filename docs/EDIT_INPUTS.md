# 改自己的 input，再跑出結果

**可以修改，也可以放入自己的新 input。** 原範例只是保留作對照；工作時使用 `inputs/` 裡的可編輯副本。以下指令在 FIRST 交接目錄執行：

```sh
cd /home/ouvic/first-handover-20261118
```

## 最簡單：建立一次，之後改檔＋跑一行

### 1. 建立自己的 VMEC 案例（只複製，不計算）

```sh
python3 tools/case.py init my-vmec --from vmec_lowbeta
```

### 2. 開啟 `inputs/my-vmec/input.test`，修改並存檔

例如把 `PRES_SCALE=2000` 改成 `PRES_SCALE=1500`。可用 VS Code Remote SSH，或：

```sh
nano inputs/my-vmec/input.test
```

`nano` 存檔：Ctrl+O、Enter；離開：Ctrl+X。

### 3. 每次改好後，只執行這一行

```sh
python3 tools/case.py run my-vmec
```

自動完成 **新目錄 → 複製當次 input → 求解 → 五張 profile → DCON**。終端機會列出本次輸出路徑。再改一次、再跑同一行即可；新結果自動使用時間戳，不覆寫上一輪，也不覆寫可編輯的 input。

- 開 `runs/my-vmec-<時間戳>/profiles/overview.png`：五圖總覽。
- 開同目錄 `profiles/profiles.pdf`：五頁圖。
- `equilibrium/input.test`：本次真正拿去算的輸入快照。
- `summary.json`：收斂、當次輸入 SHA-256、診斷、圖檔路徑與錯誤。

**修改後的結果本來就可能不同，不要拿原範例的 `expected.json` 要求它數字相同。** comparator 會明確拒絕把自訂案例當原始範例驗收。未收斂會失敗，不會假裝出圖成功；若平衡完成、後續 DCON 失敗，已生成的平衡圖仍保留，但整條流程 `valid=false`。

## 換成 CHEASE 或高 bootstrap 起點

| 想用的起點 | 建立指令 | 編輯位置 | 修改後執行 |
|---|---|---|---|
| CHEASE 教學 | `python3 tools/case.py init my-chease --from chease_c50` | `inputs/my-chease/namelist`、`EXPEQ`、`NIN` | `python3 tools/case.py run my-chease` |
| CHEASE p80 | `python3 tools/case.py init my-p80 --from freep80_high256` | `inputs/my-p80/namelist`、`EXPEQ`、`NIN` | `python3 tools/case.py run my-p80` |
| VMEC p80 | `python3 tools/case.py init my-vmec-p80 --from vmec_p80_513` | `inputs/my-vmec-p80/input.test` | `python3 tools/case.py run my-vmec-p80` |

四個教學起點：平衡＋五圖＋DCON。十四個研究起點：平衡＋五圖＋**重新計算 fBS**，**不跑 DCON、不做 bootstrap 自洽外迭代**。`case.json` 記錄所選起點，讓工具選擇對應的 solver／binary／診斷流程；不是把舊 input 偷偷拿回來算。

高 bootstrap 只是初始範例的特性；修改壓力、電流或形狀後，**fBS 以新結果為準，不預設仍為 99%**。自訂結果的 `historical_fbs`、`fbs_difference` 為 null，不沿用歷史成功判定。

## 要改哪個檔、哪個參數？

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

## 放入自己新寫的 input

最方便的方式：先 `init` 一個相同 solver 的案例，再以自己的檔案替換其中的 input；不用登錄 manifest、不用更新參考雜湊。VMEC 檔案固定命名 `input.test`；CHEASE 為 `namelist`，及該設定實際需要的 `EXPEQ/NIN`。

已經有 input 資料夾也可直接指定，不必先 `init`：

```sh
python3 tools/run_case.py vmec_lowbeta --input-dir /home/ouvic/my-inputs
python3 tools/run_bootstrap_case.py freep80_high256 --input-dir /home/ouvic/my-chease-inputs
```

這裡案例名只選 **solver／runtime／診斷流程**，實際資料來自 `--input-dir`。後者使用 highres CHEASE；不要把需要 highres 的 restart 交給教學 standard binary。只支援本交接的固定邊界、軸對稱工作流，不保證任意外部 VMEC/CHEASE 輸入格式或額外 runtime 都可直接使用。

## 常用選項與錯誤

```sh
python3 tools/case.py run my-vmec --preflight  # 檢查環境和 input，不計算
python3 tools/case.py run my-vmec --timeout 600
python3 tools/case.py run my-vmec --output runs/my-vmec-trial01
```

- `init` 的目錄已存在：直接編輯它，不要再次 init；需要新案例就換名字。
- 自訂 `--output` 已存在：改新名字，或省略讓工具自動取名。
- input 缺檔／收斂設定無法讀取：補正後再跑。數值 namelist 支援逗號、換行、D exponent、重複值及單一索引；需為每個有效 VMEC grid 明列 tolerance。
- 對應原理與圖中單位：[PROFILES.md](PROFILES.md)。原始範例重播：[QUICKSTART.md](QUICKSTART.md)。

## 已實際驗證，不只是操作示意

本次在FIRST改過上述三種輸入並重新求解：VMEC壓力得到0.75倍、CHEASE壓力得到0.95²倍、p80壓力得到0.99倍；p80的新fBS為98.7676%，不是原來99.1695%。[查看實跑圖與收據](../evidence/editable_inputs/README.md)。
