# 圖片處理規則 Image Processing Rules

## 產品圖片規格
- 尺寸：600x600px
- 背景：純白 #FFFFFF
- 產品圖等比例縮放，最長邊500px
- 四周留50px白邊
- 格式：JPG，質素90%
- 儲存路徑：assets/images/products/[slug].jpg

## 品牌Logo規格
- 尺寸：200x120px
- 背景：純白 #FFFFFF
- Logo等比例縮放居中
- 格式：PNG
- 儲存路徑：assets/images/brands/[brand_name].png

## 搵圖優先順序
1. 英文名稱 + "bottle" 搜尋
2. 中文名稱搜尋
3. 條碼搜尋（barcodelookup.com / upcitemdb.com）
4. 從對應PDF截圖

## PDF對應關係
- 威士忌 → 【代理正貨】威士忌報價.pdf 同 【進口】威士忌.pdf
- 干邑/拔蘭地 → 【代理正貨】拔蘭地干邑.pdf 同 【進口】拔蘭地干邑.pdf
- 日本產品 → 【代理正貨】日本產品.pdf 同 【進口】日本產品.pdf
- 韓國產品 → 【代理正貨】韓國_台灣_泰國_澳洲_越南.pdf
- 葡萄酒 → 【代理正貨】葡萄酒_香檳.pdf 同 【進口】葡萄酒_香檳.pdf
- 烈酒力嬌 → 【代理正貨】烈酒力嬌.pdf 同 【進口】烈酒力嬌_酒辦.pdf
- 中國白酒 → 中國酒報價_Chinese_Spirits.pdf
- 啤酒汽水 → 【進口】汽水啤酒.pdf

## 進度記錄
- 每完成一個產品記錄到 progress.json
- 格式：{"completed": ["slug1","slug2"], "failed": ["slug3"], "last_updated": "timestamp"}
- 中途停止後打「繼續圖片工作」自動從上次位置繼續

## 使用Library
- Pillow (PIL) 處理所有圖片
- requests + beautifulsoup4 搜尋下載圖片
- PyMuPDF (fitz) 讀取PDF截圖
- 安裝指令：pip install Pillow requests beautifulsoup4 PyMuPDF --break-system-packages
