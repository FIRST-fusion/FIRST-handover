# 五張 equilibrium profile 圖：來源、座標與重畫

此工具**只讀已有的平衡輸出**，不執行 CHEASE／VMEC／DCON，也不修改輸入或 reference。每案例產生五張 PNG、五張向量 PDF、overview、五頁 `profiles.pdf`、逐點 `profiles.csv` 及含來源 SHA-256 的 `metadata.json`。

## 使用

在 FIRST 執行 `tools/run_case.py` 或 `tools/run_bootstrap_case.py`，現在會在求解與診斷成功後自動呼叫此工具，圖放在該次 `runs/<name>/profiles/`。以下獨立指令則用於重畫既有輸出，不會重跑 solver。自動出圖會驗證 15 個必要檔案：6 PNG、7 PDF、CSV 與 metadata JSON。

在 repository 根目錄，使用有 NumPy、SciPy、Matplotlib 的 Python（依賴見 `requirements-plot.txt`）：

```sh
python3 -m pip install -r requirements-plot.txt
python3 tools/plot_profiles.py --solver chease \
  --source reference/chease_c50/equilibrium/linliu_profiles.dat \
  --namelist examples/chease_c50/namelist \
  --label chease_c50 --output runs/plots-chease-c50
python3 tools/plot_profiles.py --solver vmec \
  --source reference/vmec_lowbeta/equilibrium/wout_test.nc \
  --label vmec_lowbeta --output runs/plots-vmec-lowbeta
```

`--output` 必須為新目錄，避免覆蓋結果。`--x rho_tor` 可改畫 √s；`--x psi_n` 可改畫正規化極向磁通。缺檔、非有限資料、錯誤座標或缺少必要 normalization 會報錯，不會造假補曲線。

對高 bootstrap runner 的新輸出，將 `--source` 指向其實際產生的 `linliu_profiles.dat` 或 `wout_test.nc`；CHEASE 的 `--namelist` 必須是同一次平衡所使用的 namelist。不能用別案例或只按幾何印象猜 R0/B0。例如已經跑完 `--output runs/p80-new` 的 CHEASE 案例，可直接：

```sh
python3 tools/plot_profiles.py --solver chease \
  --source runs/p80-new/equilibrium/linliu_profiles.dat \
  --namelist runs/p80-new/equilibrium/namelist \
  --label p80-new --output runs/p80-new-plots
```


## 五張圖讀哪裡

CHEASE 檔案為 `linliu_profiles.dat`，以下欄號從 **1** 開始。其兩行 header 只列 17 個名稱，但實際每列有 **18 欄**；第18欄是 `CPSRF`。不是從圖片取點，也不是從 DCON 摘要反推 profile。

| 圖 | CHEASE 原始欄位 | VMEC `wout_test.nc` 變數 | 圖中單位 |
|---|---|---|---|
| safety factor q | 第8欄 `q` | `1/iotaf` | 無因次 |
| pressure | 第6欄 `p`，乘 B0²/μ0 | `presf`，已是 Pa | Pa |
| ⟨J·B⟩ | 第9欄 `jpar`，乘 B0²/(μ0 R0) | `jdotb`，直接使用 | A·T/m² |
| 極向電流剖面 | 第5欄 `ffp`／第4欄 `f`，再乘 D B0 R0/μ0 | `jcuru`，直接使用 | A |
| 環向電流剖面 | 第15欄 `RIIE`，乘 D B0 R0/(2πμ0) | `jcurv`，直接使用 | A |

這裡 μ0=4π×10⁻⁷ H/m；R0、B0 取自 CHEASE `namelist` 的 `R0EXP` [m]、`B0EXP` [T]；D=dψ̂/ds，定義如下。`jpar` 是 ⟨J·B⟩ 的 CHEASE normalization，不是局部 J∥；`ipar`（第10欄）不是本圖採用的 quantity。

**兩張 current 圖是 Jacobian 加權剖面，不是圓柱座標的局部電流密度 A/m²，也不是累積總電流 Ip。** VMEC 定義為

`jcurX = (dV/ds)/(2π)² × ⟨J·∇X⟩`, X=u,v。

