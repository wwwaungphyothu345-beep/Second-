from fastapi import FastAPI, Request, Response
from agent_brain import AIAgentBrain
from telegram_manager import TelegramManager
import requests
import uuid

app = FastAPI()
ai_brain = AIAgentBrain()
tg_manager = TelegramManager()

FB_PAGE_ACCESS_TOKEN = "မင်းရဲ့_FACEBOOK_PAGE_ACCESS_TOKEN"
FB_VERIFY_TOKEN = "မင်းသတ်မှတ်မည့်_အိုင်ဒီလျှို့ဝှက်ချက်_TOKEN" # ဥပမာ- my_secret_agent_123

def send_fb_message(recipient_id, text_message):
    """Facebook Customer ထံသို့ စာလှမ်းပြန်သည့် Function"""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text_message}
    }
    requests.post(url, json=payload)

@app.get("/")
def home():
    # Render ပေါ်မှာ Live ဖြစ်မဖြစ် အမြဲတမ်း စစ်လို့ရအောင် ကျန်းမာရေးစစ်ဆေးချက် ပေးထားခြင်း
    return {"status": "AI Agent is running 24/7 successfully"}

@app.get("/webhook")
def verify_fb_webhook(request: Request):
    """Facebook က Webhook လာချိတ်ရင် Verify လုပ်ပေးမည့်အပိုင်း"""
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == FB_VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"))
    return "Verification failed"

@app.post("/webhook")
async def handle_fb_messages(request: Request):
    """Facebook Customer ဆီက စာဝင်လာရင် AI က ဖတ်ပြီး တွေးတောတုံ့ပြန်မည့်အပိုင်း"""
    body = await request.json()
    
    if body.get("object") == "page":
        for entry in body.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")
                    
                    if message_text:
                        # 🧠 AI Agent Brain ထံ စာပို့ပြီး အဖြေတောင်းခြင်း
                        # (ဒီနေရာမှာ လုပ်ငန်းခွင်သုံး Memory အတွက် Chat History ကို ယာယီ ဗလာထားထားပါတယ်)
                        ai_response = ai_brain.handle_customer_message(sender_id, message_text, chat_history=[])
                        
                        # AI က ပုံမှန်စာပြန်ခိုင်းရင်
                        if ai_response["type"] == "text":
                            send_fb_message(sender_id, ai_response["data"])
                        
                        # AI က လိပ်စာစစ်လို့ ပြီးသွားရင် (COD / Pre-paid ဆုံးဖြတ်ချက်)
                        elif ai_response["type"] == "cod_check":
                            cod_data = ai_response["data"]
                            order_id = str(uuid.uuid4())[:8] # ထူးခြားတဲ့ Order ID ဆောက်ခြင်း
                            
                            if cod_data["found"] and "Home Delivery" in cod_data["cod_status"]:
                                # COD ရရင် Packing တိုက်ရိုက်ပို့
                                send_fb_message(sender_id, f"ဟုတ်ကဲ့ပါရှင်။ လူကြီးမင်းမြို့နယ်က COD (ပစ္စည်းရောက်ငွေချေ) ရပါတယ်ရှင်။ အော်ဒါအမှတ်က #{order_id} ဖြစ်ပါတယ်ရှင်။")
                                tg_manager.send_to_packing(order_id, "Customer", "09xxxxxxx", cod_data["township"], "မှာယူသည့်ပစ္စည်းစာရင်း")
                            else:
                                # COD မရရင် ငွေကြိုလွှဲခိုင်းပြီး ဘဏ်အကောင့်ပေး
                                banks = ai_brain.sheet_manager.get_bank_accounts()
                                bank_text = "\n".join([f"- {b['Bank_Name']}: {b['Account_Number']} ({b['Account_Name']})" for b in banks])
                                send_fb_message(sender_id, f"စိတ်မရှိပါနဲ့ရှင်၊ လူကြီးမင်းရဲ့မြို့နယ်က COD မရသေးလို့ ငွေကြိုလွှဲပေးရပါမယ်ရှင်။ အော်ဒါအမှတ်က #{order_id} ဖြစ်ပါတယ်။\n\nလွှဲရမည့်အကောင့်များ-\n{bank_text}\n\nလွှဲပြီးရင် Screenshot ပို့ပေးပါရှင်။")
                                
    return "EVENT_RECEIVED"

@app.post("/telegram-webhook")
async def handle_telegram_callback(request: Request):
    """Telegram Group ထဲက ခလုတ်တွေနှိပ်ရင် အလုပ်လုပ်မည့်အပိုင်း"""
    body = await request.json()
    
    if "callback_query" in body:
        callback_data = body["callback_query"]["data"]
        # ခလုတ်နှိပ်ချက်အရ (ဥပမာ- fin_approve_1234, pack_done_1234)
        # ၎င်း ဒေတာကိုခွဲထုတ်ပြီး Facebook customer ဆီ စာအလိုအလျောက် သွားပြန်ပေးမည့် စနစ်ကို ရေးရပါမည်။
        
        # TODO: Database ထဲတွင် သိမ်းထားသော Customer ID ကို ဆွဲထုတ်ပြီး `send_fb_message` လှမ်းလုပ်ခြင်း
        pass
        
    return {"status": "success"}
