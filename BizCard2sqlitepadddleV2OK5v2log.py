import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import io
import sqlite3
from paddleocr import PaddleOCR


from openai import OpenAI
import time

#from busrestfuldata import Busscardload
import json
import pickle
import base64
from busrestfuldataV2 import ContactPerson,Company
import requests

import logging  # 加入 logging 模組
import os
import datetime


# 設定日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bizcardx.log'),  # 將日誌寫入檔案
        logging.StreamHandler()  # 同時輸出到控制台
    ],
    force=True
)
logger = logging.getLogger(__name__)


# 定義儲存圖片的資料夾（相對路徑）
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(uploaded_file):
    try:
        # 生成唯一的檔案名稱（使用時間戳）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = uploaded_file.name.split('.')[-1]
        file_name = f"image_{timestamp}.{file_extension}"
        
        # 建立儲存路徑
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # 儲存檔案
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path
    except Exception as e:
        st.error(f"儲存檔案時發生錯誤: {e}")
        return None


client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="xxxxxxxxxxxx",
    #base_url="https://api.chatanywhere.tech/v1"
    #base_url="https://api.chatanywhere.tech/v1"
    base_url="https://api.chatanywhere.tech/v1/"
    
)

#chatgptapi 格式
####
####
# messages =[
#   {
#     "role": "user",
#     "content": "一變頻器列穩壓器, 可程式交流電源, 可程式直流電源, 直流電源供應器, 歐源電子有限公司, 新北市235中和區中山路三段110號3樓二6, 張育豪, TEL:(02)2225-0320FAX:(027)2225-4568, 深圳, 097229B-028, TEL:(755)2661-5361FAX:(755)2661-5367, E-mail: imaino@allpower.com.tw, Http://www.allpower.com.tw, 統一編號：842428９6"",這是名片檔的解析,幫我區分姓名、住址，電話，統編，FAX，website, email, 公司名，其他 "
#   }
# ]

# 正規表達式，保留中文和英文字母，並過濾空鍵
def clean_keys(d):
    cleaned_data = {}
    for key, value in d.items():
        # 僅保留中文和英文字母
        new_key = re.sub(r'[^A-Za-z\u4e00-\u9fff]', '', key)
        # 如果清理後的 key 不為空，則加入字典
        if new_key:
            cleaned_data[new_key] = value
    return cleaned_data


# 非流式响应
def gpt_35_api(messages: list):
    """为提供的对话消息创建新的回答

    Args:
        messages (list): 完整的对话消息
    """
    start_time = time.time()
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    print(completion.choices[0].message.content)
    end_time = time.time() - start_time
    print(end_time)
    return completion.choices[0].message.content

def chatgptjson(completion_message):

    # print("chatgptjsonin")
    # print(completion_message)
    # print("xxxxxxxxx")

# 依照換行符分割成一個字串列表
    message_lines = completion_message.split('\n')
    
    print(message_lines)
    print("message_lines")

    # 初始化一個空字典
    message_dict = {}

    # 將每一行訊息按照冒號分割成鍵值對，並加入到字典中
    for line in message_lines:
        #key_value = line.split('：')  # 
        
        if '：' in line:
            key_value = line.split('：')  # 中文全形冒號
        elif ':' in line:
            key_value = line.split(':')  # 英文半形冒號
        
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip() 
            message_dict[key] = value

    # 印出轉換後的字典檔
    print("chatgptjsonout")
    print(message_dict)
    #正規表達式，保留中文和英文字母，並過濾空鍵

    message_dict=clean_keys(message_dict)
    
    
    

    return message_dict

 
    
# 資料給chatgpt      chatgptmessage

def chatgptstring(text1,text2):
    messages =[
  {
    "role": "user",
    "content": "{},{}".format(text1,text2)
  }
]

    return messages


# ocr = PaddleOCR(lang="ch",
#                 use_gpu=False,
#                 det_model_dir="../paddleORC_model/ch_ppocr_server_v2.0_det_infer/",
#                 cls_model_dir="ch_ppocr_mobile_v2.0_cls_infer/",
#                 rec_model_dir="ch_ppocr_server_v2.0_rec_infer/")

