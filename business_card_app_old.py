import streamlit as st
import os
from PIL import Image
import json
import tempfile
from google import genai
from google.genai import types

import time

# Gemini API 設置
#api_key = "xxxxxxxxxxxxxxx"

GOOGLE_API_KEY = "xxxxxxxxxxxxxxx"  # 請替換成你的 API KEY
#genai.configure(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash"

class BusinessCardAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
    
    def analyze_image(self, img, max_retries=5, retry_delay=1):
        prompt = """
        請仔細分析這張名片圖片，並提取以下資訊（以JSON格式回傳）：

        請注意以下重點：
        1. 若遇到多個電話號碼，請依照格式（如：+886-、02-、0800-）判斷是電話、手機或傳真
        2. 地址通常會包含縣市、路名、樓層等資訊
        3. 統一編號（統編）通常為8位數字
        4. 電子郵件通常包含 @ 符號
        5. 網址通常以 http:// 或 www. 開頭

        請將資訊整理成以下JSON格式：
        {
            "name": "姓名",
            "company_name": "公司名稱",
            "title": "職稱",
            "address": "完整地址",
            "phone": "市話號碼",
            "mobile": "手機號碼",
            "fax": "傳真號碼",
            "email": "電子郵件",
            "website": "網站網址",
            "tax_id": "統一編號",
            "other_info": "其他重要資訊"
        }

        若某欄位在名片上找不到對應資訊，請將該欄位保留為空字串。
        請確保所有擷取的資訊準確且格式正確。
        """
        
        for attempt in range(max_retries):
            try:
                image_response = self.client.models.generate_content(
                    model=MODEL_ID,
                    contents=[img, prompt],
                    config=genai.types.GenerateContentConfig(temperature=0.5)
                )
                # 嘗試解析 JSON
                try:
                    # 清理回應文本，只保留 JSON 部分
                    response_text = image_response.text
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        return json.loads(json_str)
                    return None
                except json.JSONDecodeError:
                    print("JSON 解析錯誤")
                    return None
                    
            except Exception as e:
                if "429" in str(e):
                    print(f"429 error, 等待 {retry_delay} 秒後重試...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"發生錯誤: {e}")
                    return None
        print("已達最大重試次數")
        return None

# 初始化分析器
@st.cache_resource
def init_analyzer():
    return BusinessCardAnalyzer()

# Streamlit 應用界面
st.set_page_config(
    page_title="名片識別系統",
    page_icon="📇",
    layout="wide"
)

analyzer = init_analyzer()

# 側邊欄
with st.sidebar:
    st.title("名片識別系統")
    choice = st.radio(
        "功能選擇",
        ["名片識別", "歷史記錄"]
    )

# 主要識別頁面
if choice == "名片識別":
    st.header("📸 名片識別與編輯")
    
    # 檔案上傳
    uploaded_file = st.file_uploader("上傳名片圖片", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        # 顯示圖片
        col1, col2 = st.columns(2)
        with col1:
            image = Image.open(uploaded_file)
            # 調整圖片大小
            resized_img = image.resize((800, int(800 * image.size[1] / image.size[0])), Image.Resampling.LANCZOS)
            st.image(resized_img, caption="上傳的名片", use_column_width=True)
        
        # 識別按鈕
        if st.button("開始識別"):
            with st.spinner("正在識別名片..."):
                # 執行識別
                result = analyzer.analyze_image(resized_img)
                
                if result:
                    with col2:
                        st.success("識別完成！")
                        # 顯示識別結果並允許編輯
                        with st.form("edit_form"):
                            st.subheader("識別結果")
                            
                            # 基本信息
                            name = st.text_input("姓名", result.get('name', ''))
                            company = st.text_input("公司名稱", result.get('company_name', ''))
                            title = st.text_input("職稱", result.get('title', ''))
                            
                            # 聯絡方式
                            st.subheader("聯絡方式")
                            phone = st.text_input("電話", result.get('phone', ''))
                            mobile = st.text_input("手機", result.get('mobile', ''))
                            fax = st.text_input("傳真", result.get('fax', ''))
                            email = st.text_input("電子郵件", result.get('email', ''))
                            
                            # 地址和網站
                            st.subheader("地址和網站")
                            address = st.text_area("地址", result.get('address', ''))
                            website = st.text_input("網站", result.get('website', ''))
                            
                            # 其他信息
                            st.subheader("其他信息")
                            tax_id = st.text_input("統一編號", result.get('tax_id', ''))
                            other = st.text_area("其他資訊", result.get('other_info', ''))
                            
                            # 儲存按鈕
                            if st.form_submit_button("儲存資料"):
                                # 建立儲存資料
                                save_data = {
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
                                    'other_info': other,
                                    'image_path': uploaded_file.name
                                }
                                
                                # 儲存到 session state
                                if 'saved_cards' not in st.session_state:
                                    st.session_state.saved_cards = []
                                st.session_state.saved_cards.append(save_data)
                                
                                st.success("資料已成功儲存！")
                else:
                    st.error("識別失敗，請確認圖片品質後重試。")

# 歷史記錄頁面
elif choice == "歷史記錄":
    st.header("📋 歷史記錄")
    
    if 'saved_cards' in st.session_state and st.session_state.saved_cards:
        for idx, card in enumerate(st.session_state.saved_cards):
            with st.expander(f"名片 {idx+1}: {card['name']} - {card['company_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**基本資訊**")
                    st.write(f"姓名: {card['name']}")
                    st.write(f"公司: {card['company_name']}")
                    st.write(f"職稱: {card['title']}")
                
                with col2:
                    st.write("**聯絡方式**")
                    st.write(f"電話: {card['phone']}")
                    st.write(f"手機: {card['mobile']}")
                    st.write(f"傳真: {card['fax']}")
                    st.write(f"Email: {card['email']}")
                
                st.write("**地址和網站**")
                st.write(f"地址: {card['address']}")
                st.write(f"網站: {card['website']}")
                
                st.write("**其他資訊**")
                st.write(f"統編: {card['tax_id']}")
                st.write(f"其他: {card['other_info']}")
                
                # 編輯按鈕
                if st.button(f"編輯 #{idx+1}"):
                    st.session_state.editing_card = idx
                    st.experimental_rerun()
    else:
        st.info("目前沒有儲存的名片記錄")

# 頁面底部
st.markdown("---")
st.markdown("### 💡 使用說明")
st.markdown("""
- 上傳名片圖片進行自動識別
- 識別結果可以直接編輯
- 儲存的資料可在歷史記錄中查看
- 支援多種名片格式和語言
""") 