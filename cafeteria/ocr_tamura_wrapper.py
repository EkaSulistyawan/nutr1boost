import torch
import torch.nn as nn
import os
from tqdm import tqdm
import pandas as pd
from PIL import Image, ImageOps
import numpy as np
import os
import io
import requests
import json
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleOCR:
    def __init__(self,prob_ths=0.5,imsz=700,device='cpu'):
        self.device = device
        self.prob_ths = prob_ths
        self.imsz = imsz

        # self.drive_service is defined in the beginning of views
        self.GCP_CLIENT_SECRET = os.getenv("GCP_CLIENT_SECRET")
        if self.GCP_CLIENT_SECRET == None:
            self.GCP_CLIENT_SECRET = ''
    
    def get_text_from_doc(self,doc_id):
        request = self.drive_service.files().export_media(fileId=doc_id, mimeType="text/plain")
        content = request.execute()
        return content.decode("utf-8")

    def get_text_from_image(self,image_path='temp.png'):
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()

            # Encode image to base64
            encoded_image = base64.b64encode(content).decode('utf-8')

            # Create JSON data for API request
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.GCP_CLIENT_SECRET}"
            headers = {"Content-Type": "application/json"}
            data = {
                "requests": [
                    {
                        "image": {"content": encoded_image},
                        "features": [{"type": "TEXT_DETECTION"}]
                    }
                ]
            }

            # Call the API
            response = requests.post(url, headers=headers, data=json.dumps(data))

            # Parse the result
            if response.status_code == 200:
                result = response.json()
                texts = result["responses"][0].get("textAnnotations", [])
                return texts[0]["description"] if texts else ""
            else:
                print(f"API request error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling Google Cloud Vision API: {e}")
            return ""
    
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

                text = self.get_text_from_image(patch_filename)

                for txt in text.split():
                    print(txt)
                    response[txt] = 0.0

        return response