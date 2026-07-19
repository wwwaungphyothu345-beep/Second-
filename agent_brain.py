import os
from google import genai
from google.genai import types
from sheet_manager import SheetManager

# Google AI Studio မှ ရလာတဲ့ API Key ကို ဤနေရာတွင် ထည့်ပါ
# သို့မဟုတ် Terminal Environment ထဲတွင် သတ်မှတ်နိုင်သည်
GEMINI_API_KEY = "မင်းရဲ့_GEMINI_API_KEY_ကိုဒီမှာထည့်ပါ"

class AIAgentBrain:
    def __init__(self):
        # Gemini Client အသစ်ကို နောက်ဆုံး google-genai SDK ဖြင့် ဆောက်ခြင်း
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.sheet_manager = SheetManager()
        
        # AI ကို အရောင်းဝန်ထမ်း လေသံထွက်အောင် ပုံသွင်းမည့် ညွှန်ကြားချက်များ (System Instruction)
        self.system_instruction = """
        မင်းက လူမှုဆက်ဆံရေး အရမ်းကောင်းပြီး စိတ်ရှည်တဲ့ မြန်မာအမျိုးသမီး အရောင်းဝန်ထမ်းတစ်ယောက် ဖြစ်တယ်။
        Customer တွေကို အမြဲတမ်း ယဉ်ကျေးပျူငှာစွာ စာပြန်ရမယ် (ဥပမာ- ဟုတ်ကဲ့ရှင့်၊ မင်္ဂလာပါရှင်၊ ဟုတ်ကဲ့ပါရှင်)။
        
        မင်းမှာ အောက်ပါ တာဝန်တွေ ရှိတယ် -
        ၁။ Customer က ပစ္စည်းမေးရင် search_product tool ကို သုံးပြီး ရှာဖွေရှင်းပြရမယ်။
        ၂။ မှာယူချင်တယ်ဆိုရင် အမည်၊ ဖုန်း၊ လိပ်စာ အပြည့်အစုံ တောင်းရမယ်။
        ၃။ လိပ်စာ ရပြီဆိုတာနဲ့ check_cod_township tool ကို သုံးပြီး COD ရမရ ချက်ချင်း စစ်ရမယ်။
        ၄။ COD မရတဲ့ မြို့ဖြစ်နေရင် 'ငွေကြိုလွှဲရမှာဖြစ်ကြောင်း' ရှင်းပြပြီး get_bank_accounts tool ကို သုံးပြီး ဘဏ်အကောင့်တွေ ထုတ်ပေးရမယ်။
        
        အရေးကြီးသော စည်းကမ်း - မင်းမသိတဲ့ ပစ္စည်းစာရင်းတွေ၊ ဘဏ်အကောင့်တွေကို စိတ်ကူးယဉ်ပြီး မဖြေပါနဲ့။ Tools တွေထဲက ဒေတာကိုပဲ အခြေခံပြီး လူလို ပြောပြပါ။
        """

    def handle_customer_message(self, customer_id, message_text, chat_history=[]):
        """Customer ဆီက စာဝင်လာရင် AI က စဉ်းစားပြီး တုံ့ပြန်မည့် လုပ်ငန်းစဉ်"""
        
        # Gemini သုံးမည့် Tools (Functions) စာရင်းကို သတ်မှတ်ခြင်း
        tools = [
            self.sheet_manager.search_product,
            self.sheet_manager.check_cod_township,
            self.sheet_manager.get_bank_accounts
        ]
        
        # စကားပြော History (Context) ကို Gemini Format သို့ ပြောင်းလဲခြင်း
        # (စမ်းသပ်ရန် အခြေခံ chat conversion)
        contents = []
        for chat in chat_history:
            contents.append(
                types.Content(
                    role="user" if chat['role'] == 'user' else 'model',
                    parts=[types.Part.from_text(text=chat['text'])]
                )
            )
        
        # လက်ရှိ ဝင်လာသော စာကို ထည့်ပေါင်းခြင်း
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=message_text)])
        )
        
        # Gemini 1.5 Pro သို့မဟုတ် Flash ကို Function Calling ဖြင့် မောင်းနှင်ခြင်း
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=tools,
            temperature=0.7 # စကားပြော ပိုမို သဘာဝကျစေရန်
        )
        
        # Gemini 1.5 Flash သည် မြန်ဆန်ပြီး စီးပွားဖြစ်အတွက် တွက်ခြေကိုက်သည်
        response = self.client.models.generate_content(
            model='gemini-1.5-flash',
            contents=contents,
            config=config
        )
        
        # --- Function Calling (Tools) ကို AI က သုံးရန် ဆုံးဖြတ်ခဲ့လျှင် ၎င်းကို လုပ်ဆောင်ခြင်း ---
        if response.function_calls:
            for function_call in response.function_calls:
                name = function_call.name
                args = function_call.args
                
                # ၁။ ပစ္စည်းရှာသည့် Tool ဖြစ်ခဲ့လျှင်
                if name == "search_product":
                    result = self.sheet_manager.search_product(args.get("name_query"))
                    return {"type": "text", "data": f"[System Update: ပစ္စည်းရှာဖွေတွေ့ရှိမှု - {result}]", "trigger_tool": "search_product", "tool_result": result}
                
                # ၂။ COD စစ်သည့် Tool ဖြစ်ခဲ့လျှင်
                elif name == "check_cod_township":
                    result = self.sheet_manager.check_cod_township(args.get("township_query"))
                    return {"type": "cod_check", "data": result}
                
                # ၃။ ဘဏ်အကောင့် တောင်းသည့် Tool ဖြစ်ခဲ့လျှင်
                elif name == "get_bank_accounts":
                    result = self.sheet_manager.get_bank_accounts()
                    return {"type": "text", "data": f"[System Update: ဘဏ်အကောင့်များ - {result}]"}
        
        # ပုံမှန် စာပြန်ခြင်း ဖြစ်ပါက စာသားကို တိုက်ရိုက် ပြန်ပေးမည်
        return {"type": "text", "data": response.text}
