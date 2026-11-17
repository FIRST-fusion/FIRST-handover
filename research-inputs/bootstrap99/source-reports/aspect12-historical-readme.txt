# 2026-10-28 持續搜尋中：A=1.2 第二穩定區

使用者本日明確要求「運行到找出來為止」。目前尚未取得完整穩定解；不是完成一批就結束目標。最新入口為 [continuation-20261028/CURRENT.md](continuation-20261028/CURRENT.md) 及 [監督程序](continuation-20261028/control/SUPERVISOR.md)。所有舊案例與 main 排程保留。

---

## 以下為 2026-10-27 已結束批次的歷史記錄（不是本日即時狀態）

# A=1.2 高 bootstrap 平衡搜尋 — 2026-10-27

**本輪完成：得到 CHEASE 局部判據通過的新候選，但尚未取得跨求解器一致、完整的穩定證據。**

使用者本日具體授權 plasma 接續搜尋。沒有修改舊 Lin-Liu／FIRST 實驗，沒有接管 main 的 FIRST direct-search，未恢復既有排程，未使用 Nano。本輪所有求解器已結束；只在確認自有容器剩下 sleep 後停止該容器，沒有刪除檔案或容器。

## 實際完成

- 4 個新物理參數點，各 45 次外迭代，共 **180 次初篩外迭代**。
- 兩點粗網格閉合未通過；另兩點通過粗網格／原生 ballooning 初篩，但加密後閉合超標。這些不等於已確認物理不穩定。
- 對第一點做 **25 次細映射自洽修正**，再用完全相同 EXPEQ 重求 NS320、NPSI1024、NTNOVA1024、9 個 ballooning 相位。
- 最終 CHEASE 候選通過兩組加密 DCON 局部檢查；配對 VMEC2049 正常收斂，完成 3 組預設與 2 組 classic-spline DCON 對照。
- 已獨立核對 7 份完整 DCON 剖面與原始 VMEC NetCDF；本輪負結果與原始輸出均保留。

## 最佳 CHEASE 候選

`p6_s033_c050_fine_exact320`

| 量 | 結果 |
|---|---:|
| R0 / a / A | 0.45 m / 0.375 m / 1.2 |
| B0（真空參考環向場） | 1 T |
| κ / 幾何 δ | 2.4000 / 0.4795，FIRST Fourier 邊界 |
| 全域 fBS（Hirshman 電流分解） | 99.288578% |
| βvac | 15.187458% |
| βN | 5.602794 |
| Ip | 1.016510111 MA |
| 近軸 q / qedge | 2.752316 / 66.453297 |
| 外層閉合殘差 | 0.00034208592，門檻 < 1e-3 |

A=1.2 是長寬比，不是理想壁 b/a。有限 n 若續作，既定設定為同形理想壁 b/a=1.05；不是已確認的真實真空室。

## 檢查結果

| 檢查 | 實際結果 |
|---|---|
| CHEASE 力平衡與閉合 | 通過；NS128/NS320 閉合均約 3.4e-4 |
| 原生 ballooning | NS320：1025 磁面 × 9 相位，0 個不穩定面 |
| CHEASE→DCON G768，ψN∈[1e-4,1.0] | 769/769 面完成，零 ballooning crossing，完整 Mercier 通過 |
| CHEASE→DCON G1536，同區間 | 1537/1537 面完成，零 crossing，完整 Mercier 通過 |
| VMEC 2049 / MPOL48 / clustered1601 | 正常完成，ier_flag=0；最大力殘差 9.999e-12 |
| VMEC 電流／bootstrap 配對 | Ip=1.016496789 MA，與 CHEASE 相差 0.00131%；fBS=99.287075%，βvac=15.187526% |
| VMEC→DCON 預設，G1024/edge .999 與 1.0 | 每組只有 1015/1025 面積分；10 面正 Mercier，未通過 |
| VMEC→DCON 預設，G1536/edge .999 | 1523/1537 面積分；14 面正 Mercier，未通過 |
| VMEC→DCON classic，G1024/G1536、edge 1.0 | 同樣缺 10/14 面，Mercier 警訊仍在 |
| 有限 n=1,2,3 固定／自由邊界 | **未執行**；未越過配對局部判據門檻 |
| 整體結論 | **尚未驗證穩定；不能據此認定物理解不存在** |

