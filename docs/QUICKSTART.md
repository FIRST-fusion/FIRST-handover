# 快速入門：在 FIRST 跑出自己的結果

## 前置條件

- 已獲授權的 FIRST/NCKU 帳號、SSH、Docker 存取及本私人 GitHub repository 的讀取權限。
- 在 FIRST Linux x86_64 執行，Python ≥3.10；runner 使用標準函式庫，自動出圖另需 NumPy／SciPy／Matplotlib。ouvic 預設使用已安裝套件的 `/home/ouvic/linliu-reproduction-20260911/.venv_uv/bin/python`，不需安裝或更動系統環境。其他帳號可用 `--plot-python /path/to/python` 指定自己的環境（依賴見 `requirements-plot.txt`）；preflight 會先查核。
- `runtime/first.json` 所列既有映像及 binary 仍在。新帳號還須有讀取 binary 的權限；沒有就由主機管理者依授權配置，不用 sudo 硬繞過。
- 不在 Mac 或 GitHub Actions 跑 solver。repository 沒有包含 solver，也不會自動下載／安裝它們。

```sh
ssh ouvic@140.116.16.7
# 在個人的新目錄 clone；下面目錄如已存在，選新名稱，不覆寫。
git clone https://github.com/FIRST-fusion/FIRST-handover.git
cd FIRST-handover
python3 tools/check_reference.py
python3 tools/run_case.py --preflight
```

私人 repo 的 GitHub 認證使用組織核准方式，不將 token 寫進 URL、shell history 或教材。`--preflight` 只查核主機、映像 ID 與 binary SHA，不啟動計算。

## 1. 先跑簡單的 VMEC → DCON

```sh
python3 tools/run_case.py vmec_lowbeta --output runs/my-vmec-lowbeta
python3 tools/compare.py runs/my-vmec-lowbeta/summary.json reference/vmec_lowbeta/expected.json
```

## 2. 再跑 CHEASE → DCON

```sh
python3 tools/run_case.py chease_c50 --output runs/my-chease-c50
python3 tools/compare.py runs/my-chease-c50/summary.json reference/chease_c50/expected.json
```

## 3. 另外兩個固定範例

```sh
python3 tools/run_case.py chease_c51 --output runs/my-chease-c51
python3 tools/compare.py runs/my-chease-c51/summary.json reference/chease_c51/expected.json
python3 tools/run_case.py vmec_smooth --output runs/my-vmec-smooth
python3 tools/compare.py runs/my-vmec-smooth/summary.json reference/vmec_smooth/expected.json
```

順序執行，不需要平行開四個。每個 solver 階段 timeout 300 秒；每個容器最多2 CPU、8GiB RAM，BLAS/OpenMP單執行緒，停用網路、來源二進位唯讀掛載。DCON 不需要 GPU。

**輸出目錄必須不存在**。要再跑一次請用新名稱（例如 my-vmec-lowbeta-02），工具不覆寫、不刪舊資料。SSH 中斷先核對自己的具名容器與輸出，不直接重送。

## 4. 看哪些檔案？

上述每條 runner 指令完成後，**自動從本次新平衡產生五張 profile**，終端機會列出 `profiles.overview` 與 `profiles.pdf` 的完整路徑。不是複製 reference 圖。用 VS Code Remote SSH 的檔案總管打開 `profiles/overview.png` 可看到五圖總覽，或下載 `profiles/profiles.pdf` 看五頁圖；不需要在主機開瀏覽器或新增服務。

```text
runs/my-case/
├── equilibrium/
│   ├── run.log            平衡求解的原始 stdout/stderr
│   ├── INP1               CHEASE 新輸出的 DCON 介面（CHEASE 案例）
│   ├── wout_test.nc       VMEC 平衡（VMEC 案例）
│   ├── threed1.test       VMEC 診斷（VMEC 案例）
│   └── dcon_test.txt      VMEC 新輸出的 DCON 介面（VMEC 案例）
├── dcon/
│   ├── equil.in / dcon.in / vac.in   實際使用的設定
│   ├── run.log / dcon.out           原始診斷
│   └── INP1 或 dcon_test.txt        從此次平衡複製的介面
├── profiles/
│   ├── overview.png / overview.pdf     五張圖總覽
│   ├── q.png / pressure.png / jdotb.png
│   ├── poloidal_current.png / toroidal_current.png
│   ├── profiles.pdf                   五頁圖（各單圖另有 PDF）
│   └── profiles.csv / metadata.json   逐點值、來源路徑與 SHA-256
├── profiles.log           出圖命令的 stdout/stderr
└── summary.json           實際命令、exit、耗時、hash、指標、警訊與圖檔路徑
```

`reference/<case>/` 提供對應的真實輸出節選與完整 stdout/stderr，不只是一張摘要表。大型繪圖／中間副產品不放入 Git；原始完整 run 保留在 FIRST 隔離驗證目錄。`evidence/reference_manifest.json` 記錄節選檔 SHA-256 與來源位置。

## 5. 何謂通過？

1. runner 結束碼0、summary 的 valid=true：指定的收斂、輸出、非有限數與錯誤檢查通過。
2. compare 結束碼0、JSON passed=true：輸入／runtime／控制檔摘要與分類相同，關鍵數字在固定公差內。
3. 公差定義 `abs(actual-reference) <= atol + rtol*abs(reference)`；目前主要物理／診斷量 rtol=5e-4、atol=1e-8。日誌數字有列印精度限制。殘差另外依輸入門檻檢查，不要求不同執行的最後一位殘差相等。
4. 必須讀 warnings。**流程通過不等於平衡物理穩定**；本套已知 DCON 浮點警訊保留在 expected labels 中，不因正常結束而忽略。

比對失敗先確認沒有更換 binary、image、輸入或設定，保留兩份 summary 與 log 交給維護者；不要自動更新 reference 或放寬容差。

若 solver 已完成但出圖失敗，整個 runner 仍回傳非零、`valid=false`，保留全部計算輸出與 `profiles.log`；修復後只用 [PROFILES.md](PROFILES.md) 的獨立繪圖命令讀該次輸出，指定新的圖目錄，不必重跑 solver。

## 無 FIRST 的本機檢查

完整測試包含繪圖，需在有 `requirements-plot.txt` 套件的 Python 環境執行；例如：

```sh
python3 -m venv .venv-plot
.venv-plot/bin/python -m pip install -r requirements-plot.txt
.venv-plot/bin/python -m unittest discover -s tests -v
python3 tools/check_reference.py
```

這只驗證工具與已保存資料的完整性，不代表本機跑過 solver。GitHub CI 也只做這些檢查。
