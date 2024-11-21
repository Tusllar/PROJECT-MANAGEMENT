from flask import Blueprint, render_template, flash, request, jsonify,redirect,url_for
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from werkzeug.exceptions import RequestURITooLarge
from googleapiclient.http import MediaIoBaseDownload
from .models import Note,User_infor,File
from . import db
from todolist.control.Google import authenticate,download_file,word_to_pdf
from googleapiclient.errors import HttpError # type: ignore
from googleapiclient.http import MediaFileUpload,MediaIoBaseUpload
import os
from io import BytesIO
from werkzeug.utils import secure_filename
import win32com.client
from flask import send_from_directory
views = Blueprint("views", __name__)
PARENT_FOLDER_ID = "161T4j3VgAVtD0uWEGRbnYqkavyyYmqh_" 
TYPE_FILE=['docx','pdf']

def checkformat(type):
    if type in TYPE_FILE:
        return 1
    else:
        return 0

@views.route("/home", methods=["GET", "POST"])
@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if file.filename.split(".")[1] not in TYPE_FILE:
        #     flash("Not help this type file",category="error")
        #     return redirect(request.url)
        
        print(file.filename.split('.'))
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        service = authenticate()
        try:
            file_metadata={
                'name': file.filename,
                'parents':[PARENT_FOLDER_ID]
            }
            file_name, type = os.path.splitext(file.filename)
            file_content = BytesIO(file.read())  # Đọc và lưu tệp vào bộ nhớ

            # Tạo đối tượng MediaIoBaseUpload để tải tệp lên Google Drive
            media = MediaIoBaseUpload(file_content, mimetype='application/octet-stream')
            
            # Upload the file to Google Drive
            file = (
                service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    fields='id,mimeType'
                )
                .execute()
            )
            file_id = file.get('id')
            permission = {
                'type': 'anyone',
                'role': 'writer'
            }
            service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            file_Type = file.get('mimeType')
            print(file_id)
            print(file_name)
            print(type)
            # download_file1(file_id,file_name)
            if file_Type =='application/vnd.openxmlformats-officedocument.wordprocessingml.document':
               print(f"https://docs.google.com/document/d/{file_id}/edit")
               file_link = f"https://docs.google.com/document/d/{file_id}/edit"
            elif file_Type == 'application/pdf':
               print(f"https://drive.google.com/file/d/{file_id}/view")
               file_link = f"https://drive.google.com/file/d/{file_id}/view"
            else:
               print(f"https://docs.google.com/presentation/d/{file_id}/edit")
               file_link = f"https://docs.google.com/presentation/d/{file_id}/edit"
            
            new_file = File(
                
                filename=file_name,
                filetype=type,
                link=file_link,
                user_id = current_user.id,
                file_id = file_id
            )
            db.session.add(new_file)
            db.session.commit()
            return redirect(request.url)
        except HttpError as error:
           print(f"An error occurred: {error}")
           file = None
    user_files = File.query.filter_by(user_id=current_user.id).all()    
    user_info = User_infor.query.filter_by(user_id=current_user.id).first()

    return render_template("index.html", user=current_user,user_info=user_info,user_files=user_files)

# 
@views.route("/download_file_pdf", methods=["GET"])
@login_required
def download_file_pdf():
    file_id = request.args.get("file_id")
    name = request.args.get("file_name")  
    output_folder = "C:/downloads"
    service = authenticate()
    os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, f'{name}.pdf')  
    request_file = service.files().get_media(fileId=file_id)
    chunk_size =  1024 * 1024  # 5MB mỗi phân đoạn
    with open(file_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request_file, chunksize=chunk_size)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")
    print("Download completed!")
    return send_from_directory(directory=output_folder, path=f'{name}.pdf', as_attachment=True)
    # return f"File {name} và  {file_id} not found"
  
@views.route("/convert_file", methods=["GET"])
@login_required
def convert_file():
    file_id = request.args.get("file_id")
    name = request.args.get("file_name")  
    file = File.query.filter_by(file_id=file_id).first()
    if file.link_convert:
        print("hehe")
    else:  
        print(file.link_convert)
    
        link,fileid = download_file(file_id,name)
            
        if file:
                print(file.filename)
                print(f"File found: {file.link_convert}")
                file.link_convert = link
                file.file_id_convert = fileid
                print(f"File found: {file.link_convert}")
                db.session.commit()
    user_files = File.query.filter_by(user_id=current_user.id).all()
    user_info = User_infor.query.filter_by(user_id=current_user.id).first()
    return render_template("index.html", user=current_user,user_info=user_info,user_files=user_files)



