NBA Fantasy Scout — GitHub Pages 更新套件
=======================================
專案：https://github.com/gilbertwice/nba-fantasy-scout
網站：https://gilbertwice.github.io/nba-fantasy-scout/

1. 解壓縮 ZIP。
2. 打開 GitHub Repository，使用 Add file > Upload files。
3. 將 ZIP 解壓後的 index.html、data 資料夾、scripts 資料夾、.github 資料夾內容上傳到專案根目錄。
   注意：GitHub 網頁拖曳資料夾可能依瀏覽器支援而異。
   如果隱藏的 .github 資料夾沒有上傳，請在 GitHub 按 Add file > Create new file，
   檔名輸入 .github/workflows/daily-update.yml，將本套件同名檔案的內容貼上儲存。
   其他檔案也可以用 Create new file 輸入完整路徑逐一新增。
4. Commit changes；index.html 是網站新版，會覆蓋舊首頁。
5. GitHub Settings > Actions > General > Workflow permissions，選 Read and write permissions，Save。
6. GitHub Actions > Daily NBA data update > Run workflow，執行一次。
7. 等待 workflow 成功後，檢查 data/players.json 有 updatedAt 和 players 資料。
8. 開啟公開網站，按重新整理。若仍是舊版，等待 Pages 部署後再試。

注意：
- 來源為 ESPN 非官方公開 NBA 資料端點，不是 Yahoo API；可能變動、限制存取或故障。
- 不保證 ESPN 授權大量自動抓取；使用前請自行確認資料來源條款。
- Yahoo 全站 Adds/Drops 與 League 420 的 FA 即時資料沒有自動串接。
- 球探分數是明示公式的規則評分，不是 AI 模型、不是市場熱門排名。
- FA 名單只儲存在你目前使用的瀏覽器，網站公開但不會自動公開你的 FA 清單。
- GitHub Actions 的 cron 可能延遲；資料更新失敗會保留舊檔，不會顯示假資料。
- 由於本環境無法連到 ESPN 網路端點，無法在這裡完成真實線上取數驗證。