#0527 ocr V3 版本
ocr = PaddleOCR(lang="chinese_cht",
                use_gpu=False,
                det_model_dir="../paddleORC_model/ch_ppocr_server_v2.0_det_infer/",
                cls_model_dir="ch_ppocr_mobile_v2.0_cls_infer/",
                rec_model_dir="chinese_cht_PP-OCRv3_rec_infer/") 

# # ocr V4 版本 中文版本是有問題
# ocr = PaddleOCR(lang="chinese_cht",
#                 use_gpu=False,
#                 det_model_dir="ch_PP-OCRv4_det_infer/",
#                 cls_model_dir="ch_ppocr_mobile_v2.0_cls_infer/",
#                 rec_model_dir="ch_PP-OCRv4_rec_infer/")


def img_to_text(path):
    image = []
    input_IMG1 = Image.open(path)
    input_IMG1_Array = np.array(input_IMG1)

    #ocr = PaddleOCR(use_angle_cls=True, lang='en')  # need to run only once to download and load model into memory
    result = ocr.ocr(input_IMG1_Array)
    
    #result = ocr.ocr(input_IMG1_Array, det=False, cls=True)

    plt.imshow(input_IMG1_Array)
    plt.axis('off')
    plt.show()

        
    for line in result:
        for word in line:
            image.append(word[1][0])


    print("detect_text")
    print(image)
    #chatgptinputstring = '{} {} {}'.format(image, "")

    print("debug")

    return image, input_IMG1

def extracting_data2(dict1):
    
    parsed_info = {
        "Name": [],
        "Address": [],
        "AddressEng": [],
        "Telephone": [],
        "Mobile": [],
        "Email": [],
        "Website": [],
        "Fax": [],
        "CompanyName": [],
        "BusinessNo": [],
        "Other": [],
        "Business_Card": []
    }

    name = dict1.get("姓名", "")
    if name:
        parsed_info["Name"].append(name)
     
    # Parsing Address
    address = dict1.get("住址", "")
    address2 = dict1.get("地址", "")
    
    if address:
        parsed_info["Address"].append(address)
    if address2:
        parsed_info["Address"].append(address2)


    # Parsing Telephone and Mobile
    telephone = dict1.get("電話", "")
    
    # if telephone:
    #     parsed_info["Telephone"].append(telephone)

    
    

    #mobile = re.findall(r'\b\d{5}-\d{7,8}\b', telephone)
    
    if telephone:
        #parsed_info["Mobile"].extend(mobile)
        parsed_info["Telephone"].append(telephone)
    else:
        parsed_info["Telephone"].append(telephone)

    
    mobile1 = dict1.get("手機", "")
    if mobile1:
        parsed_info["Mobile"].append(mobile1)
    

    
    # Parsing Email and E-mail
    email = dict1.get("Email", "")
    e_mail = dict1.get("E-Mail", "")
    e_mail2 = dict1.get("email", "")
    e_mail3 = dict1.get("E-mail", "")
    if email:
        parsed_info["Email"].append(email)
    if e_mail:
        parsed_info["Email"].append(e_mail)
    if e_mail2:
        parsed_info["Email"].append(e_mail2)
    if e_mail3:
        parsed_info["Email"].append(e_mail3)



    # Parsing Website
    website = dict1.get("Website", "")
    website2 = dict1.get("網站", "")
    website3 = dict1.get("website", "")
    if website:
        parsed_info["Website"].append(website)
    if website2:
        parsed_info["Website"].append(website2)
    if website3:
        parsed_info["Website"].append(website3)



    # Parsing Fax
    fax = dict1.get("FAX", "")
    fax2 = dict1.get("傳真", "")
    if fax:
        parsed_info["Fax"].append(fax)
    if fax2:
        parsed_info["Fax"].append(fax2)


    # Parsing Company Name
    company_name = dict1.get("公司名稱", "")
    if company_name:
        parsed_info["CompanyName"].append(company_name)

    # Parsing Business Number
    business_no = dict1.get("統一編號", "")
    business_no2 = dict1.get("統編", "")
    
    if business_no:
        parsed_info["BusinessNo"].append(business_no)
    if business_no2:
        parsed_info["BusinessNo"].append(business_no2)

    # Parsing Other Information
    other_info = dict1.get("其他", "")
    if other_info:
        parsed_info["Other"].append(other_info)

    
    for key, value in parsed_info.items():
        if len(value)==0:
            
            value = "N/A"
            parsed_info[key] = [value]    
    

    # dict1 = {"Name": [],
    #          "Address": [],
    #          "AddressEng":[],
    #          "Telephone": [],
    #          "Mobile":[],
    #          "Email": [],
    #          "Website": [],
    #          "Fax":[],
    #          "CompanyName":[],
    #          "BusinessNo":[],
    #          "Other":[],
    #          "Business_Card": []
    #          }
    
    # dict1['Name'].append(text.get("姓名"))
    # dict1['Address'].append(text.get("住址"))
    # dict1['AddressEng'].append(text.get("英文住址"))
    # dict1['Telephone'].append(text.get("電話"))
    # dict1['Mobile'].append(text.get("手機"))
    
    # if "統編" in text:
    #     dict1['BusinessNo'].append(text.get("統編"))
    # elif "統一編號" in text:
    #     dict1['BusinessNo'].append(text.get("統一編號"))
    # else:
    #     dict1['BusinessNo'].append(text.get("統編"))
    
    
    # dict1['Fax'].append(text.get("FAX"))
    # dict1['Website'].append(text.get("網站"))
    # dict1['Email'].append(text.get("Email"))
    # dict1['CompanyName'].append(text.get("公司名稱"))
    # dict1['Other'].append(text.get("其他"))
    # dict1['Business_Card'] =["N/A"]
    
    # # for key, value in dict1.items():
    # #     if len(value)>0:
    # #         concad = " ".join(value)
    # #         dict1[key] = [concad]

    # #     else:
    # #         value = "N/A"
    # #         dict1[key] = [value]    
       


    return parsed_info


