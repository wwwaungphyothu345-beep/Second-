import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class SheetManager:
    def __init__(self):
        # credentials.json ကို ဖတ်ပြီး ချိတ်ဆက်ခြင်း
        self.creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        self.client = gspread.authorize(self.creds)
        
        # ⚠️ အရေးကြီး - "မင်းရဲ့_GOOGLE_SHEET_ID_ကိုဒီမှာထည့်ပါ" နေရာတွင် စောစောက Copy ကူးလာသော ID ထည့်ပါ
        # ဥပမာ - self.sheet = self.client.open_by_key("1abc123XYZ...")
        self.sheet = self.client.open_by_key("1CJf69o5Gp_oxtoE7tDog3KPov-ylC0jc67T4XTuFlxU")
        
        # နာမည်အတိအကျကို စာလုံးအကြီးအသေးပါမကျန် သေချာစွာ Map လုပ်ခြင်း
        self.products_tab = self.sheet.worksheet("Products")
        self.cod_tab = self.sheet.worksheet("COD")
        self.settings_tab = self.sheet.worksheet("Settings")
        
        # Orders tab မရှိသေးလျှင် Crash မဖြစ်စေရန် try-except ဖြင့် ပိတ်ထားခြင်း
        try:
            self.orders_tab = self.sheet.worksheet("Orders")
        except gspread.exceptions.WorksheetNotFound:
            self.orders_tab = None

    def search_product(self, name_query):
        records = self.products_tab.get_all_records()
        results = []
        for r in records:
            if name_query.lower() in str(r.get("Product Name", "")).lower():
                results.append(r)
        return results

    def check_cod_township(self, township_query):
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

    def get_bank_accounts(self):
        return self.settings_tab.get_all_records()

    def add_new_order(self, order_id, customer_name, phone, address, items, total_amount, status="Pending"):
        if self.orders_tab:
            self.orders_tab.append_row([order_id, customer_name, phone, address, items, total_amount, status])
            return True
        return False
