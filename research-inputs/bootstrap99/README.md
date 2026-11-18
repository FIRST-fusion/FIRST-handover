# 約 99% bootstrap current 的歷史研究輸入

**14 組已找到的平衡輸入：10 組 CHEASE、4 組 VMEC。** 2026-11-18 從 FIRST 原始研究目錄取回，保留輸入原始位元組、必要 restart、歷史結果與 SHA-256。本目錄保存歷史資料；後續只對 p80 配對及修改案例做了新實跑，**不是重新驗收全部14組或認證穩定性**，見[實跑證據](../../evidence/ACCEPTANCE.md)。

[回交接首頁](../../README.md) · [完整來源與雜湊](manifest.json) · [執行條件及調參注意](RUNTIME.md)

**所有建立案例、修改 input、執行與看圖的步驟統一在[交接首頁](../../README.md)。** 本頁只保留研究案例、物理定義與歷史限制。

## 先看這兩對

- **A=1.4／較低 β 分支**：[CHEASE p80](cases/freep80_high256/inputs) → [配對 VMEC513](cases/vmec_p80_513/inputs)，fBS 約 99.16%／99.17%。兩者各附歷史 n=1、2、3、壁面 b/a=1.2 的 DCON 設定、日誌及摘要。
- **A=1.2／老師目標的候選**：[CHEASE exact320](cases/p6_s033_c050_fine_exact320/inputs) → [配對 VMEC2049](cases/vmec_p6_s033_c050_fine_exact320_2049/inputs)，fBS 約 99.29%，βN 約 5.60。VMEC→DCON 的近軸問題未解、有限 n=1–3 尚未完成，不是已證明的第二穩定區。

## 案例索引

| 案例（點選取得輸入） | Solver | A | fBS [%] | βvac [%] | NS |
|---|---|---:|---:|---:|---:|
| [freep80_high256](cases/freep80_high256/inputs) | CHEASE | 1.4 | 99.160292 | 36.838307 | 256 |
| [freep80_high320_phase9](cases/freep80_high320_phase9/inputs) | CHEASE | 1.4 | 99.160335 | 36.838270 | 320 |
| [freep90_high256_phase9](cases/freep90_high256_phase9/inputs) | CHEASE | 1.4 | 99.465158 | 44.755893 | 256 |
| [freep98_high256_phase9](cases/freep98_high256_phase9/inputs) | CHEASE | 1.4 | 99.612084 | 51.847865 | 256 |
| [freep98_high320_phase9](cases/freep98_high320_phase9/inputs) | CHEASE | 1.4 | 99.612133 | 51.847821 | 320 |
| [free54_refined](cases/free54_refined/inputs) | CHEASE | 1.4 | 99.616444 | 53.773235 | 128 |
| [free54_high256](cases/free54_high256/inputs) | CHEASE | 1.4 | 99.616060 | 53.773101 | 256 |
| [free54_high320](cases/free54_high320/inputs) | CHEASE | 1.4 | 99.616112 | 53.773055 | 320 |
| [vmec_p80_513](cases/vmec_p80_513/inputs) | VMEC | 1.4 | 99.169525 | 36.838335 | 513 |
| [vmec_p98_513](cases/vmec_p98_513/inputs) | VMEC | 1.4 | 99.621140 | 51.847885 | 513 |
| [vmec_selfconsistent513](cases/vmec_selfconsistent513/inputs) | VMEC | 1.4 | 99.625381 | 53.773445 | 513 |
| [p6_s033_c050_fine128_024](cases/p6_s033_c050_fine128_024/inputs) | CHEASE | 1.2 | 99.290589 | 15.187460 | 128 |
| [p6_s033_c050_fine_exact320](cases/p6_s033_c050_fine_exact320/inputs) | CHEASE | 1.2 | 99.288578 | 15.187458 | 320 |
| [vmec_p6_s033_c050_fine_exact320_2049](cases/vmec_p6_s033_c050_fine_exact320_2049/inputs) | VMEC | 1.2 | 99.287075 | 15.187526 | 2049 |

βvac 是以真空參考場定義的體積平均 β，不是 βN。NS 為各 solver 自身的徑向設定，不代表兩者有相同磁通座標。A=1.4 的幾何為 R0=1 m、B0=1 T、κ=3、δ=0.5；A=1.2 為 R0=0.45 m、a=0.375 m、B0=1 T、κ≈2.4、δ≈0.4795。不能只按 β 大小排名。

## 檔案怎麼看

