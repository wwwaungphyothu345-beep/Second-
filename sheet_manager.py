import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class SheetManager:
    def __init__(self):
        # 💡 Render ရဲ့ Environment Variable ထဲက 'GOOGLE_CREDS_JSON' စာသားကို ယူဖတ်ခြင်း
        creds_json = os.environ.get("GOOGLE_CREDS_JSON")
        
        if creds_json:
            # စာသားကို JSON format အဖြစ် ပြန်ပြောင်းပြီး အသိအမှတ်ပြုခြင်း
            info = json.loads(creds_json)
            self.creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        else:
            # Local စမ်းသပ်မှုအတွက် credentials.json ရှိရင် ဖတ်ရန် (Fallback)
            self.creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
            
        self.client = gspread.authorize(self.creds)
        
        # ⚠️ အရေးကြီး - အစ်ကို့ရဲ့ Google Sheet ID အစစ်ကို ဒီနေရာမှာ ထည့်ပေးပါ
        self.sheet = self.client.open_by_key("မင်းရဲ့_GOOGLE_SHEET_ID_ကိုဒီမှာထည့်ပါ")
        
        worksheets = {ws.title.strip(): ws for ws in self.sheet.worksheets()}
        self.products_tab = worksheets.get("Products")
        self.cod_tab = worksheets.get("COD")
        self.settings_tab = worksheets.get("Settings")
        self.orders_tab = worksheets.get("Orders")

    def get_bank_accounts(self):
        if self.settings_tab:
            return self.settings_tab.get_all_records()
        return []

    def check_cod_township(self, township_query):
        if not self.cod_tab:
            return {"found": False, "cod_status": "Pre-paid"}
        records = self.cod_tab.get_all_records()
        for r in records:
            if township_query.lower() in str(r.get("Township", "")).lower():
                return {
                    "found": True,
                    "township": r.get("Township"),
                    "deli": r.get("Deli"),
                    "cod_status": r.get("COD")
                }
        return {"found": False, "cod_status": "Pre-paid"}

    def search_product(self, name_query):
        if not self.products_tab:
            return []
        records = self.products_tab.get_all_records()
        results = []
        for r in records:
            if name_query.lower() in str(r.get("Product Name", "")).lower():
                results.append(r)
        return results

    def add_new_order(self, order_id, customer_name, phone, address, items, total_amount, status="Pending"):
        if self.orders_tab:
            self.orders_tab.append_row([order_id, customer_name, phone, address, items, total_amount, status])
            return True
        return False
