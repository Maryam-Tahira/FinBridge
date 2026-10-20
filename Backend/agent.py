"""
FinBridge AI Agent — Dual Mode
Mode 1: Smart saved replies for finance topics (always works)
Mode 2: OpenAI for general questions (needs API key)
"""

import os
import json

# Try to load OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    HAS_KEY = bool(os.getenv("OPENAI_API_KEY"))
except:
    client = None
    HAS_KEY = False

SYSTEM_PROMPT = """You are FinBridge, an AI cross-border student finance assistant.
You help international students with currency, remittance, budgeting, 
tuition payments, and banking (especially China: Alipay, WeChat Pay, UnionPay).
Be helpful, specific with numbers, and friendly. Keep replies concise."""

TOOLS = [
    {"type": "function", "function": {"name": "convert_currency", "description": "Convert currency",
        "parameters": {"type": "object", "properties": {
            "from_currency": {"type": "string"}, "to_currency": {"type": "string"}, "amount": {"type": "number"}
        }, "required": ["from_currency", "to_currency", "amount"]}}},
    {"type": "function", "function": {"name": "compare_remittance", "description": "Compare money transfer services",
        "parameters": {"type": "object", "properties": {
            "from_country": {"type": "string"}, "to_country": {"type": "string"}, "amount_usd": {"type": "number"}
        }, "required": ["from_country", "to_country", "amount_usd"]}}}
]


