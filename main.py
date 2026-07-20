import os
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sheet_manager import SheetManager
import google.generativeai as genai

app = FastAPI()
sheet_manager = SheetManager()

VERIFY_TOKEN = "my_super_secret_token_123"
FB_PAGE_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

def generate_ai_response(user_message):
    try:
        products = sheet_manager.search_product(user_message)
        bank_accounts = sheet_manager.get_bank_accounts()
        context = f"မင်္ဂလာပါ။ သင်သည် လူကြီးမင်း၏ ဆိုင်အတွက် AI အရောင်းကိုယ်စားလှယ် ဖြစ်သည်။\n"
        if products:
            context += f"ရှာဖွေတွေ့ရှိသော ပစ္စည်းအချက်အလက်များ- {str(products)}\n"
        else:
            context += "လက်ရှိ ရှာဖွေထားသော ပစ္စည်းမျိုး မတွေ့ရှိပါ။\n"
            
        context += f"ဆိုင်၏ ဘဏ်အကောင့်များ- {str(bank_accounts)}\n"
        context += "Customer ကို ယဉ်ကျေးပျူငှာစွာ မြန်မာလို စကားပြန်ပေးပါ။ ပစ္စည်းဈေးနှုန်းနှင့် အချက်အလက်များကို အပေါ်က Context အတိုင်းသာ မှန်ကန်စွာ ဖြေကြားပေးပါ။"

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"{context}\n\nCustomer: {user_message}")
        return response.text
    except Exception as e:
     import traceback
     error_details = traceback.format_exc()
     print("====== !!! DETAILED AI ERROR !!! ======")
     print(error_details)
     print("=======================================")
     return "ခဏနေမှ ပြန်စာပို့ပေးပါဦးခင်ဗျာ။"
    
async def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={FB_PAGE_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(content=params.get("hub.challenge"), status_code=200)
    return PlainTextResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def handle_fb_webhook(request: Request):
    data = await request.json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message") and not messaging_event["message"].get("is_echo"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"]["text"]
                    
                     ai_reply = generate_ai_response(user_text)
                    await send_fb_message(sender_id, ai_reply)
    return {"status": "EVENT_RECEIVED"}

@app.post(f"/telegram/{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else "/telegram/webhook")
async def handle_telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
          ai_reply = generate_ai_response(user_text)
        
          telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(telegram_url, json={"chat_id": chat_id, "text": ai_reply})
            
    return {"status": "ok"}