def extracting_data1(text):
    dict1 = {"Name": [],
             "Designation": [],
             "Address": [],
             "AddressEng":[],
             "Telephone": [],
             "Mobile":[],
             "Email_ID": [],
             "Website": [],
             "Fax":[],
             "CompanyName":[],
             "BusinessNo":[],
             "Mark":[],
             "Business_Card": []
             }
    
    dict1['Name'].append(text[0])
    dict1['Designation'].append(text[1])

    for i in range(len(text)):
        if text[i].startswith("+") or (text[i].replace("-", "").isdigit() and '-' in text[i]):
            dict1["Telephone"].append(text[i])

        elif "@" in text[i] and ".com" in text[i]:
            dict1["Email_ID"].append(text[i])

        elif "WWW" in text[i] or "www" in text[i] or "Www" in text[i] or "wwW" in text[i] or "wWw" in text[i] or ".com" in text[i]:
            normal = text[i].lower()
            dict1["Website"].append(normal)

        elif "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or text[i].isdigit():
            dict1["Address"].append(text[i])

        elif re.match(r'^[A-Za-z]', text[i]):
            dict1["Business_Card"].append(text[i])

        else:
            remove_colon = re.sub(r'[,;]','',text[i])
            dict1["Address"].append(remove_colon)

    for key, value in dict1.items():
        if len(value)>0:
            concad = " ".join(value)
            dict1[key] = [concad]

        else:
            value = "N/A"
            dict1[key] = [value]    
       


    return dict1


# Streamlit Part
st.title("BizCardX: Extracting Business Card Data with OCR")

tabs = st.sidebar.selectbox(
    "Navigation",
    ["EXTRACTING AND TRANSFERING", "MODIFYING & INSERTING"]
)

# if tabs == "Title":
#     pass

