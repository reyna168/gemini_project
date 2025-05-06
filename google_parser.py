import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def clean_text(text):
    # 移除多餘的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?，。！？]', '', text)
    return text.strip()

def parse_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 自動檢測編碼
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除不需要的元素
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # 獲取標題
        title = soup.title.string if soup.title else "無標題"
        
        # 獲取主要內容
        content = []
        
        # 獲取所有段落
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = clean_text(p.get_text())
            if text:
                content.append(text)
        
        # 獲取列表內容
        for ul in soup.find_all(['ul', 'ol']):
            for li in ul.find_all('li'):
                text = clean_text(li.get_text())
                if text:
                    content.append(f"• {text}")
        
        return {
            'title': clean_text(title),
            'content': content
        }
    
    except requests.RequestException as e:
        print(f"解析網頁時發生錯誤: {e}")
        return None

def main():
    url = input("請輸入要解析的網頁網址: ")
    result = parse_webpage(url)
    
    if result:
        print("\n" + "="*50)
        print(f"網頁標題: {result['title']}")
        print("="*50 + "\n")
        
        print("網頁內容:")
        print("-"*50)
        for i, text in enumerate(result['content'], 1):
            print(f"{i}. {text}")
            print("-"*50)

if __name__ == "__main__":
    main() 