def smart_reply(query):
    """Built-in smart replies for finance topics — always works, no API needed"""
    q = query.lower()

    if any(w in q for w in ['alipay', 'wechat', 'mobile pay', 'weixin']):
        return {
            "reply": "📱 **WeChat Pay Setup:**\n• Download WeChat → Me → Services → Wallet\n• Bind Chinese bank card OR foreign passport\n• Since 2023, Visa/Mastercard can link directly\n• QR scan payments everywhere\n\n📱 **Alipay Setup:**\n• Download Alipay → Tour Pass for foreigners\n• Link Visa/MC → spend in CNY, charged in your currency\n• Best for Taobao, Tmall, online shopping\n• Yu'e Bao for savings interest\n\n💡 **Tip:** Use BOTH — WeChat for social payments, Alipay for shopping!",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['bank account', 'chinese bank', 'open account', 'open bank']):
        return {
            "reply": "🏦 **Opening a Chinese Bank Account:**\n\n**You need:**\n✅ Passport (with valid visa)\n✅ University admission letter\n✅ Chinese SIM card (China Mobile recommended)\n✅ Registration proof from university\n\n**Best banks for students:**\n• 🏦 Bank of China — Best for international transfers\n• 🏦 ICBC — Most ATMs nationwide\n• 🏦 CCB — Great mobile app\n• 🏦 ABC — Common on campuses\n\n**Process:** Visit branch → fill forms → get debit card same day → download mobile app → bind to WeChat/Alipay\n\n💡 Bring a Chinese-speaking friend to help!",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['remittance', 'send money', 'transfer money', 'cheap', 'cheapest']):
        return {
            "reply": "💸 **Best Ways to Send Money to China:**\n\n1️⃣ **Wise** — Best exchange rate ✅\n• Fee: ~$4-5 for $500\n• Speed: 1-2 hours\n• Mid-market rate, no markup\n\n2️⃣ **Remitly** — Fastest\n• Fee: $3.99 flat\n• Speed: Minutes (express)\n• Good first-time promotions\n\n3️⃣ **Alipay International** — Instant in China\n• Fee: $1.99\n• Speed: Instant\n• Needs Alipay account\n\n4️⃣ **Western Union** — Cash pickup\n• Fee: $5-8\n• 500K+ agent locations\n\n5️⃣ **Bank SWIFT** — For tuition ✅\n• Fee: $25-40\n• Speed: 3-5 business days\n• Official receipt for university\n\n💡 Use the Remittance Compare tool for live comparison!",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['budget', 'monthly', 'expense', 'cost of living', 'living cost']):
        return {
            "reply": "📊 **Monthly Budget for Student in China:**\n\n| Category | Range |\n|---|---|\n| 🏠 Rent (dorm) | ¥800–1,200 |\n| 🏠 Rent (off-campus) | ¥1,500–3,000 |\n| 🍜 Food & Dining | ¥1,000–1,500 |\n| 🚌 Transport | ¥200–400 |\n| 📱 Phone/Internet | ¥100–200 |\n| 📚 Study Materials | ¥200–400 |\n| 🎮 Entertainment | ¥300–500 |\n\n**Total: ¥2,600–5,200/month (~$360–720 USD)**\n\n💡 Tips:\n• Campus canteen: ¥15-25/meal (cheapest)\n• Cook at home: save 30-40% on food\n• Student metro card: 50% discount in most cities",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['exchange rate', 'bdt', 'cny', 'dollar', 'rate', 'convert']):
        return {
            "reply": "💱 **Current Exchange Rates (approximate):**\n\n| Pair | Rate |\n|---|---|\n| 🇧🇩 1 BDT | = 0.0597 CNY |\n| 🇺🇸 1 USD | = 7.245 CNY |\n| 🇺🇸 1 USD | = 121.45 BDT |\n| 🇨🇳 1 CNY | = 16.76 BDT |\n| 🇬🇧 1 GBP | = 9.18 CNY |\n| 🇪🇺 1 EUR | = 7.92 CNY |\n\n💡 Use the Currency Converter tool for instant calculations!\n\n⚠️ Rates fluctuate — always check before making large transfers.",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['tuition', 'payment method', 'university fee', 'pay tuition']):
        return {
            "reply": "🎓 **Tuition Payment Methods for Chinese Universities:**\n\n1️⃣ **SWIFT Bank Wire** ✅ Most Common\n• University provides: bank name, SWIFT code, account #\n• Fee: $25-40\n• Time: 3-5 business days\n• Use admission letter reference number\n\n2️⃣ **Flywire** ✅ Recommended\n• Tracks payment end-to-end\n• Locks exchange rate\n• Partners with 100+ Chinese universities\n\n3️⃣ **WeChat Pay / Alipay**\n• After arrival, needs Chinese bank account\n• Some unis accept mobile payment\n\n4️⃣ **Cash at Registration**\n• Some accept CNY cash during enrollment week\n• Not recommended for large amounts\n\n⚠️ Always confirm with your university's finance office before sending!",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['visa', 'mastercard', 'card', 'unionpay', 'credit card']):
        return {
            "reply": "💳 **Using Cards in China:**\n\n**Visa/Mastercard:**\n• Limited acceptance — mainly hotels, airports, big chains\n• Most small shops do NOT accept\n• Can link to Alipay (Tour Pass) for wider use\n• WeChat Pay also allows foreign card binding\n• ATM withdrawal: $3-5 fee per transaction\n\n**UnionPay:**\n• China's national card network\n• Works at ALL ATMs and POS terminals\n• Cloud QuickPass for NFC contactless\n• Can bind to WeChat/Alipay\n• International cards accepted in 180+ countries\n\n💡 **Tip:** Get a Chinese bank card (UnionPay) within your first week — it makes everything easier!",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['digital yuan', 'e-cny', 'dcep', 'cbdc']):
        return {
            "reply": "📱 **Digital Yuan (e-CNY):**\n\n• China's Central Bank Digital Currency (CBDC)\n• Piloted in: Shenzhen, Shanghai, Beijing, Chengdu, Suzhou\n• No bank account needed for basic use\n• Zero transaction fees\n• Available through major Chinese bank apps\n• Government subsidies sometimes distributed via e-CNY\n• Growing merchant acceptance at universities\n\n💡 Check if your university city is a pilot city — you might get a ¥200 welcome bonus!",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['scholarship', 'csc', 'stipend', 'financial aid']):
        return {
            "reply": "🎓 **Scholarships for Studying in China:**\n\n**CSC (China Scholarship Council):**\n• Full tuition + accommodation + stipend\n• Stipend: ¥3,000-3,500/month (Master's)\n• Apply through your country's education ministry\n\n**University Scholarships:**\n• Partial to full tuition waiver\n• Apply directly to university\n• Based on academics + HSK score\n\n**Provincial/City Scholarships:**\n• Zhejiang, Shanghai, Beijing have their own\n• Usually cover tuition only\n\n💡 Tips:\n• HSK 4-5 significantly improves chances\n• Apply 6-12 months before intake\n• Strong recommendation letters are key",
            "tool_used": None, "mode": "smart"
        }

    if any(w in q for w in ['hello', 'hi ', 'hey', 'help', 'what can you']):
        return {
            "reply": "Hello! 👋 I'm **FinBridge AI**, your student finance assistant!\n\nI can help you with:\n• 💱 Currency conversion & exchange rates\n• 💸 Money transfer / remittance comparison\n• 📊 Budget planning for studying abroad\n• 📱 Alipay, WeChat Pay & mobile payments\n• 🏦 Chinese bank accounts & UnionPay\n• 🎓 Tuition payment methods\n• 💳 Card usage in China\n• 🎓 Scholarship information\n\nJust ask me anything! For example:\n*\"How do I set up Alipay?\"*\n*\"Cheapest way to send money to China?\"*",
            "tool_used": None, "mode": "smart"
        }

    # No match — return None so we try OpenAI
    return None


