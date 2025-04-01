import os
import time
import difPy


def delete_old_files_and_empty_dirs(path, days):
    now = time.time()
    cutoff = now - days * 86400
    for root, dirs, files in os.walk(path, topdown=False):  # topdown=False 從下往上遍歷
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                if os.stat(file_path).st_mtime < cutoff:
                    os.remove(file_path)
                    print(f"已刪除檔案: {file_path}")
        # 檢查資料夾是否為空，若空則刪除
        if not os.listdir(root):
            os.rmdir(root)
            print(f"已刪除空資料夾: {root}")

if __name__ == "__main__":
    path = "path/to/your/directory"
    days = 5
    
    delete_old_files_and_empty_dirs(path, days)
    
    dif = difPy.build('C:/Path/to/Folder/')
    search = difPy.search(dif)


    