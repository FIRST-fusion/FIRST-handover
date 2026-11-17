# 使用範圍與授權

本私人儲存庫供 FIRST/NCKU 授權團隊交接使用。沒有放入 CHEASE、VMEC、DCON 的原始碼、執行檔或容器映像；沒有對第三方程式授予新授權。

FIRST 既有 CHEASE `README.md` 記載：Subproject II 成員使用、不可安裝到 NCKU 外的主機、CHEASE 未經 EPFL 核准不得散布；對外討論另須依既有授權程序。私有 GitHub 存取權不等於程式使用權。

`runtime/first.json` 指向 FIRST 上既有獲授權的執行環境，並記錄二進位 SHA-256 與映像 ID。映像 ID 是本機內容識別，不是可從 Docker Hub 拉取的 registry digest。沒有推送任何映像到 registry。

範例資料與本次輸出只供組織內交接，不附開源再散布授權。改為公開 repository、上傳 solver 或跨校部署前，必須另核對權利與授權。原始碼定位可參考 FIRST-fusion/CHEASE、FIRST-fusion/DCON、FIRST-fusion/Stellarator-Tools；GitHub HEAD 不一定等於本機已修訂的二進位。