if tabs == "EXTRACTING AND TRANSFERING":
    insert = st.file_uploader("Upload the Image to Extract The Details", type=["png", "jpg", "jpeg"])
    if insert:
        
        logger.info(f"File uploaded: {insert.name}")
        #舊版的正規化文字解析
        image_text, input_image = img_to_text(insert)
        #pddf = extracting_data1(image_text)
        logger.info("OCR processing completed")


        #組合問chatgpt 訊息 prompt
        #text2="這是名片檔的解析,幫我區分姓名、住址，電話，統編，FAX，website, email, 公司名稱，手機，其他"

        #組合問chatgpt 訊息 prompt
        text2="這是名片檔的解析,幫我區分姓名、住址，電話，統編，FAX，website, email, 公司名稱，手機，其他"
    

        reschatmsg=chatgptstring(image_text,text2)

        #使用 chatgpt3.5 解析 nlp 的意思
        respongpt=gpt_35_api(reschatmsg)

        logger.info("GPT-3.5 API call completed")        

        msgdic=chatgptjson(respongpt)
        
        #查完後的資料需解析過
       
        msgdf=extracting_data2(msgdic)

        #把檔案傳到server

        file_path = save_uploaded_file(insert)

        logger.info("Data extracted and parsed into dictionary")

        print("msgdf")
        print(msgdf)
        print("msgdfxxxxxxx")
        
        #新增到資料庫中
        #使用chatgpt資料
        print('bdf1')
        df1 = pd.DataFrame(msgdf)
        print('afterdf1')
        #新增到資料庫中
        #舊的方式舊資料格式 
        #df1 = pd.DataFrame(pddf)


        st.image(input_image, caption='Uploaded Image.', use_column_width=True)
        #把解析的資料不呈現
        # st.write("OCR Extracted Text:")
        # st.write(image_text)
        # st.write("NLP Extracted Data:")
        # #st.write(pddf)
        # st.write(msgdf)
        st.write("DataFrame".upper())

        # Convert the image to bytes
        Img_Byte = io.BytesIO()
        input_image.save(Img_Byte, format="PNG")
        Img_data = Img_Byte.getvalue()
        
        print("image_image_image")
        print("Img_data")
        Img_data = Img_Byte.getvalue()
        print(type(Img_data))

        print("type(Img_data)")


        # Add the image byte data to the DataFrame
        df1["Image_Byte"] = [Img_data]

        # Display the DataFrame
        st.dataframe(df1)
        org_df = pd.DataFrame(msgdf)

        print("xxxx-----------xxxx")
        print(org_df)
        print("org_df")

        modified_DF = org_df.copy()

        print(modified_DF)
        # image_bytes = org_df["Image_Byte"].iloc[0]
        # image_stream = io.BytesIO(image_bytes)
    

        M_name = st.text_input("NAME", org_df["Name"].iloc[0])
        M_address = st.text_input("ADDRESS", org_df["Address"].iloc[0])
        M_addresseng = st.text_input("ADDRESS ENG", org_df["AddressEng"].iloc[0])
        M_telephone = st.text_input("TELEPHONE", org_df["Telephone"].iloc[0])
        M_mobile = st.text_input("MOBILE", org_df["Mobile"].iloc[0])
        M_email = st.text_input("EMAIL", org_df["Email"].iloc[0])
        M_website = st.text_input("WEBSITE", org_df["Website"].iloc[0])
        M_fax = st.text_input("FAX", org_df["Fax"].iloc[0])
        M_companyname = st.text_input("COMPANY NAME", org_df["CompanyName"].iloc[0])
        M_businessno = st.text_input("BUSINESS NO", org_df["BusinessNo"].iloc[0])
        M_other = st.text_input("OTHER", org_df["Other"].iloc[0])
        M_bz = st.text_input("BUSINESS CARD", org_df["Business_Card"].iloc[0])
        #M_ib = st.text_input("Image Byte", org_df["Image_Byte"].iloc[0])
        #Img_data = image_stream.getvalue()
            
        

        
        modified_DF["name"]= M_name
        modified_DF["address"]= M_address
        modified_DF["addresseng"]= M_addresseng
        
        modified_DF["telephone"]= M_telephone
        modified_DF["mobile"]= M_mobile
        
        modified_DF["email"]= M_email
        modified_DF["website"]= M_website
        modified_DF["fax"]= M_fax
        modified_DF["companyname"]= M_companyname
        modified_DF["businessno"]= M_businessno

        modified_DF["other"]= M_other

        modified_DF["business_card"]= M_bz
        modified_DF["Image_Byte"]= [Img_data]
        
        

        # st.write("MODIFIED DATA BASE")
        # st.dataframe(modified_DF)


        if st.button("Transfer To SQL"):
            try:
                
                logger.info("Starting SQL transfer process")

                # Example usage with the provided data
                contact_person_data = ContactPerson(
                    name= M_name ,
                    email=M_email,
                    landline_number= M_telephone,
                    cellphone_number= M_mobile,
                    address= M_address,
                )

                company_data = Company(
                    name= M_companyname,
                    tax= M_fax,
                    tax_id_number = M_businessno,
                    trade_method="Company Name 2",
                    #contact_persons=[contact_person_data],
                )

                #print(company_data.to_dict())

                
                type(Img_data)
                
                #new
                #busload.set_image_from_blob(image_stream)
                # 傳送到伺服器
                #server_url = "https://example.com/api/busscardload"  # 替換為實際伺服器 URL
                #server_url = "http://172.16.11.86:3333/api/createBusinessPartner"
                #server_url = "http://172.16.11.86:3333/api/business-partner"
                server_url = "http://172.16.11.41:3333/api/business-partner"

                
                # 假设 values 和 dataSource 是 Python 字典
                values = company_data.to_dict()
                dataSource = [contact_person_data.to_dict()]

                print("filename1")
                print(insert.name)
                print("filename")
                # 假设 fileList 是一个包含文件路径的列表
                fileList = [insert.name]

                # 创建 form-data
                form_data = {
                    "data": (None, json.dumps(values), "application/json"),  # 发送 JSON 数据
                    "contactPersons": (None, json.dumps(dataSource), "application/json")
                }
                
               
                # 添加文件
                files = []
                #for file_path in fileList:
                files.append(("imageBase64", (file_path, open(file_path, "rb"), "image/jpeg")))


                logger.info(f"Sending data to server: {server_url}")

                response = requests.post(server_url, files={**form_data, **dict(files)})

                
                
                #new
                
                # print(busload.image)
                # print("busload.image")
                # print(type(busload.image))
                # print("type busload.image")

                # image_data = base64.b64decode(busload.image)
                # image2 = Image.open(io.BytesIO(image_data))
                # image2.save('20250107.jpg')


                
                # img.save('20250107.jpg')

            
                # # 将对象写入文件
                # with open("20250106bus_class.pkl", "wb") as file:
                #     pickle.dump(busload, file)
                
                
            # 保存对象到文件
                # with open("20250206businesscard.json", "w") as file:
                #     #old
                #     #json.dump(busload.to_dict(), file)
                #     # new version
                #     #json.dump(contact_person_data.to_dict(), file)
                #     json.dump(company_data.to_dict(), file)
                    
                # print("对象已保存到 person.json 文件。")

                #old
                #response = busload.send_to_server(server_url)
                #new version
                #response = contact_person_data.send_to_server(server_url)
                #response = company_data.send_to_server(server_url)


                # response dic
                print("busloadsexxxx")
                print(response.text)
                print("response0000")
                print(type(response.text))
                
                
                #把資料轉為json
                s = response.text
                #把資料重組成json格式
                response = json.loads(s)
                
                logger.info(f"Sending data to server: {server_url}")
               
                # 顯示伺服器回應
                if isinstance(response, dict) and response.get("message") == "Success!":
                    print("Server Response (200 OK):", response)
                    logger.info("Data successfully saved to server")

                elif response.get("error"):
                    print("Error:", response["error"])
                    #logger.error(f"Server error occurred: {response["error"]}")
                    logger.error(f"Server error occurred: {response.get('error', 'Unknown error')}")
                else:
                    print("Unexpected Response:", response)

                # # 顯示伺服器回應
                # if isinstance(response, dict) and response.get("status_code") == 200:
                #     print("Server Response (200 OK):", response)
                # elif response.get("error"):
                #     print("Error:", response["error"])
                # else:
                #     print("Unexpected Response:", response)



                
                st.success("Data saved successfully!")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                logger.error(f"EXTRACTING AND TRANSFERING error occurred: {str(e)}", exc_info=True)
               

