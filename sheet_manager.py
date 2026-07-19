import gspread
from google.oauth2.service_account import Credentials

# Google Sheets API Authorization Setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class SheetManager:
    def __init__(self, spreadsheet_name="database"):
        # credentials.json ဖိုင်ကို ဖတ်ပြီး Google API နဲ့ ချိတ်ဆက်ခြင်း
        self.creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open(spreadsheet_name)
        
        # Tabs မန်နေဂျာများ
        self.products_tab = self.sheet.worksheet("Products")
        self.cod_tab = self.sheet.worksheet("COD")
        self.settings_tab = self.sheet.worksheet("Settings")
        self.orders_tab = self.sheet.worksheet("Orders")

    def search_product(self, name_query):
        """ပစ္စည်းအမည်ကို ရှာဖွေပြီး စျေးနှုန်းနှင့် လက်ကျန်ပြသရန်"""
        records = self.products_tab.get_all_records()
        results = []
        for r in records:
            if name_query.lower() in str(r.get("Product Name", "")).lower():
                results.append(r)
        return results

    def check_cod_township(self, township_query):
        """မြို့နယ်အလိုက် COD ရမရ နှင့် Deli ခ စစ်ဆေးရန်"""
        records = self.cod_tab.get_all_records()
        for r in records:
            # User ရိုက်လိုက်တဲ့ မြို့နယ် ပါမပါ စစ်ဆေးခြင်း
            if township_query.lower() in str(r.get("Township", "")).lower():
                return {
                    "found": True,
                    "township": r.get("Township"),
                    "deli": r.get("Deli"),
                    "cod_status": r.get("COD")  # Home Delivery / ဂိတ်ချ / ဂိတ်ချ (ငွေကြို)
                }
        return {"found": False, "cod_status": "Pre-paid"}

    def get_bank_accounts(self):
        """ငွေကြိုလွှဲရမည့် ဘဏ်အကောင့်များကို Settings မှ ဆွဲထုတ်ရန်"""
        return self.settings_tab.get_all_records()

    def add_new_order(self, order_id, customer_name, phone, address, items, total_amount, status="Pending"):
        """အော်ဒါအသစ်ကို Orders tab ထဲ သွားသိမ်းရန်"""
        # Orders tab မှာ column ခေါင်းစဉ်တွေ ရှိပြီးသားဖြစ်ရပါမယ်
        # Order_ID | Customer_Name | Phone | Address | Items | Total | Status
        self.orders_tab.append_row([order_id, customer_name, phone, address, items, total_amount, status])
        return True
