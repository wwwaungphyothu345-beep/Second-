class SheetManager:
    def __init__(self):
        print("Google Sheet connection completely bypassed.")

    def get_bank_accounts(self):
        return [{"Bank_Name": "Kpay", "Account_Number": "09123456789", "Account_Name": "Dummy Name"}]

    def check_cod_township(self, township_query):
        return {"found": True, "township": township_query, "cod_status": "Home Delivery"}

    def add_new_order(self, order_id, customer_name, phone, address, items, total_amount, status="Pending"):
        return True
