# 專案目標與交接邊界

## 老師目標

低長寬比 A≈1.2、高 βN≈7–8、主要由 bootstrap 電流維持並有第二穩定分支證據的平衡；再研究侷限改善與啟動→輸運演化→終態的可達路徑。

基準：Miller、Y. R. Lin-Liu 等，Stable equilibria for bootstrap-current-driven low aspect ratio tokamaks，Physics of Plasmas 4,1062 (1997)，https://doi.org/10.1063/1.872193 。原文 A=1.4，有限 n 結論有導體壁條件，不能直接外推 A=1.2。

## 歷史研究狀態，不是本次新驗收

2026-11-07 交接依 10/27–29 紀錄：A=1.2 候選 βN≈5.60、fBS≈99.29%；尚未證明第二穩定分支，VMEC/DCON 近軸對照與磁面覆蓋有問題，BALOO 介面曾通但科學驗收未通過。主機上的詳細入口：

`/home/ouvic/plasma-research-handover-20261107/START_HERE.md`

接手 Agent 先核對目前 owner、輸出與鎖；此新 repository 的四個示範不代表以上問題已解決。FIRST direct-search 及其他既有排程仍由原 owner 管理。

## 第一週交接成果

1. 能在授權 FIRST 帳號跑完四個範例，提交新的 summary 與 compare 結果。
2. 能說明 EXPEQ/NIN/namelist、input.test、INP1/dcon_test.txt 的差別。
3. 能指出一個正常執行但不代表穩定的結果，以及其警訊與限制。
4. 能用唯讀指令找到自己的容器、使用的 binary/image、資料位置與主機空間。
5. 再依研究交接文件選擇下一個工作包；不把教程執行擴大成全主機重啟或參數搜尋。

## 原教材作為查閱庫

原套件：FIRST-完整教材-20261014（原版138頁、220張、9支影片約177分鐘，另有重製版）。本 repository 不重複納入大型影片。

- 接手先讀：M8 工作流與除錯、M9 修改與驗證。
- 程式專題：M4 CHEASE、M5 VMEC、M6 DCON；bootstrap 研究再讀 M7。
- 理論補充：M1–M3，依需要查閱。
- 持有者本機位置：`~/Library/Mobile Documents/com~apple~CloudDocs/電漿所資料/參考資料/FIRST-完整教材-20261014`。這不是 clone 後自動出現的路徑，由交接者依組織權限另行提供。