## 真正卡住的位置

VMEC→DCON 的正 Mercier 指標位於 **ψpol,N≈0.0002504–0.0007798**，最大 D_I≈17.05。完整表中這些面恰好是 ballooning 積分表缺少的面，因此只看成功積分列的「Mercier stable」會誤導。原始 log 亦有 divide-by-zero/underflow/denormal 訊號；正常退出不是通過。

由原始 `wout_test.nc` 獨立重算，VMEC 第一個非軸原生點在 **ψpol,N=0.0026147103**，整個警訊區內沒有原生網格點。DCON 加密與 classic-spline 對照均無法補足這段原生平衡解析度。這是近軸離散／轉接問題的具體線索，**不是已證明的數值假象，也不能刪去近軸區間來宣稱穩定**。

合理的下一個獨立工作包：核對 VMEC→DCON Fourier／半網格轉接與近軸正則性，做可控的原生徑向解析度收斂；確認兩個求解器一致後，再進入 n=1–3 能量表與網格／諧波收斂。這些尚未執行，沒有背景續跑或新排程。

## 必須保留的另一個數值反例

細映射迭代的預設 `NTNOVA=128` 不等同 `NPSI=1024`；該版本在 G1536 曾有 ψ≈0.95112 的 ballooning crossing。最後同 EXPEQ 的 NS320/NTNOVA1024 對照沒有該零點。NS 與輸出角向解析度同時改變，不能單獨歸因於其中一項。

## 證據入口

- [4 點參數與初篩 CSV](initial_scan.csv)
- [方法、座標、單位與門檻](METHODS.md)
- [初篩證據 SHA256](evidence/initial_scan_complete/sha256.json)
- [細映射自洽及原始 DCON](validation/evidence/fine_complete/fine_state.json)
- [最終 CHEASE 與兩組 DCON](validation/evidence/refinement_complete/refinement_result.json)
- [VMEC 配對與三組預設檢查](validation/evidence/cross_complete/cross_state.json)
- [兩組 classic-spline 對照](validation/evidence/cross_complete/diagnostic_state.json)
- [64 份交叉驗證檔案的 SHA256](validation/evidence/cross_complete/sha256.json)
- [本機獨立原始資料稽核](evidence/cross_independent_audit.json)
- [CHEASE 近軸 Mercier 圖](figures/chease_mercier_near_axis.png) / [PDF](figures/chease_mercier_near_axis.pdf)
- [VMEC 近軸 Mercier 圖](figures/vmec_mercier_near_axis.png) / [PDF](figures/vmec_mercier_near_axis.pdf)
- [閉合修正前後圖](figures/closure_correction.png) / [PDF](figures/closure_correction.pdf)
- [程序歸屬及結束狀態](validation/evidence/runtime.json) / [實際收尾證據](validation/evidence/settlement.json)

## 重現與範圍

- 初篩遠端：`140.116.16.7_ouvic:/home/ouvic/aspect12-stability-20261027`
- 驗證遠端：`140.116.16.7_ouvic:/home/ouvic/aspect12-validation-20261027`
- 原始參考：`/home/ouvic/linliu-reproduction-20260911`，保持唯讀使用；自有容器中 `/study`、`/source` 均唯讀掛載。
- 所有案例拒絕覆寫，writer 使用 flock 與明確 PID／出生識別。部分大檔保留遠端，另有大小及雜湊記錄。
- `src/`、`validation/src/` 保存程式；以 execution/owner/state 與原始 log 判定是否實際執行。`cross_after_fine.py`、`extra_local_controls.py` 等部分準備稿未執行。
- 本機數值稽核／畫圖使用 `/opt/anaconda3/bin/python3`；遠端使用原專案 `.venv_uv/bin/python`。不因不同 PATH 的缺套件訊息重裝環境。
- n=0、真實壁／PF 線圈、電阻性、碰撞及非線性不在本輪認證範圍。

更新時間（UTC）：2026-10-27T10:49:41.868229+00:00
