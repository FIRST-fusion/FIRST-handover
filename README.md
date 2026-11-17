# FIRST：可重現的容器實作與專案交接

**接手者先跑得出來，再按需要查理論。** 此 repository 提供兩條獨立流程、四組固定範例、真實參考輸出及自動比對，另附 FIRST 主機管理速查。

- [快速開始：clone → preflight → 執行 → 比對](docs/QUICKSTART.md)
- [CHEASE → DCON、VMEC → DCON：每一步做什麼](docs/WORKFLOWS.md)
- [帳號別驗證：ouvic／ubuntu 與路徑權限限制](docs/MULTIUSER.md)
- [FIRST 主機管理：帳號、磁碟、容器、排程與故障](docs/OPERATIONS.md)
- [老師目標、目前缺口與第一週交接驗收](docs/PROJECT.md)
- [授權與使用範圍](NOTICE.md)
- [本次實跑驗收紀錄](evidence/ACCEPTANCE.md)

## 四個可執行範例

| 名稱 | 路徑 | 輸入 | 本次參考輸出 | 定位 |
|---|---|---|---|---|
| `vmec_lowbeta` | VMEC → DCON | [input.test](examples/vmec_lowbeta/input.test) | [reference](reference/vmec_lowbeta) | 新的簡單低壓軸對稱教學例，建議第一個跑 |
| `vmec_smooth` | VMEC → DCON | [input.test](examples/vmec_smooth/input.test) | [reference](reference/vmec_smooth) | FIRST 歷史平滑電流剖面例 |
| `chease_c50` | CHEASE → DCON | [namelist / EXPEQ / NIN](examples/chease_c50) | [reference](reference/chease_c50) | Lin-Liu 歷史固定輸入快照 |
| `chease_c51` | CHEASE → DCON | [namelist / EXPEQ / NIN](examples/chease_c51) | [reference](reference/chease_c51) | 同一迭代鏈的另一固定輸入快照 |

參考輸出由本次 **2026-11-18 真正執行平衡 solver 與 DCON** 產生；不是拿舊日誌冒充新執行。每條路徑均從其自身輸入開始，不依賴先跑另一條路徑。

## 最短上手（已在 FIRST clone 後）

```sh
python3 tools/run_case.py --preflight
python3 tools/run_case.py vmec_lowbeta --output runs/my-first-vmec
python3 tools/compare.py runs/my-first-vmec/summary.json reference/vmec_lowbeta/expected.json

python3 tools/run_case.py chease_c50 --output runs/my-first-chease
python3 tools/compare.py runs/my-first-chease/summary.json reference/chease_c50/expected.json
```

需要 Linux x86_64、Python 3.10+、Docker、FIRST 的既有授權 runtime。**不是任意機器 clone 後就能下載 solver 的公開套件**：binary 與 image 不在 Git 中；`runtime/first.json` 固定 FIRST 的映像 ID、binary 路徑與 SHA-256。

每次輸出放新目錄；輸入與原 binary 不修改。容器斷網、限制資源，不啟動參數搜尋、不改排程、不刪舊容器。

## 看懂驗收結果

- runner `valid=true`：必要流程、平衡收斂與輸出檢查通過。
- compare `passed=true`：新執行與固定參考的數字、輸入／runtime／設定 hash、分類與警訊一致。
- **上述均不等於物理穩定性證明**。四例只示範 n=1、指定壁面與有限解析度；DCON 既有浮點警訊完整保留，`scientific_acceptance` 明列 NOT_CERTIFIED。
- GitHub CI 只跑 Python 工具測試與檔案雜湊，不在校外執行授權 solver。

reference 約數 MB，提供必要中間檔和輸出；大型影片與不影響判讀的繪圖副產品不重複塞進 repository。舊完整教材仍作為延伸查閱，不是快速入門的必讀前置。
