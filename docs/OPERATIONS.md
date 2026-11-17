# FIRST 主機管理速查

主機：`140.116.16.7` / `ncku-first`。本頁快照：2026-11-18（Asia/Taipei）；不是持續監控。所有維護先與現任 owner 協調；本 repository 不轉移其他研究或排程的所有權。

## 1. 連線與帳號

校外先用 NCKU 官方 VPN；校內可直接 SSH。VPN 登入公告：每次最長 120 分鐘，閒置 20 分鐘可能斷線。各接手者用獲核准的個人憑證／SSH key，不在 repository 留密碼、OTP 或私鑰。

```sh
ssh ouvic@140.116.16.7
hostname
id
```

- `ubuntu`：sudo、adm、docker 群組；偏系統管理，sudo 本次仍要求認證。不是建議所有工作都用管理帳號。
- `ouvic`：研究目錄與 docker 群組；Docker 權限具有很高的主機操作能力，不是隔離的唯讀權限。
- 歷史摘要：ubuntu 的紀錄偏安裝／權限／SSH；ouvic 偏建置／計算／容器。歷史是不完整的命令紀錄，不是操作成功證據；原始 history 未交付。

## 2. 主機與資料位置

| 項目 | 查核快照 |
|---|---|
| OS | Ubuntu 22.04.5 LTS，x86_64 |
| CPU / RAM | 64 logical CPUs，約 1 TiB RAM |
| `/` | 1.8T，85% 使用，261G 可用 |
| `/data_36T` | 37T，20% 使用，28T 可用；RAID5，`[3/3] [UUU]` |
| Docker root | `/var/lib/docker`（根分割區） |
| GPU | NVIDIA RTX A4000 16GB；nvidia-smi 查詢正常 |
| 管理待辦 | nvidia-persistenced.service 為 failed；本次未修復 |

RAID 不是備份。沒有查核到可還原的專案備份證據；不要把系統 `dpkg-db-backup.timer` 當成研究資料備份。接手管理者須另外記錄備份目的地、頻率、最後成功時間與抽樣還原結果。

| 路徑 | 用途／限制 |
|---|---|
| `/home/ouvic/workspace/ESTCombo` | 既有 VMEC/DCON 等程式來源，唯讀參考，不跑會改共用 rundir 的舊 wrapper |
| `/home/ouvic/Cheese/CheaseMerge` | 舊 CHEASE 來源；不是本套範例的 patched binary |
| `/home/ouvic/linliu-reproduction-20260911` | Lin-Liu 封存與本範例的 CHEASE binary；不覆寫 |
| `/home/ouvic/first-handover-20261118` | 本次交接的隔離驗證目錄，不是唯一可 clone 位置 |
| `/home/ouvic/plasma-research-handover-20261107/START_HERE.md` | 老師目標／既有參數搜尋交接 |
| `/data_36T` | 大容量資料盤；新目錄與配額先由 owner 指定，不任意搬動既有資料 |

## 3. 日常唯讀檢查

```sh
uptime
free -h
df -hT / /data_36T
cat /proc/mdstat
systemctl --failed --no-pager
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
docker ps -a --filter label=org.first.handover=true
systemctl list-timers --all --no-pager
crontab -l
```

盤點時有 919 個容器、4 個 running（本交接測試前）：plasma_a12_second_20261028 與 study-control-plane/worker/worker2。容器運行不等於 solver 運行。兩帳號沒有個人 crontab，不代表沒有 system/root cron、systemd timer 或其他電腦的監督器。

## 4. 出問題先查什麼

| 症狀 | 先查 | 不要直接做 |
|---|---|---|
| SSH 斷線 | VPN、網路、主機可達性；重新確認自己的容器／輸出 | 重送同一計算、認定遠端已停 |
| 根目錄空間不足 | df、自己新輸出大小、Docker 資料位置與 owner | docker system prune、批次刪容器 |
| 執行停住 | `docker logs <自己的名稱>`、`docker inspect --format '{{.State.Status}} {{.State.ExitCode}} {{.State.OOMKilled}}' <名稱>` | killall、重啟 Docker daemon |
| GPU 服務失敗 | 分開看 nvidia-smi 與 systemctl 狀態 | 未協調就更新驅動或 reboot |
| 結果與參考不符 | input/binary/image/control hash、完整 log、summary | 放寬公差或覆寫 reference |

停止工作只針對自己已確認的容器名稱，先保留 log 與狀態並通知協作者。此教材的程式使用 timeout；不自動刪除容器、資料或設定排程。重啟主機、SSH／防火牆／驅動修改、帳號增刪、RAID 維修皆屬獨立管理作業，不在快速入門流程中。

## 帳號別執行驗收

ubuntu 已另做四例實跑，但不是直接讀取 ouvic home：使用相同hash的帳號自有程式副本。詳見 [MULTIUSER.md](MULTIUSER.md)；其他帳號仍未驗證。
