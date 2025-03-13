import torch
import torch.nn as nn
import os
from tqdm import tqdm
import pandas as pd
from PIL import Image, ImageOps
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# drive_service is defined in the beginning of views
GCP_CLIENT_SECRET = os.getenv("GCP_CLIENT_SECRET")
if GCP_CLIENT_SECRET == None:
    GCP_CLIENT_SECRET = ''

SCOPES = ["https://www.googleapis.com/auth/drive"]
client_config = {
    "installed":{
        "client_id":"253879512770-0ot833ecqqo5ndk7a0me08u0upi2l931.apps.googleusercontent.com",
        "project_id":"iconic-baton-453304-b6",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":GCP_CLIENT_SECRET,"redirect_uris":["http://localhost"]}}
# Set up OAuth authentication
flow = InstalledAppFlow.from_client_config(
    client_config,  # Specify the OAuth client ID JSON obtained from GCP
    SCOPES
)
credentials = flow.run_local_server(port=0)  # Open a login screen for authentication
# Create a Google Drive API client
drive_service = build("drive", "v3", credentials=credentials)

class GoogleOCR:
    def __init__(self,prob_ths=0.5,imsz=700,device='cpu'):
        self.device = device
        
        self.prob_ths = prob_ths
        self.imsz = imsz
    
    def get_text_from_doc(self,doc_id):
        request = drive_service.files().export_media(fileId=doc_id, mimeType="text/plain")
        content = request.execute()
        return content.decode("utf-8")

    def upload_image(self,image_path='temp.png'):
        # file_metadata = {
        #     "name": os.path.basename(image_path),
        #     "parents":['1MT6I_Xw_EbpzUxl-2tAVCM3r16mIITZ-'],
        #     "mimeType": "application/vnd.google-apps.document",
        # }
        media = MediaFileUpload(image_path, mimetype="image/png")
        # file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        updated_file = drive_service.files().update(
            fileId='10SdTXRMXKe2OWIWVf8v7pc7B40kCwc-RH0go4jEUrzU',
            media_body=media,  # The new file content you want to upload
            fields="id"  # Specify the fields you want to retrieve (in this case, only the file ID)
        ).execute()

        return updated_file.get("id")
    
    def predict(self,im):
        npim = np.array(im)
        npim = np.rot90(npim, k=-1) # rotate 90deg  
        step = self.imsz // 2

        response = {}

        for i in range(0, npim.shape[0] - self.imsz + 1, step):
            for j in range(0, npim.shape[1] - self.imsz + 1, step):
                print(i,j)
                # Crop the image patch
                patch = npim[i:i + self.imsz, j:j + self.imsz]

                # Save the patch as a separate image file using PIL
                patch_img = Image.fromarray(patch).convert('L')
                patch_img = ImageOps.equalize(patch_img)
                patch_filename = f"temp.png"
                patch_img.save(patch_filename)

                id = self.upload_image(patch_filename)
                text  = self.get_text_from_doc(id)

                for txt in text:
                    response[txt] = 0.0

        return response