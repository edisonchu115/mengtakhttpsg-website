# 明德行網站規則 Meng Tak Hong Website Rules

## 路徑
- 網站根目錄：C:\Users\user\Desktop\mengtakhong-website\
- 產品JSON：C:\Users\user\Desktop\mengtakhong-website\products\
- 產品圖片：C:\Users\user\Desktop\mengtakhong-website\assets\images\products\
- 品牌Logo：C:\Users\user\Desktop\mengtakhong-website\assets\images\brands\
- 進度記錄：C:\Users\user\Desktop\mengtakhong-website\progress.json

## 設計規則
- 導航背景：#1C1C1C
- 金色主調：#D4AF37
- 主背景：#FFFFFF
- 次背景：#F5F0E8
- Footer背景：#1C1C1C
- Footer文字：#FFFFFF + #D4AF37

## 公司資料
- 公司名：明德行國際有限公司 Meng Tak Hong International Co., Ltd.
- Est. 1998
- 地址：澳門黑沙環慕拉士大馬路195號南嶺工業大廈4樓F
- 電話：28415128 / 28584838
- WhatsApp：https://wa.me/85366687448
- Email：info@mengtakhong.com
- Facebook：https://www.facebook.com/profile.php?id=61555744448402
- Instagram：https://www.instagram.com/mengtakhong.mo/

## 產品分類
- whisky.json → category/whisky.html（威士忌）
- cognac.json → category/cognac.html（干邑/拔蘭地）
- japan.json → category/japan.html（日本產品）
- korea.json → category/korea.html（韓國產品）
- wine.json → category/wine.html（葡萄酒/香檳）
- spirits.json → category/spirits.html（烈酒/力嬌）
- chinese.json → category/chinese.html（中國白酒）
- beer.json → category/beer.html（啤酒/汽水）

## 重要原則
- 唔顯示價錢
- 所有產品卡片點擊跳去獨立產品頁 product/[slug].html
- 圖片統一600x600px白底
- 語言：繁體中文為主，英文副標

## JavaScript 嚴格規則（必須遵守，違反會造成Bug）

### 全局變數規則
- 所有需要跨檔案共享嘅變數必須用 var，唔可以用 const 或 let
- 正確：var MTH_PRODUCTS = [...]
- 錯誤：const MTH_PRODUCTS = [...] ← 唔會加到 window，其他檔案讀唔到
- 每次建立新的 products-data.js 或任何共享數據檔案，必須用 var

### 圖片錯誤處理規則
- 禁止用 inline onerror 巢狀引號
- 錯誤寫法：onerror="this.src='placeholder.jpg'"
- 正確寫法：onerror="handleImgError(this)"
- 必須配合外部函數：
  function handleImgError(img) {
    img.src = 'assets/images/placeholder.jpg';
    img.onerror = null;
  }

### 引號規則
- HTML 屬性統一用雙引號
- JavaScript 字串統一用單引號
- 禁止喺 HTML 屬性入面巢狀同款引號

### Emoji 規則
- 禁止喺 JavaScript 字串入面直接用 Emoji
- 如需要用，改為 HTML entity 或放喺 HTML 而唔係 JS 入面

### 每次修改後必須檢查
- 確認 window.MTH_PRODUCTS 可以讀取到
- 確認所有輪播 carouselInit 正常執行
- 喺 Console 冇紅色錯誤
