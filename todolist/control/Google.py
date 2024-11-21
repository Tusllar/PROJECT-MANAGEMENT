from google.oauth2 import service_account # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.http import MediaIoBaseDownload
import os
import win32com.client
from googleapiclient.http import MediaFileUpload,MediaIoBaseUpload
import pythoncom
PARENT_FOLDER_ID = "161T4j3VgAVtD0uWEGRbnYqkavyyYmqh_" 
# # Hàm xác thực với Google Drive
def authenticate():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'pbl3.json'
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
     # call Drive API client
    service = build('drive', 'v3', credentials=creds)
    return service
def word_to_pdf(input_file,output_file):
    pythoncom.CoInitialize()
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
        pythoncom.CoUninitialize()
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
    file_link, file_id = upload_file(pdf_file)
    print(f"File link: {file_link}")
    print(f"File ID: {file_id}")
    return file_link,file_id 

def upload_file(file_path):
    service = authenticate()
    
    # Tạo metadata cho file upload
    file_metadata = {'name': os.path.basename(file_path)}
    
    if PARENT_FOLDER_ID:
        file_metadata['parents'] = [PARENT_FOLDER_ID]
    
    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
    
    # Tải file lên Google Drive
    request = service.files().create(media_body=media, body=file_metadata)
    file = request.execute()
    
    # Lấy link tải về của file
    file_link = f"https://drive.google.com/file/d/{file['id']}/view?usp=sharing"
    print("File uploaded successfully")
    return file_link,file['id']