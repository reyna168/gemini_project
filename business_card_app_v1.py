import streamlit as st
import os
from PIL import Image
import json
import tempfile
from google import genai
from google.genai import types
import time
import logging
from datetime import datetime

# 設置日誌系統
def setup_logging():
    # 創建 logs 目錄（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 設置日誌檔案名稱（包含日期）
    log_filename = f'logs/business_card_system_{datetime.now().strftime("%Y%m%d")}.log'
    
    # 配置日誌系統
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 設置第三方庫的日誌級別
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)

# 初始化日誌系統
setup_logging()
logger = logging.getLogger(__name__)

# Gemini API 設置
#GOOGLE_API_KEY = "YOUR_API_KEY"  # 請替換成你的 API 
#api_key = "AIzaSyD1GjdcUrcYeL-KdR7gZyjxlO0d9OGO2OA"

GOOGLE_API_KEY = "xxx"

MODEL_ID = "gemini-2.0-flash"

class BusinessCardAnalyzer:
    def __init__(self):
        logger.info("初始化 BusinessCardAnalyzer")
        try:
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
            logger.info("Gemini API 客戶端初始化成功")
        except Exception as e:
            logger.error(f"Gemini API 客戶端初始化失敗: {str(e)}")
            raise
    
    def analyze_image(self, img, max_retries=5, retry_delay=1):
        logger.info("開始分析名片圖片")
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
                logger.debug(f"嘗試第 {attempt + 1} 次分析")
                image_response = self.client.models.generate_content(
                    model=MODEL_ID,
                    contents=[img, prompt],
                    config=genai.types.GenerateContentConfig(temperature=0.5)
                )
                
                try:
                    response_text = image_response.text
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        result = json.loads(json_str)
                        logger.info("名片分析成功")
                        return result
                    logger.warning("無法在回應中找到有效的 JSON")
                    return None
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析錯誤: {str(e)}")
                    return None
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning(f"遇到速率限制，等待 {retry_delay} 秒後重試")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"分析過程發生錯誤: {str(e)}")
                    return None
        logger.error("已達最大重試次數，分析失敗")
        return None

# Streamlit 應用界面設置
try:
    st.set_page_config(
        page_title="名片識別系統",
        page_icon="📇",
        layout="wide"
    )
    logger.info("Streamlit 頁面配置完成")
except Exception as e:
    logger.error(f"Streamlit 頁面配置失敗: {str(e)}")

# 初始化分析器
@st.cache_resource
def init_analyzer():
    try:
        analyzer = BusinessCardAnalyzer()
        logger.info("分析器初始化成功")
        return analyzer
    except Exception as e:
        logger.error(f"分析器初始化失敗: {str(e)}")
        raise

try:
    analyzer = init_analyzer()
except Exception as e:
    st.error("系統初始化失敗，請檢查設定或聯絡管理員")
    logger.critical(f"系統初始化失敗: {str(e)}")
    st.stop()

# 側邊欄
with st.sidebar:
    st.title("名片識別系統")
    choice = st.radio(
        "功能選擇",
        ["名片識別", "歷史記錄"]
    )
    logger.debug(f"用戶選擇功能: {choice}")

# 主要識別頁面
if choice == "名片識別":
    st.header("📸 名片識別與編輯")
    
    uploaded_file = st.file_uploader("上傳名片圖片", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        logger.info(f"用戶上傳檔案: {uploaded_file.name}")
        try:
            # 顯示圖片
            col1, col2 = st.columns(2)
            with col1:
                image = Image.open(uploaded_file)
                resized_img = image.resize((800, int(800 * image.size[1] / image.size[0])), Image.Resampling.LANCZOS)
                st.image(resized_img, caption="上傳的名片", use_column_width=True)
                logger.debug("圖片顯示成功")
            
            # 識別按鈕
            if st.button("開始識別"):
                logger.info("開始識別流程")
                with st.spinner("正在識別名片..."):
                    result = analyzer.analyze_image(resized_img)
                    
                    if result:
                        logger.info("名片識別成功")
                        with col2:
                            st.success("識別完成！")
                            # 顯示識別結果並允許編輯
                            with st.form("edit_form"):
                                st.subheader("識別結果")
                                
                                # 基本信息
                                name = st.text_input("姓名", result.get('name', ''))
                                company = st.text_input("公司名稱", result.get('company_name', ''))
                                title = st.text_input("職稱", result.get('title', ''))
                                print(name+''+company+" "+title)
                                
                                # 聯絡方式
                                st.subheader("聯絡方式")
                                phone = st.text_input("電話", result.get('phone', ''))
                                mobile = st.text_input("手機", result.get('mobile', ''))
                                fax = st.text_input("傳真", result.get('fax', ''))
                                email = st.text_input("電子郵件", result.get('email', ''))
                                print(phone+''+mobile+''+fax+''+email)
                                
                                # 地址和網站
                                st.subheader("地址和網站")
                                address = st.text_area("地址", result.get('address', ''))
                                website = st.text_input("網站", result.get('website', ''))
                                print(address+''+website)
                                # 其他信息
                                st.subheader("其他信息")
                                tax_id = st.text_input("統一編號", result.get('tax_id', ''))
                                other = st.text_area("其他資訊", result.get('other_info', ''))
                                print(tax_id+''+other)
                                
                                # 
                                
                                if st.form_submit_button("儲存資料"):
                                    try:
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
                                        print(save_data)

                                        
                                        if not isinstance(st.session_state.saved_cards, list):
                                            st.session_state.saved_cards = []

                                        st.session_state.saved_cards.append(save_data)

                                        logger.info(f"成功儲存名片資料: {save_data['name']}")
                                        st.success("資料已成功儲存！")
                                    except Exception as e:
                                        logger.error(f"儲存資料時發生錯誤: {str(e)}")
                                        st.error("儲存資料失敗")
                    else:
                        logger.error("名片識別失敗")
                        st.error("識別失敗，請確認圖片品質後重試。")
        except Exception as e:
            logger.error(f"處理上傳檔案時發生錯誤: {str(e)}")
            st.error("處理圖片時發生錯誤")

# 歷史記錄頁面
elif choice == "歷史記錄":
    logger.info("進入歷史記錄頁面")
    st.header("📋 歷史記錄")
    
    if 'saved_cards' in st.session_state and st.session_state.saved_cards:
        logger.debug(f"顯示 {len(st.session_state.saved_cards)} 筆歷史記錄")
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
        logger.info("無歷史記錄")
        st.info("目前沒有儲存的名片記錄")

# 頁面底部
st.markdown("---")
st.markdown("### �� 使用說明")
st.markdown("""
- 上傳名片圖片進行自動識別
- 識別結果可以直接編輯
- 儲存的資料可在歷史記錄中查看
- 支援多種名片格式和語言
""")

# 錯誤處理裝飾器
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"函數 {func.__name__} 執行時發生錯誤: {str(e)}")
            st.error("系統發生錯誤，請稍後再試")
    return wrapper

# 應用程式啟動日誌
logger.info("名片識別系統啟動完成")