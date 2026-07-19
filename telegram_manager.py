import requests

TELEGRAM_BOT_TOKEN = "မင်းရဲ့_TELEGRAM_BOT_TOKEN"
# Telegram Group ID များကို ဤနေရာတွင် ထည့်ပါ (ဥပမာ- -100xxxxxxxxx)
FINANCE_GROUP_ID = "မင်းရဲ့_FINANCE_GROUP_ID"
PACKING_GROUP_ID = "မင်းရဲ့_PACKING_GROUP_ID"

class TelegramManager:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    def send_to_finance(self, order_id, customer_name, amount, screenshot_url=None):
        """Finance Group သို့ Screenshot နှင့်အတူ စစ်ဆေးရန် ခလုတ်များ ပို့ခြင်း"""
        text = f"💰 **[ငွေလွှဲစစ်ဆေးရန်]**\nOrder ID: #{order_id}\nဝယ်သူ: {customer_name}\nကျသင့်ငွေ: {amount} MMK"
        
        # Inline Buttons (ခလုတ်များ တပ်ဆင်ခြင်း)
        reply_markup = {
            "inline_keyboard": [[
                {"text": "ငွေဝင်ပြီ ✅", "callback_data": f"fin_approve_{order_id}"},
                {"text": "အတု/မှားနေသည် ❌", "callback_data": f"fin_reject_{order_id}"}
            ]]
        }
        
        if screenshot_url:
            # ပုံပါလာလျှင် ပုံနှင့်တကွ ပို့မည်
            payload = {
                "chat_id": FINANCE_GROUP_ID,
                "photo": screenshot_url,
                "caption": text,
                "reply_markup": reply_markup,
                "parse_mode": "Markdown"
            }
            requests.post(f"{self.api_url}/sendPhoto", json=payload)
        else:
            payload = {
                "chat_id": FINANCE_GROUP_ID,
                "text": text,
                "reply_markup": reply_markup,
                "parse_mode": "Markdown"
            }
            requests.post(f"{self.api_url}/sendMessage", json=payload)

    def send_to_packing(self, order_id, customer_name, phone, address, items):
        """Packing Group သို့ ပါဆယ်ထုတ်ရန် ပို့ခြင်း"""
        text = (f"📦 **[ပါဆယ်ထုတ်ပိုးရန်]**\n"
                f"Order ID: #{order_id}\n"
                f"ဝယ်သူ: {customer_name}\n"
                f"ဖုန်း: {phone}\n"
                f"လိပ်စာ: {address}\n"
                f"ပစ္စည်းစာရင်း: {items}")
        
        reply_markup = {
            "inline_keyboard": [[
                {"text": "ထုတ်ပိုးပြီးပါပြီ 🟢", "callback_data": f"pack_done_{order_id}"}
            ]]
        }
        
        payload = {
            "chat_id": PACKING_GROUP_ID,
            "text": text,
            "reply_markup": reply_markup,
            "parse_mode": "Markdown"
        }
        requests.post(f"{self.api_url}/sendMessage", json=payload)
