# 在 ouvic 跑高 bootstrap 案例，並讀取 fBS

**先選 `freep80_high256`。** 新增 `tools/run_bootstrap_case.py` 接受本包 14 組固定輸入，只做一次容器內平衡求解，再由主機既有 Python 科學環境重新計算 bootstrap 比例。它不執行參數搜尋、bootstrap 外迭代或 DCON，不修改原案例。

## 1. 登入與檢查（不求解）

```sh
ssh ouvic@140.116.16.7
cd /home/ouvic/first-handover-20261118
python3 tools/run_bootstrap_case.py freep80_high256 --preflight
```

已在此交接目錄放好新增工具，不必先 clone。`preflight_passed=true` 代表 host、image、binary／診斷原碼 hash、輸入 hash 與 Python 依賴檢查通過；不代表已重跑平衡。

## 2. 執行 CHEASE，然後自動重算 bootstrap

```sh
python3 tools/run_bootstrap_case.py freep80_high256 --output runs/my-p80-01
```

輸出目錄不得已存在；再次執行請改成 `my-p80-02`，不要刪舊資料。原機的平衡計算歷史約 4 分鐘，預設 timeout 為 3,600 秒，可用 `--timeout` 指定。輸入被複製到新目錄，不會修改 archive。

完成時會自動從這次新平衡畫出 **q、pressure、⟨J·B⟩、極向／環向加權電流** 五圖，終端機顯示 `valid`、`fbs`、`percent` 及 `profiles.overview`／`profiles.pdf` 路徑。資料結構：

```text
runs/my-p80-01/
  summary.json                 ← 新執行狀態、fBS、與歷史值的差、容器命令
  profiles/overview.png        ← 五圖總覽，VS Code Remote SSH 可直接開啟
  profiles/profiles.pdf        ← 五頁圖，可下載閱讀
  profiles/*.png / *.pdf       ← 五張單圖與總覽
  profiles/profiles.csv        ← 每個繪圖點的數值
  profiles/metadata.json       ← 本次來源檔路徑、SHA-256、單位與換算
  profiles.log                 ← 繪圖日誌
  equilibrium/
    namelist / EXPEQ / NIN      ← 本次實際使用的輸入
    run.log / linliu_profiles.dat / INP1 / ...
    bootstrap.json             ← 從本次剖面重新積分的結果
```

若失敗，讀新目錄 `summary.json` 的 `error` 與 `equilibrium/run.log`；不使用 historical 摘要補成成功。`valid=true` 僅代表平衡與有限值診斷完成，還需看 fBS 範圍、閉合、數值差異；不等於 DCON 或穩定性通過。

出圖套件使用主機既有科學 Python；`--preflight` 也會檢查繪圖依賴，可用 `--plot-python` 指定另一個環境。若只在出圖階段失敗，保留 solver 結果，依 [PROFILES.md](../../docs/PROFILES.md) 單獨重畫到新目錄，不必重跑求解。

## 3. 看 bootstrap current ratio

```sh
python3 - <<'PY'
import json
from pathlib import Path
s = json.loads(Path('runs/my-p80-01/summary.json').read_text())
if not s['valid']:
    raise SystemExit(s.get('error', '本次執行未完成'))
print('bootstrap ratio =', s['fbs_total_hirshman'])
print('bootstrap [%]   =', s['fbs_percent'])
print('與歷史 fBS 差值 =', s['fbs_difference'])
print('閉合 < 1e-3     =', s['bootstrap']['closure_below_1e-3'])
PY
```

`fbs_total_hirshman=0.9916029189` 即 **99.16029189%**。不要讀成 0.9916%，也不要改讀 `fbs_weighted_hirshman`。

定義為 **`fBS = 1 − Iaux / Ip`**：先由磁場幾何與壓力梯度計算 collisionless Hirshman bootstrap，再做全域環向電流分解。這套研究採 Zeff=2、pe=pi、Te=Ti 與指定梯度假設，並依原方法處理 diamagnetic／Pfirsch–Schlüter 部分；不是通用輸運模型，也不是 namelist 的 0.99 開關。

CHEASE 的 `linliu_profiles.dat` 含此修改版 solver 輸出的 Hirshman 診斷；Python 對新剖面做電流積分。VMEC 則從新 `wout_test.nc` 的 Fourier／Jacobian 重新計算，並輸出有安培單位的 `Iaux_A`、`Itotal_A`。原始 CHEASE `itotal` 是正規化電流，不能直接標成安培。

## 4. 換成 VMEC，或 A=1.2

