from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sheet_manager import SheetManager

app = FastAPI()
sheet_manager = SheetManager()

VERIFY_TOKEN = "my_super_secret_token_123"

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    # Meta ဘက်က တောင်းဆိုချက်ကို ကွက်တိ စစ်ဆေးခြင်း
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        # ⚠️ အရေးကြီး - JSON မဟုတ်ဘဲ Plain Text သီးသန့်ဖြင့် Challenge ကို ပြန်ပေးရပါမည်
        return PlainTextResponse(content=challenge, status_code=200)
        
    return PlainTextResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print("Received webhook data:", data)
    return {"status": "EVENT_RECEIVED"}