class FinBridgeAgent:
    def __init__(self):
        self.history = []

    async def process(self, user_message: str) -> dict:
        """Dual mode: Smart replies first, OpenAI for everything else"""

        # Step 1: Try smart reply (always works)
        smart = smart_reply(user_message)
        if smart:
            return smart

        # Step 2: Try OpenAI (needs API key)
        if HAS_KEY and client:
            try:
                self.history.append({"role": "user", "content": user_message})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *self.history[-10:]
                    ],
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=800
                )

                msg = response.choices[0].message

                if msg.tool_calls:
                    tool = msg.tool_calls[0]
                    args = json.loads(tool.function.arguments)
                    result = self._run_tool(tool.function.name, args)

                    self.history.append(msg.model_dump())
                    self.history.append({
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "content": json.dumps(result)
                    })

                    final = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *self.history[-12:]
                        ],
                        temperature=0.7, max_tokens=800
                    )
                    reply = final.choices[0].message.content
                else:
                    reply = msg.content

                self.history.append({"role": "assistant", "content": reply})
                return {"reply": reply, "tool_used": None, "mode": "openai"}

            except Exception as e:
                print(f"OpenAI error: {e}")
                # Fall through to fallback

        # Step 3: Fallback generic reply
        return {
            "reply": "I'm FinBridge, your student finance assistant! I can help with:\n\n• 💱 Currency conversion\n• 💸 Money transfers\n• 📊 Budget planning\n• 📱 Alipay & WeChat Pay\n• 🏦 Chinese banking\n• 🎓 Tuition payments\n\nTry asking about a specific topic!\n\n*Note: For general questions beyond finance, connect an OpenAI API key for full AI capability.*",
            "tool_used": None, "mode": "fallback"
        }

    def _run_tool(self, name, args):
        from tools import CurrencyTool, RemittanceTool
        if name == "convert_currency":
            import asyncio
            return asyncio.get_event_loop().run_until_complete(
                CurrencyTool().convert(args["from_currency"], args["to_currency"], args["amount"])
            )
        elif name == "compare_remittance":
            import asyncio
            return asyncio.get_event_loop().run_until_complete(
                RemittanceTool().compare(args["from_country"], args["to_country"], args["amount_usd"])
            )
        return {"error": "Unknown tool"}