- `cases/<案例>/inputs/`：CHEASE 的 `namelist + EXPEQ + NIN`；VMEC 的 `input.test`。**NIN 是原始 restart，不能漏掉或用其他案例任意替換。**
- `cases/<案例>/historical/`：原始 `summary.json`、`run.log`，以及存在時的 bootstrap 稽核、電流剖面、幾何轉接與解析度設定。歷史摘要中的 `valid=true` 不是本次重跑成功，也不是完整穩定。
- p80 兩個案例的 `historical/dcon_n*_w0.2_g512_s5_robust/`：三個 n 的 `equil.in / dcon.in / vac.in / run.log / summary.json`。原設定中的絕對路徑只作來源記錄，重跑必須指向自己的新平衡輸出。
- `source-reports/`：歷史研究報告與獨立稽核快照；`.txt` 中的舊連結、執行指示、當時狀態不是本次任務或即時狀態。
- `manifest.json`：逐檔來源、大小、雜湊及案例摘要。CHEASE 閉合殘差以 `closure_field` 標明來源；A=1.2 採符合該案例 seed 的 `closure_fixed_seed`，不得誤用 default-seed 診斷。

這是**精選輸入＋關鍵歷史輸出**，不是所有大檔的完整備份；例如 `wout_test.nc` 與完整 mapping 留在 manifest 指向的 FIRST 原研究目錄。新跑時自行產生，不要假裝已隨 Git 收錄。

## 0.99 到底代表什麼

本表取 `fbs_total_hirshman`，是 collisionless Hirshman 電流分解得到的**全域積分比例** `fBS = 1 − Iaux / Ip`；不是加權近似值 `fbs_weighted_hirshman`，也不是輸入裡把某個開關設成 0.99。

CHEASE 這批使用 `NBSOPT=0`：bootstrap 自洽由外部迭代完成，存下來的是迭代後壓力／電流剖面。**單跑一次保存的平衡輸入不等於重新做 bootstrap 自洽。** 改壓力、seed、邊界後，必須重新迭代、重新算 fBS 與閉合殘差；原先的 99% 不會自動保留。`p80/p90/p98` 是原分支的壓力梯度幅度標記，不是 bootstrap 百分比。

這套 fBS 診斷採 Zeff=2、pe=pi、Te=Ti 與指定梯度假設，依原方法處理 diamagnetic／Pfirsch–Schlüter 部分；不是通用輸運模型。CHEASE 從本次 `linliu_profiles.dat` 重新積分；VMEC 從本次 `wout_test.nc` 的 Fourier／Jacobian 重新計算。VMEC 的 `Iaux_A/Itotal_A` 是安培，CHEASE 原始 `itotal` 是正規化電流，不可直接標為安培。

讀新執行的 `summary.json`：`fbs_percent` 為百分比，`fbs_total_hirshman` 為比例；例如0.9916029189等於99.16029189%，不是0.9916%。自訂 input 的 `historical_fbs/fbs_difference` 為 null；VMEC 的 `closure_below_1e-3=null` 表示沒有固定 seed 閉合認證。CHEASE 自訂 seed 規則見[輸入參數參考](../../docs/WORKFLOWS.md#input-reference)。

## 跨 solver 的來源配對

| VMEC | 真正的 CHEASE parent |
|---|---|
| `vmec_p80_513` | `freep80_high256` |
| `vmec_p98_513` | `freep98_high256_phase9` |
| `vmec_selfconsistent513` | **`free54_refined`**，不是 high256/high320 |
| `vmec_p6_s033_c050_fine_exact320_2049` | `p6_s033_c050_fine_exact320` |

CHEASE 剖面使用 poloidal-flux 相關座標；VMEC 使用 normalized toroidal flux。重建剖面時必須沿用轉換，不能直接以相同橫軸索引替換。

## 穩定性邊界：高 bootstrap ≠ 完整穩定

- **p80**：已有指定近壁 b/a=1.2、n=1–3 的 CHEASE／VMEC 有限正能量歷史結果；CHEASE 九相位局部加密對照較完整。但不能外推成全部 n、無壁或已消除 VMEC 近軸警訊。
- **p90／p98**：壁面 b/a=1.3 有負能量或未通過品質篩選的模式；局部穩定也不能替代有限 n 的檢查。
- **free54**：βvac≈53.77%、fBS≈99.62%，高 n 邊緣 ballooning 未通過；近壁 n=1–5 的正能量不是完整穩定證明，n=6 timeout 是未知。
- **A=1.2**：CHEASE 局部檢查通過；VMEC→DCON 仍有近軸 Mercier 警訊與缺失磁面。第二穩定區及有限 n=1–3 尚未驗收。

詳見 [Lin–Liu 數值表](source-reports/linliu-numerical-tables.txt)、[研究結論](source-reports/linliu-results.txt)、[A=1.2 歷史報告](source-reports/aspect12-historical-readme.txt) 與 [獨立稽核](source-reports/aspect12-independent-audit.json)。

## 只檢查交接檔案完整性（不執行 solver）

在 repository 根目錄：

```sh
python3 tools/check_research_inputs.py
```

成功只代表輸入／歷史證據未損毀且索引與原始摘要一致；不是新的數值重現驗收。
