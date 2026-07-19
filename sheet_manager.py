class SheetManager:
    def __init__(self):
        print("Google Sheet connection skipped for now.")

    def get_bank_accounts(self):
        # စမ်းသပ်ချက် အချက်အလက်အတု
        return [{"Bank_Name": "Kpay", "Account_Number": "09123456789", "Account_Name": "Dummy Name"}]

    def check_cod_township(self, township_query):
        # အမြဲတမ်း COD ရသည်ဟု ပြပေးမည်
        return {"found": True, "township": township_query, "cod_status": "Home Delivery"}

    def add_new_order(self, order_id, customer_name, phone, address, items, total_amount, status="Pending"):
        print(f"Order {order_id} recorded in log instead of sheet.")
        return True