elif tabs == "MODIFYING & INSERTING":

    # insert = st.file_uploader("Upload the Image to Extract The Details", type=["png", "jpg", "jpeg"])
    
    # if insert:
    #     # 圖片轉文字
    #     image_text, input_image = img_to_text(insert)
        
    #     # 準備ChatGPT提示
    #     text2 = "這是名片檔的解析,幫我區分姓名、住址，電話，統編，FAX，website, email, 公司名稱，手機，其他"
    #     reschatmsg = chatgptstring(image_text, text2)
        
    #     # 使用GPT-3.5解析
    #     respongpt = gpt_35_api(reschatmsg)
    #     msgdic = chatgptjson(respongpt)
    #     msgdf = extracting_data2(msgdic)
        
    #     # 轉為DataFrame
    #     df1 = pd.DataFrame(msgdf)
        
    #     # 將圖片轉為bytes
    #     Img_Byte = io.BytesIO()
    #     input_image.save(Img_Byte, format="PNG")
    #     Img_data = Img_Byte.getvalue()
        
    #     # 將圖片bytes加入DataFrame
    #     df1["Image_Byte"] = [Img_data]
        
    #     # 顯示原始圖片和識別結果
    #     st.image(input_image, caption='Uploaded Image.', use_column_width=True)
    #     st.write("DATAFRAME".upper())
    #     st.dataframe(df1)
        
    #     # 建立修改用的副本
    #     modified_DF = df1.copy()
        
    #     # 提供人工修改介面，使用原始識別結果作為預設值
    #     with st.form(key='modify_form'):
    #         M_name = st.text_input("NAME", value=modified_DF.get("Name", [""])[0])
    #         M_address = st.text_input("ADDRESS", value=modified_DF.get("Address", [""])[0])
    #         M_addresseng = st.text_input("ADDRESS ENG", value=modified_DF.get("AddressEng", [""])[0])
    #         M_telephone = st.text_input("TELEPHONE", value=modified_DF.get("Telephone", [""])[0])
    #         M_mobile = st.text_input("MOBILE", value=modified_DF.get("Mobile", [""])[0])
    #         M_email = st.text_input("EMAIL", value=modified_DF.get("Email", [""])[0])
    #         M_website = st.text_input("WEBSITE", value=modified_DF.get("Website", [""])[0])
    #         M_fax = st.text_input("FAX", value=modified_DF.get("Fax", [""])[0])
    #         M_companyname = st.text_input("COMPANY NAME", value=modified_DF.get("CompanyName", [""])[0])
    #         M_businessno = st.text_input("BUSINESS NO", value=modified_DF.get("BusinessNo", [""])[0])
    #         M_other = st.text_input("OTHER", value=modified_DF.get("Other", [""])[0])
    #         M_bz = st.text_input("BUSINESS CARD", value=modified_DF.get("Business_Card", [""])[0])
            
    #         submit_button = st.form_submit_button(label='Confirm Modifications')
        
    #     # 更新修改後的資料
    #     if submit_button:
    #         modified_DF["Name"] = [M_name]
    #         modified_DF["Address"] = [M_address]
    #         modified_DF["AddressEng"] = [M_addresseng]
    #         modified_DF["Telephone"] = [M_telephone]
    #         modified_DF["Mobile"] = [M_mobile]
    #         modified_DF["Email"] = [M_email]
    #         modified_DF["Website"] = [M_website]
    #         modified_DF["Fax"] = [M_fax]
    #         modified_DF["CompanyName"] = [M_companyname]
    #         modified_DF["BusinessNo"] = [M_businessno]
    #         modified_DF["Other"] = [M_other]
    #         modified_DF["Business_Card"] = [M_bz]
    #         modified_DF["Image_Byte"] = [Img_data]
            
    #         st.write("MODIFIED DATABASE")
    #         st.dataframe(modified_DF)
        
    #     # 傳輸到SQL
    #     if st.button("Transfer To SQL"):
    #         try:
    #             contact_person_data = ContactPerson(
    #                 name=M_name,
    #                 email=M_email,
    #                 landline_number=M_telephone,
    #                 cellphone_number=M_mobile,
    #                 address=M_address,
    #             )

    #             company_data = Company(
    #                 name=M_companyname,
    #                 tax=M_fax,
    #                 tax_id_number=M_businessno,
    #                 trade_method="Company Name 2",
    #             )

    #             server_url = "http://172.16.11.41:3333/api/business-partner"
                
    #             values = company_data.to_dict()
    #             dataSource = [contact_person_data.to_dict()]
    #             fileList = [insert.name]

    #             # 準備form-data
    #             form_data = {
    #                 "data": (None, json.dumps(values), "application/json"),
    #                 "contactPersons": (None, json.dumps(dataSource), "application/json")
    #             }
                
    #             # 添加文件
    #             files = [("imageBase64", (insert.name, insert.getvalue(), "image/jpeg"))]
                
    #             response = requests.post(server_url, files=files, data=form_data)
                
    #             response_json = response.json()
                
    #             if response_json.get("message") == "Success!":
    #                 st.success("Data saved successfully!")
    #             else:
    #                 st.error(f"Server error: {response_json.get('error', 'Unknown error')}")
                    
    #         except Exception as e:
    #             st.error(f"An error occurred: {str(e)}")

        insert = st.file_uploader("Upload the Image to Extract The Details", type=["png", "jpg", "jpeg"])
        if insert:
            image_text, input_image = img_to_text(insert)
            text2 = "這是名片檔的解析,幫我區分姓名、住址，電話，統編，FAX，website, email, 公司名稱，手機，其他"
            reschatmsg = chatgptstring(image_text, text2)
            respongpt = gpt_35_api(reschatmsg)
            msgdic = chatgptjson(respongpt)
            msgdf = extracting_data2(msgdic)
            df1 = pd.DataFrame(msgdf)
            
            st.image(input_image, caption='Uploaded Image.', use_column_width=True)
            st.write("DataFrame")
            
            Img_Byte = io.BytesIO()
            input_image.save(Img_Byte, format="PNG")
            Img_data = Img_Byte.getvalue()
            
            df1["Image_Byte"] = [Img_data]
            st.dataframe(df1)
            
            modified_DF = df1.copy()
            
            # 讓使用者手動輸入數據
            for col in ["Name", "Address", "AddressEng", "Telephone", "Mobile", "Email", "Website", "Fax", "CompanyName", "BusinessNo", "Other", "Business_Card"]:
                modified_DF[col] = st.text_input(col.upper(), df1[col].iloc[0])
            
            modified_DF["Image_Byte"] = [Img_data]
            st.write("MODIFIED DATA BASE")
            st.dataframe(modified_DF)
            
            if st.button("Transfer To SQL"):
                try:
                    contact_person_data = ContactPerson(
                        name=modified_DF["Name"].iloc[0],
                        email=modified_DF["Email"].iloc[0],
                        landline_number=modified_DF["Telephone"].iloc[0],
                        cellphone_number=modified_DF["Mobile"].iloc[0],
                        address=modified_DF["Address"].iloc[0],
                    )
                    
                    company_data = Company(
                        name=modified_DF["CompanyName"].iloc[0],
                        tax=modified_DF["Fax"].iloc[0],
                        tax_id_number=modified_DF["BusinessNo"].iloc[0],
                        trade_method="Company Name 2",
                    )
                    
                    server_url = "http://172.16.11.41:3333/api/business-partner"
                    values = company_data.to_dict()
                    dataSource = [contact_person_data.to_dict()]
                    
                    form_data = {
                        "data": (None, json.dumps(values), "application/json"),
                        "contactPersons": (None, json.dumps(dataSource), "application/json")
                    }
                    
                    files = {"imageBase64": (insert.name, insert.getvalue(), "image/jpeg")}
                    response = requests.post(server_url, files={**form_data, **files})
                    
                    response_json = response.json()
                    
                    if response_json.get("message") == "Success!":
                        st.success("Data saved successfully!")
                    else:
                        st.error(f"Server Error: {response_json}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
