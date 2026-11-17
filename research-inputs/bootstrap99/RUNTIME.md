# 研究輸入的執行條件

這批是歷史輸入封裝，**不是已註冊到 `tools/run_case.py` 的新增範例**。四個入門範例仍使用原本固定 runtime、參考輸出與 300 秒限制，不要為了讀取這批輸入而覆蓋它們。

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

## 接手者如何使用或改值

1. 先用 [快速開始](../../docs/QUICKSTART.md) 完成一組已驗收的教學流程，確認自己的帳號與容器權限。**ubuntu 的四個入門案例已跑過，不代表這 14 組高解析度研究案例也已在 ubuntu 跑過。**
2. 將所選案例的整個 `inputs/` 複製到自己的新工作目錄。保留原包不動；CHEASE 必須一起帶 `namelist`、`EXPEQ`、`NIN`，VMEC 帶 `input.test`。
3. 依上表核對實際可讀的 executable、hash、image 與容量；如果在 ubuntu 使用 highres CHEASE，需另取得該授權 binary 的可讀副本。先前的 ubuntu 教學副本只有標準 CHEASE，不可拿來替代。
4. 第一輪先不改值，保留 solver stdout、退出狀態、收斂與輸出。容器內 CHEASE 的基本入口為 `/opt/solver < namelist`，VMEC 為 `/opt/solver input.test`；`/opt/solver` 是唯讀掛載的正確 executable，工作目錄需可寫。這是入口說明，不是完整、已驗收的研究 runner。
5. 比對 `historical/summary.json` 的 β、q、電流、解析度及收斂，使用相同 Hirshman 稽核重算 fBS／閉合。歷史摘要不是自動比較用的 `reference/*/expected.json`，不得直接餵給教學 comparator 冒充新通過。
6. 需要 DCON 時另建各 n／壁面的工作目錄。p80 的三份原設定可作起點，但必須更新 `equil.in` 的平衡輸出路徑、確認 GPEC_balnorm 版本與磁面覆蓋。A=1.2 有限 n 結果不能借用 p80 的輸出。
7. 再修改自己的副本：CHEASE 數值控制在 `namelist`，壓力／電流／邊界主要在 `EXPEQ`；VMEC 在 `input.test`。改物理剖面後重做 bootstrap 閉合與穩定性，不沿用舊 fBS 或舊穩定標籤。

不把 `NBSOPT` 改為某個值來「設定 99%」。A=1.2 的 seed 與壓力公式保存在 [原始摘要](cases/p6_s033_c050_fine_exact320/historical/summary.json) 及 [pressure_model](cases/p6_s033_c050_fine_exact320/historical/pressure_model.json)；重建時同時核對磁通座標、單位與 seed 定義。

本次沒有啟動任何新平衡、DCON 或參數搜尋；所有時間與數值均為歷史證據。