因此本工具標記為 A。所有圖保留 solver 原生符號；轉換案例的 VMEC 環向場方向可能與 CHEASE 相反，不能因電流／⟨J·B⟩ 符號相反就認定物理不一致，也不能偷偷取絕對值。

## 磁通轉換：不是把座標乘 q

預設橫軸 `s=Φtor/Φtor,edge`（以磁軸為零）。VMEC 從 `phi` 取 s，從 `chi` 取 ψN。CHEASE 的第1欄 `cs` 是 √ψN 的區間邊界；第2欄 `csm` 是區間中點；第3欄 `psi` 與第18欄 `CPSRF` 提供無因次極向磁通。

與封存轉換器一致的離散公式：

```text
Δψ̂_i = (cs[i+1]² - cs[i]²) CPSRF
T_0 = 0; T_{i+1} = T_i + q[i] Δψ̂_i
s_boundary = T / T_edge
s_profile[i] = (s_boundary[i]+s_boundary[i+1])/2  # 原中點資料
s_profile[last] = 1                              # 原邊界診斷列
D = T_edge / q
|Φtor,edge| = 2π B0 R0² T_edge
```

CHEASE 原始中點資料沒有磁軸點，本工具不補造。最後的 edge diagnostic 列不再額外計入積分。取樣位置沿用原 converter 的區間規則，並不是重新插值後宣稱高解析度。

VMEC 的 `presf/iotaf/jdotb/jcuru/jcurv` 使用 full mesh，不拿 half-mesh `pres/iotas` 直接混用；電流與 ⟨J·B⟩ 的來源端點外插保留，小負壓也不裁掉。

## 本次產圖與資料定位

圖在 [`../figures/profiles`](../figures/profiles/README.md)。四個教學例各自的來源：

- `reference/chease_c50/equilibrium/linliu_profiles.dat` + `examples/chease_c50/namelist`。
- `reference/chease_c51/equilibrium/linliu_profiles.dat` + `examples/chease_c51/namelist`。
- `reference/vmec_lowbeta/equilibrium/wout_test.nc`。
- `reference/vmec_smooth/equilibrium/wout_test.nc`。

另外兩組真正 parent→VMEC 配對：

| 配對 | CHEASE 來源 | VMEC 來源 |
|---|---|---|
| A=1.4 p80 | `research-inputs/bootstrap99/cases/freep80_high256/historical/linliu_profiles.dat` + 同案例 `inputs/namelist` | 本機封存 `vmec_p80_513/wout_test.nc` |
| A=1.2 候選 | `research-inputs/bootstrap99/cases/p6_s033_c050_fine_exact320/historical/linliu_profiles.dat` + 同案例 `inputs/namelist` | 本機封存 `vmec_p6_s033_c050_fine_exact320_2049/wout_test.nc` |

兩個研究用 wout 原本不在 Git 交接包；本次從既有本機封存讀取，未新跑 solver、未把大型 wout 混進 baseline。完整本機來源路徑與 hash 在各圖目錄 `metadata.json`；遠端原始來源與 parent 在 `research-inputs/bootstrap99/cases/<VMEC>/historical/transfer.json` 及研究包 `manifest.json`。在 FIRST 可從既有封存或自己的新 run 產生同樣五圖。

四個教學例不是同一個平衡，不做交叉誤差排名。研究配對的獨立座標／電流一致性檢查另見 [`../evidence/profile_validation.json`](../evidence/profile_validation.json)。

## 物理定義的核對依據

本次只讀既有封存原碼，不將授權原碼複製進 repository：

- CHEASE `chease_linliu.f` 21818–21826 行：18欄 writer；9923 行：RJPAR 的 ⟨J·B⟩ 定義；12456–12459 行：RIVOL/RIIE 對磁通積分；27659–27671 行：R0/B0 尺度。
- VMEC `wrout.f` 1276–1283 行：`presf/jcuru/jcurv` 寫檔時已除 μ0；`jdotb` 已具 SI 尺度。
- VMEC `eqfor.f` 193–195 行：Jacobian 加權 current 定義；209–217 行：端點線性外插。

驗證收據記錄以上檔案 hash 與來源位置。這些圖及數值一致性**不增加穩定性認證**。A=1.2 的近軸 Mercier／缺失磁面與有限 n 未完成限制仍保留；詳見高 bootstrap 包 README。
