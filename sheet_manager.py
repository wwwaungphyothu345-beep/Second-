import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

class SheetManager:
    def __init__(self):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Base64 အဖြစ် ပြောင်းထားသော JSON ကို ဖတ်ယူခြင်း
        creds_b64 = os.environ.get("GOOGLE_CREDS_BASE64")
        if creds_b64:
            creds_json = base64.b64decode(creds_b64).decode('utf-8')
            creds_dict = json.loads(creds_json)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        else:
            credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
            
        self.client = gspread.authorize(credentials)
        # အစ်ကို့ရဲ့ Google Sheet ID
        self.sheet = self.client.open_by_key("YOUR_GOOGLE_SHEET_ID_HERE")

    def search_product(self, keyword):
        try:
            worksheet = self.sheet.sheet1
            records = worksheet.get_all_records()
            results = []
            for row in records:
                if any(keyword.lower() in str(val).lower() for val in row.values()):
                    results.append(row)
            return results
        except Exception as e:
            print(f"Sheet Search Error: {e}")
            return []

    def get_bank_accounts(self):
        try:
            worksheet = self.sheet.worksheet("Bank")
            return worksheet.get_all_records()
        except Exception:
            return []
