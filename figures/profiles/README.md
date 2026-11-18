# 五張 profile 圖

每案例有 q、pressure、⟨J·B⟩、極向與環向 Jacobian 加權電流剖面。
橫軸為 normalized toroidal flux s；保留原生符號、取樣與端點。
[來源欄位、單位、磁通轉換與執行命令](../../docs/PROFILES.md)。

| 案例 | 總覽 | 五頁 PDF | 數據 | 來源與 hash |
|---|---|---|---|---|
| chease_c50 | [PNG](chease_c50/overview.png) | [PDF](chease_c50/profiles.pdf) | [CSV](chease_c50/profiles.csv) | [JSON](chease_c50/metadata.json) |
| chease_c51 | [PNG](chease_c51/overview.png) | [PDF](chease_c51/profiles.pdf) | [CSV](chease_c51/profiles.csv) | [JSON](chease_c51/metadata.json) |
| vmec_lowbeta | [PNG](vmec_lowbeta/overview.png) | [PDF](vmec_lowbeta/profiles.pdf) | [CSV](vmec_lowbeta/profiles.csv) | [JSON](vmec_lowbeta/metadata.json) |
| vmec_smooth | [PNG](vmec_smooth/overview.png) | [PDF](vmec_smooth/profiles.pdf) | [CSV](vmec_smooth/profiles.csv) | [JSON](vmec_smooth/metadata.json) |
| freep80_high256 | [PNG](freep80_high256/overview.png) | [PDF](freep80_high256/profiles.pdf) | [CSV](freep80_high256/profiles.csv) | [JSON](freep80_high256/metadata.json) |
| vmec_p80_513 | [PNG](vmec_p80_513/overview.png) | [PDF](vmec_p80_513/profiles.pdf) | [CSV](vmec_p80_513/profiles.csv) | [JSON](vmec_p80_513/metadata.json) |
| p6_s033_c050_fine_exact320 | [PNG](p6_s033_c050_fine_exact320/overview.png) | [PDF](p6_s033_c050_fine_exact320/profiles.pdf) | [CSV](p6_s033_c050_fine_exact320/profiles.csv) | [JSON](p6_s033_c050_fine_exact320/metadata.json) |
| vmec_p6_s033_c050_fine_exact320_2049 | [PNG](vmec_p6_s033_c050_fine_exact320_2049/overview.png) | [PDF](vmec_p6_s033_c050_fine_exact320_2049/profiles.pdf) | [CSV](vmec_p6_s033_c050_fine_exact320_2049/profiles.csv) | [JSON](vmec_p6_s033_c050_fine_exact320_2049/metadata.json) |

## 高 bootstrap：五張獨立圖

| 物理量 | A=1.4 CHEASE p80 | A=1.4 VMEC p80 | A=1.2 CHEASE | A=1.2 VMEC |
|---|---|---|---|---|
| q | [PNG](freep80_high256/q.png) · [PDF](freep80_high256/q.pdf) | [PNG](vmec_p80_513/q.png) · [PDF](vmec_p80_513/q.pdf) | [PNG](p6_s033_c050_fine_exact320/q.png) · [PDF](p6_s033_c050_fine_exact320/q.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/q.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/q.pdf) |
| 壓力 [Pa] | [PNG](freep80_high256/pressure.png) · [PDF](freep80_high256/pressure.pdf) | [PNG](vmec_p80_513/pressure.png) · [PDF](vmec_p80_513/pressure.pdf) | [PNG](p6_s033_c050_fine_exact320/pressure.png) · [PDF](p6_s033_c050_fine_exact320/pressure.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/pressure.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/pressure.pdf) |
| ⟨J·B⟩ [A·T/m²] | [PNG](freep80_high256/jdotb.png) · [PDF](freep80_high256/jdotb.pdf) | [PNG](vmec_p80_513/jdotb.png) · [PDF](vmec_p80_513/jdotb.pdf) | [PNG](p6_s033_c050_fine_exact320/jdotb.png) · [PDF](p6_s033_c050_fine_exact320/jdotb.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/jdotb.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/jdotb.pdf) |
| 極向加權電流 [A] | [PNG](freep80_high256/poloidal_current.png) · [PDF](freep80_high256/poloidal_current.pdf) | [PNG](vmec_p80_513/poloidal_current.png) · [PDF](vmec_p80_513/poloidal_current.pdf) | [PNG](p6_s033_c050_fine_exact320/poloidal_current.png) · [PDF](p6_s033_c050_fine_exact320/poloidal_current.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/poloidal_current.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/poloidal_current.pdf) |
| 環向加權電流 [A] | [PNG](freep80_high256/toroidal_current.png) · [PDF](freep80_high256/toroidal_current.pdf) | [PNG](vmec_p80_513/toroidal_current.png) · [PDF](vmec_p80_513/toroidal_current.pdf) | [PNG](p6_s033_c050_fine_exact320/toroidal_current.png) · [PDF](p6_s033_c050_fine_exact320/toroidal_current.pdf) | [PNG](vmec_p6_s033_c050_fine_exact320_2049/toroidal_current.png) · [PDF](vmec_p6_s033_c050_fine_exact320_2049/toroidal_current.pdf) |

教學案例不是同一物理平衡，不能直接拿其差異作跨 solver 誤差。研究用 VMEC wout 取自本機封存，不在原始 Git 輸入包；精確路徑在 metadata。沒有新的 solver／穩定性執行。
