import time

from google import genai
from google.genai import types


from PIL import Image

#api_key = "xxx"

api_key = "xxx"


client = genai.Client(api_key=api_key)

#MODEL_ID = "gemini-2.5-pro-exp-03-25"

MODEL_ID = "gemini-2.0-flash" # @param ["gemini-1.5-flash-latest","gemini-2.0-flash-lite","gemini-2.0-flash","gemini-2.5-pro-exp-03-25"] {"allow-input":true}
#MODEL_ID = "gemini-2.5-pro-exp-03-25"

img = Image.open("tool.jpg")
img = img.resize((800, int(800 * img.size[1] / img.size[0])), Image.Resampling.LANCZOS)

def analyze_image(img, prompt, max_retries=5, retry_delay=1):
    for attempt in range(max_retries):
        try:
            image_response = client.models.generate_content(
                model=MODEL_ID,
                contents=[img, prompt],
                config=types.GenerateContentConfig(temperature=0.5)
            )
            return image_response.text
        # except genai_module.types.GenerateContentError as e:
        #     if "blocked" in str(e).lower(): #check if the error is blocked.
        #         print(f"Content blocked: {e}")
        #         return None
        #     else:
        #         print(f"GenerateContentError: {e}")
        #         return None
        except Exception as e:
            if "429" in str(e):
                print(f"429 error, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"An unexpected error occurred: {e}")
                return None
    print("Max retries exceeded.")
    return None

# prompt = """
#     Point to no more than 10 items in the image, include spill.
#     The answer should follow the json format: [{"point": <point>, "label": <label1>}, ...]. The points are in [y, x] format normalized to 0-1000.
#     """
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

result = analyze_image(img, prompt)
if result:
    print(result)

