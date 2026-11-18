# 研究輸入的 runtime 參考

日常操作統一見[交接首頁](../../README.md)。研究路徑預設執行平衡＋五圖＋bootstrap audit；加 `--dcon` 可對同一份平衡執行既有教學 DCON（n=1），不重跑平衡。`run_case.py` 接受研究起點名稱；自己的 input 加 `--bootstrap --dcon` 即可一次做兩項診斷，單獨 `--bootstrap` 保留不跑DCON的模式，舊 `case.json` 亦可沿用。實跑範圍與限制以[驗收紀錄](../../evidence/ACCEPTANCE.md)為準；流程完成不等於穩定認證。

## 與入門範例不同之處

| 項目 | 研究案例所需條件 |
|---|---|
| CHEASE 容量 | NS256/320 及高解析度 restart 需要 highres build。標準教學 binary 不能直接視為相容；restart 可能在新網格轉換前就讀入。 |
| CHEASE executable | FIRST `/home/ouvic/linliu-reproduction-20260911/src_highres/chease_linliu.x`；SHA-256 `6c69f71a88605b9d6963a5f474316393018648a183dcfbf20c7c227eecbd221b`。A=1.2 exact320 的原摘要直接記錄此 hash；A=1.4 的 build 記錄見歷史 reproduction manifest。 |
| VMEC executable | FIRST `/home/ouvic/workspace/ESTCombo/Stellarator-Tools/build/_deps/parvmec-build/xvmec`；SHA-256 `af9851222f1418b43642d02576fa4067757aada16a546ef9e8129a5745599938`。 |
| DCON 版本 | 本包 p80 的 DCON 摘要標記 `gpec_balnorm`，不是教學 runner 的 classic DCON。歷史 binary 為 `/home/ouvic/linliu-reproduction-20260911/reference/GPEC_balnorm/bin/dcon`，SHA-256 `8647117100daaba0369f30248f2aef632433fda36ff04a229e811f3fbeaff3a3`。 |
| 歷史映像 | reproduction manifest 記錄 tools image `sha256:fb45041b0fd94cfff4458f7d019629317c62429c31c77863e9b9587039f975bf`，VMEC image `sha256:018ecc40f0f336be7bc46eba3f86166877701ecda4433dc4a5d75546cfada8d6`；這是歷史記錄，不是本次新增容器實跑證明。 |
| 時間 | CHEASE NS320 歷史約 491–618 秒，VMEC2049 約 1,346 秒；教學版 300 秒 timeout 不適用。硬體與資源限制不同時可能更久。 |
| 輸出 | CHEASE mapping / VMEC `wout_test.nc` 必須由該案例新產生，再交給相容的 DCON；不能使用其他案例的中間檔。 |

來源：[historical reproduction manifest](source-reports/linliu-reproduction-manifest.json)、[exact320 summary](cases/p6_s033_c050_fine_exact320/historical/summary.json)。程式與 image 均未加入 Git；使用範圍仍依 [NOTICE](../../NOTICE.md)。

## 現行 runner 與帳號限制

- CHEASE highres 使用 image `sha256:641ae18660a48900fa8ad7340f9fbc2f716b2bf2295ef382344590194400a708`；VMEC 使用上表的 `018ecc…` image。每次建立斷網、唯讀 rootfs 的新容器，binary 唯讀掛載，只有新工作目錄可寫。
- 每容器2 CPU／8 GB、BLAS/OpenMP單執行緒，使用執行帳號的UID/GID；完整命令、image ID及binary hash保存在新 `summary.json`。
- ouvic 後處理使用既有 `/home/ouvic/linliu-reproduction-20260911/.venv_uv/bin/python`，不安裝系統套件。
- **ubuntu 的教學例通過，不代表14組研究案例也在 ubuntu 驗證過。** highres CHEASE仍須取得授權及讀取權限；標準教學binary不能代替。
- 研究runner預設timeout3600秒；2026-11-18 p80實測CHEASE約225秒、VMEC約97秒，僅solver階段，不含出圖／稽核，不保證每次相同。
- 如需研究DCON，另用匹配的版本、新平衡介面、各n／壁面設定及完整磁面檢查。p80歷史GPEC_balnorm設定不能直接換成教學classic DCON後沿用研究結論；A=1.2不能借用p80的結果。

A=1.2 的 seed 與壓力公式保存在[原始摘要](cases/p6_s033_c050_fine_exact320/historical/summary.json)及[pressure_model](cases/p6_s033_c050_fine_exact320/historical/pressure_model.json)；需核對磁通座標、單位與seed。單次平衡重播不等於重新做bootstrap自洽，也不會把NBSOPT某個值當成「設定99%」。
