import streamlit as st
import os
from PIL import Image
import json
from business_card_ocr import BusinessCardOCR
import pandas as pd
import tempfile
from google import genai
from google.genai import types


# 設置頁面配置
st.set_page_config(
    page_title="名片識別系統",
    page_icon="📇",
    layout="wide"
)

# 初始化 OCR 系統
@st.cache_resource
def init_ocr():
    return BusinessCardOCR()

ocr = init_ocr()

# 側邊欄導航
with st.sidebar:
    st.title("名片識別系統")
    choice = st.radio(
        "選擇功能",
        ["上傳識別", "名片管理", "資料修改"]
    )

# 上傳和識別頁面
if choice == "上傳識別":
    st.header("📸 名片上傳與識別")
    
    uploaded_file = st.file_uploader("上傳名片圖片", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        # 顯示上傳的圖片
        col1, col2 = st.columns(2)
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="上傳的名片", use_column_width=True)
        
        # 識別按鈕
        if st.button("開始識別"):
            with st.spinner("正在識別名片..."):
                # 暫存圖片
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_path = tmp_file.name
                
                # 執行識別
                result = ocr.analyze_card(temp_path)
                
                if result:
                    with col2:
                        st.success("識別完成！")
                        # 顯示識別結果並允許編輯
                        with st.form("edit_form"):
                            st.subheader("識別結果")
                            name = st.text_input("姓名", result.get('name', ''))
                            company = st.text_input("公司名稱", result.get('company_name', ''))
                            title = st.text_input("職稱", result.get('title', ''))
                            address = st.text_area("地址", result.get('address', ''))
                            phone = st.text_input("電話", result.get('phone', ''))
                            mobile = st.text_input("手機", result.get('mobile', ''))
                            fax = st.text_input("傳真", result.get('fax', ''))
                            email = st.text_input("電子郵件", result.get('email', ''))
                            website = st.text_input("網站", result.get('website', ''))
                            tax_id = st.text_input("統一編號", result.get('tax_id', ''))
                            other = st.text_area("其他資訊", result.get('other_info', ''))
                            
                            if st.form_submit_button("儲存資料"):
                                # 更新資料
                                card_data = {
                                    'name': name,
                                    'company_name': company,
                                    'title': title,
                                    'address': address,
                                    'phone': phone,
                                    'mobile': mobile,
                                    'fax': fax,
                                    'email': email,
                                    'website': website,
                                    'tax_id': tax_id,
                                    'other_info': other
                                }
                                ocr.save_card_data(card_data, temp_path)
                                st.success("資料已成功儲存！")
                else:
                    st.error("識別失敗，請確認圖片品質後重試。")

# 名片管理頁面
elif choice == "名片管理":
    st.header("📋 名片管理")
    
    # 獲取所有名片資料
    cards = ocr.get_all_cards()
    
    if cards:
        # 轉換為 DataFrame 以便顯示
        df = pd.DataFrame(cards, columns=[
            'ID', '姓名', '公司名稱', '職稱', '地址', '電話', '手機',
            '傳真', '電子郵件', '網站', '統編', '其他資訊', '圖片路徑',
            '建立時間', '更新時間'
        ])
        
        # 顯示資料表
        st.dataframe(df)
        
        # 匯出功能
        if st.button("匯出 CSV"):
            df.to_csv("名片資料.csv", index=False, encoding='utf-8-sig')
            st.success("資料已匯出為 CSV 檔案！")
    else:
        st.info("目前沒有儲存的名片資料")

# 資料修改頁面
elif choice == "資料修改":
    st.header("✏️ 資料修改")
    
    # 獲取所有名片資料
    cards = ocr.get_all_cards()
    
    if cards:
        # 建立選擇清單
        card_options = [f"{card[1]} - {card[2]}" for card in cards]
        selected_card = st.selectbox("選擇要修改的名片", card_options)
        
        if selected_card:
            # 獲取選擇的名片索引
            idx = card_options.index(selected_card)
            card = cards[idx]
            
            # 顯示當前圖片
            if os.path.exists(card[12]):  # 圖片路徑
                st.image(Image.open(card[12]), caption="名片圖片", width=300)
            
            # 編輯表單
            with st.form("修改表單"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("姓名", card[1])
                    company = st.text_input("公司名稱", card[2])
                    title = st.text_input("職稱", card[3])
                    address = st.text_area("地址", card[4])
                    phone = st.text_input("電話", card[5])
                    mobile = st.text_input("手機", card[6])
                
                with col2:
                    fax = st.text_input("傳真", card[7])
                    email = st.text_input("電子郵件", card[8])
                    website = st.text_input("網站", card[9])
                    tax_id = st.text_input("統編", card[10])
                    other = st.text_area("其他資訊", card[11])
                
                if st.form_submit_button("更新資料"):
                    # 更新資料
                    updated_data = {
                        'name': name,
                        'company_name': company,
                        'title': title,
                        'address': address,
                        'phone': phone,
                        'mobile': mobile,
                        'fax': fax,
                        'email': email,
                        'website': website,
                        'tax_id': tax_id,
                        'other_info': other
                    }
                    ocr.update_card_data(card[0], updated_data)
                    st.success("資料更新成功！")
    else:
        st.info("目前沒有儲存的名片資料")

# 頁面底部資訊
st.markdown("---")
st.markdown("### 💡 使用說明")
st.markdown("""
- 上傳識別：上傳名片圖片進行自動識別
- 名片管理：查看所有已儲存的名片資料
- 資料修改：修改已儲存的名片資訊
""") 