每行是各自獨立的固定輸入平衡，不需先跑上一行：

```sh
# A=1.4，VMEC513：歷史 fBS≈0.991695247
python3 tools/run_bootstrap_case.py vmec_p80_513 --output runs/my-vmec-p80-01

# A=1.2，CHEASE320：歷史 fBS≈0.992885781
python3 tools/run_bootstrap_case.py p6_s033_c050_fine_exact320 --output runs/my-a12-chease-01

# A=1.2，VMEC2049：歷史 fBS≈0.992870751；歷史約22分鐘
python3 tools/run_bootstrap_case.py vmec_p6_s033_c050_fine_exact320_2049 --output runs/my-a12-vmec-01
```

所有案例皆從新執行的 `summary.json` 讀相同欄位。VMEC 的 `closure_below_1e-3=null` 代表此獨立 audit **沒有**做固定 seed 的閉合認證，不能當作通過。

| 案例 | 歷史 fBS | 歷史百分比 |
|---|---:|---:|
| CHEASE p80 | 0.9916029188592947 | 99.160292% |
| VMEC p80 | 0.9916952468332592 | 99.169525% |
| CHEASE A=1.2 exact320 | 0.9928857809614291 | 99.288578% |
| VMEC A=1.2 2049 | 0.9928707512415073 | 99.287075% |

這些是歷史參考值，不保證新環境逐位元一致。若只想查舊值、不想計算：

```sh
python3 - <<'PY'
import json
from pathlib import Path
m = json.loads(Path('research-inputs/bootstrap99/manifest.json').read_text())
for c in m['cases']:
    print(c['case'], '歷史 fBS =', c['fbs_total_hirshman'],
          '百分比 =', 100*c['fbs_total_hirshman'])
PY
```

## 5. 到底用了哪個容器？

- CHEASE：每次建立新容器，image `sha256:641ae18660a48900fa8ad7340f9fbc2f716b2bf2295ef382344590194400a708`，唯讀掛載 **highres** `chease_linliu.x` 為 `/opt/solver`，執行 `/opt/solver < namelist`。
- VMEC：新容器使用 image `sha256:018ecc40f0f336be7bc46eba3f86166877701ecda4433dc4a5d75546cfada8d6`，執行 `/opt/solver input.test`。
- 容器使用 ouvic 的 UID/GID、2 CPU／8 GB、單執行緒、斷網、唯讀 rootfs；新工作目錄可寫。容器名稱與完整命令保存在 `summary.json` 的 `stages`，不依賴正在使用的研究容器。
- Python 只是啟動器及後處理；真正解平衡的是容器內 Fortran executable。後處理使用主機既有 `/home/ouvic/linliu-reproduction-20260911/.venv_uv/bin/python`，不安裝新套件。

## 6. 哪些事這個工具不做？

- 不重新做 bootstrap 外迭代；它重播保存的自洽終點，並檢查結果。改壓力／電流／形狀後不能沿用原 99%。此入口鎖定原始輸入雜湊，改 archive 會被拒絕；自訂剖面需要獨立新案例與相應 seed 設定。
- 不執行 DCON。fBS 不需要 DCON 才能算；但判斷 MHD 穩定仍需另做 DCON 與解析度／磁面覆蓋驗證。p80 的 GPEC_balnorm 設定已附，不能替換成教學 classic DCON 後沿用研究結論。
- A=1.2 使用 `.33 / .05 / .03` 的 seed 軸值／中心／寬度；工具依原 metadata 算 `closure_fixed_seed`，保留但不誤用 legacy default-seed 診斷。

**2026-11-18 遠端實跑驗證**：已在 ouvic 新目錄實際完成 `freep80_high256`（CHEASE 約 225 秒）與 `vmec_p80_513`（VMEC 約 97 秒），並重新計算 bootstrap、自動出五圖。fBS 分別為 **99.1602918859%**、**99.1695246833%**；兩者均與各自歷史值一致。計時僅 solver 階段，不含前置檢查與出圖。其餘 12 組仍只有既有 preflight／歷史後處理驗證，本次未重跑。

- 本次 CHEASE 圖：`runs/profile-accept-20261118-freep80_high256/profiles/overview.png`
- 本次 VMEC 圖：`runs/profile-accept-20261118-vmec_p80_513/profiles/overview.png`
- [實跑總覽圖](../../evidence/remote_profiles/README.md)；[來源雜湊、逐點核對及容器實跑收據](../../evidence/remote_profile_acceptance.json)。
