import win32com.client
from flask import request
import os
from werkzeug.utils import secure_filename
from Google import authenticate
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
def word_to_pdf(input_file,output_file):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(input_file)
        doc.SaveAs(output_file, FileFormat=17)
        print("success pdf")
    except Exception as e:
        print("Error: ", e)
    finally:
        doc.Close()
        word.Quit()
    
def download_file(file_id,name,output_folder='C:/downloads'):
    service = authenticate()  # Xác thực Google API (chắc chắn bạn đã định nghĩa hàm này)
    os.makedirs(output_folder, exist_ok=True)
    # Đặt đường dẫn tệp đầu ra
    file_path = os.path.join(output_folder, f'{name}.docx')  # Tên tệp sẽ tải về
    # Lấy đối tượng request từ Google Drive API
    request = service.files().get_media(fileId=file_id)
    # Tùy chỉnh kích thước chunk là 5MB (5 * 1024 * 1024 bytes)
    chunk_size = 5 * 1024 * 1024  # 5MB mỗi phân đoạn
    # Tải tệp về
    with open(file_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request, chunksize=chunk_size)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")
    print("Download completed!")
    word_file = rf'C:\downloads\{name}.docx'  # Đường dẫn tới file Word
    pdf_file = rf'C:\downloads\{name}.pdf'
    word_to_pdf(word_file,pdf_file)



