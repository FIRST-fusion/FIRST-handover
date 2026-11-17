# 帳號別實跑驗證

查核日期：2026-11-18。這不是「FIRST 所有 user 都能直接跑」的保證。

| 帳號 | 實際結果 |
|---|---|
| ouvic | 原 runtime 設定四例 reference＋replay 通過，另驗證全新 checkout 兩條流程 |
| ubuntu | 原設定 preflight 因 /home/ouvic 權限而失敗；配置帳號自有、相同 SHA-256 的執行檔副本後，四例實跑與數值等價比對通過 |
| 其他帳號 | 尚未測試，不能由 ubuntu 通過直接外推 |

## ubuntu 的測試位置

`/home/ubuntu/first-handover-validation-20261118`

交接檔直接 rsync 傳入，沒有從 GitHub clone。使用既有 SSH key 分別登入兩帳號：由 ouvic 讀取自己的三個 solver，複製至 ubuntu 目錄的 `licensed-runtime/`；沒有修改 `/home/ouvic` 的750權限，也沒有使用 sudo。副本權限700、owner=ubuntu，沒有把授權程式傳到 GitHub。

- 原配置保存為 `runtime/first.ouvic.json`。
- 此目錄的 `runtime/first.json` 只改三個 `binaries` 路徑。
- image ID、binary SHA-256、案例設定、輸入和公差保持相同。
- Docker 容器實查 user=1000:1000，八個 solver stage 均 exit 0。
- 19項 Python 測試與44份 reference SHA-256檢查通過。

可在 ubuntu 登入後重跑（輸出目錄名稱必須全新）：

```sh
cd /home/ubuntu/first-handover-validation-20261118
python3 tools/run_case.py --preflight
python3 tools/run_case.py vmec_lowbeta --output runs/my-next-vmec
python3 tools/run_case.py chease_c50 --output runs/my-next-chease
```

## 比對如何處理路徑差異

完整 `runtime.sha256` 包含絕對路徑，因此此 ubuntu 副本直接使用原版 `compare.py` 對原 reference 比較，會有 **唯一一項 runtime.sha256 不同**。這不是未加說明就讓原版驗收變綠。

本次額外驗收先確認配置只有 binary 路徑不同、三個 binary 實際 SHA一致、image/case完全相同，再只在記憶體中對齊該路徑配置身分；原始 reference 不寫入、不放寬任何數值公差。四例的數值、input/control hash、reported分類及IEEE警訊全部匹配。實際輸出仍保留ubuntu配置與原始hash。

機器可讀紀錄：[ubuntu_account.json](../evidence/ubuntu_account.json)。遠端 `verify_ubuntu.py` 可重驗本次四個固定輸出；它不是任意新參數的通用驗收工具。

後續為其他獲授權帳號配置時，需由管理者提供可讀的授權 binary／相同 runtime，以及使用者自己的可寫輸出目錄。不要開放整個他人的 home、不把所有人加入 sudo；Docker 使用權本身也需核准。此repository的預設runtime仍是已驗證的ouvic路徑，不會自動搬移或修改權限。

流程重現通過仍不代表科學穩定性通過；DCON浮點警訊全部保留。
