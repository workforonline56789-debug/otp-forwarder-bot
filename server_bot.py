import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import threading
import os
from flask import Flask, request, jsonify

# =========================================================
# ⚙️ শুধুমাত্র নিচের ৪টি তথ্য আপনার অ্যাকাউন্ট অনুযায়ী এডিট করুন
# =========================================================
BOT_TOKEN = '8870112454:AAE5BMAuUqzj7T7Haw5F7U62NNrWQX6VLHQ'
GROUP_CHAT_ID = -1004475062727         # ওটিপি যে গ্রুপে যাবে (অবশ্যই -100 সহ)
PANEL_API_KEY = '35acbab6f40ed83432698af5eaa197e3c113f6cd'
YOUR_ADMIN_ID = 8243861643              # আপনার নিজের পার্সোনাল টেলিগ্রাম আইডি
# =========================================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
PANEL_URL = "https://axnumberserver.shop"

# হোস্টিং সার্ভার সচল রাখার রুট
@app.route('/')
def home():
    return "AX Number Server Live Bot is Running!", 200

# 📱 বটের নিচের মেইন কিপ্যাড বাটনসমূহ (হুবহু স্ক্রিনশটের মতো)
def main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📱 GET NUMBER"))
    markup.row(KeyboardButton("🔍 SEARCH OTP"))
    markup.row(KeyboardButton("🔑 GET 2FA"), KeyboardButton("💰 BALANCE"))
    markup.row(KeyboardButton("🎁 REFER AND EARN"), KeyboardButton("👤 PROFILE"))
    markup.row(KeyboardButton("🏆 LEADERBOARD"))
    markup.row(KeyboardButton("🎧 SUPPORT"))
    
    # আপনি এডমিন হলে আপনার জন্য অতিরিক্ত ADMIN PANEL বাটন শো করবে
    if str(user_id) == str(YOUR_ADMIN_ID):
        markup.row(KeyboardButton("⚙️ ADMIN PANEL"))
        
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(
        message.chat.id, 
        "👋 **AS NUMBER PANEL BOT**-এ আপনাকে স্বাগতম!\n\nলাইভ নম্বর নিতে নিচের বাটনটি ব্যবহার করুন।", 
        reply_markup=main_menu(message.chat.id)
    )

# ⚙️ ADMIN PANEL বাটনে ক্লিক করলে এডমিন প্যানেল মেসেজ
@bot.message_handler(func=lambda message: message.text == "⚙️ ADMIN PANEL")
def admin_panel_cmd(message):
    if str(message.chat.id) == str(YOUR_ADMIN_ID):
        bot.send_message(message.chat.id, "⚙️ **Welcome to Admin Control Unit!**\n\nএখানে আপনি বটের সার্বিক তথ্য দেখতে পাবেন।")
    else:
        bot.send_message(message.chat.id, "❌ আপনি এই বটের এডমিন নন।")

# 🔄 প্যানেল থেকে রিয়েল-টাইম ওটিপি চেক করার লুপ
def fetch_live_otp(chat_id, order_id, phone_number, app_name, status_message_id):
    for _ in range(60): 
        time.sleep(5) 
        check_url = f"{PANEL_URL}/get_otp"
        params = {'api_key': PANEL_API_KEY, 'order_id': order_id}
        
        try:
            response = requests.get(check_url, params=params)
            try:
                res_data = response.json()
            except:
                res_data = {"status": "error", "otp": response.text}
            
            # ওটিপি কোড প্যানেলে আসলে তা রিসিভ করার লজিক
            if res_data.get('status') == 'success' or res_data.get('otp') or len(str(res_data.get('otp', ''))) > 2:
                otp_code = res_data.get('otp') or res_data.get('code') or response.text
                
                # ওটিপি যদি পেন্ডিং থাকে তবে অপেক্ষা বজায় রাখবে
                if "waiting" in str(otp_code).lower() or "pending" in str(otp_code).lower():
                    continue
                
                # হুবহু স্ক্রিনশটের লেআউটের মতো মেসেজ ফরম্যাট
                msg_text = (
                    f"📱 <b>Service:</b> {app_name} ❞\n"
                    f"🌐 <b>Country:</b> Cameroon 🇨🇲 ❞\n\n"
                    f"📞 <code>{phone_number}</code> ❞\n"
                    f"🔑 <b>OTP:</b> <code>{otp_code}</code>\n"
                    f"💰 <b>AVAILABLE WITHDRAW:</b> 0.40 BDT\n"
                    f"📊 <b>MIN 55.00 BDT</b> — need 54.60 BDT more"
                )
                
                inline_markup = InlineKeyboardMarkup()
                inline_markup.row(InlineKeyboardButton(text=f"📋 {phone_number}", callback_data="copy_num"))
                inline_markup.row(InlineKeyboardButton(text=f"📋 🔑 {otp_code}", callback_data="copy_otp"))
                inline_markup.row(InlineKeyboardButton(text="Change Number", callback_data="change_num"),
                                  InlineKeyboardButton(text="Change Country", callback_data="change_country"))
                inline_markup.row(InlineKeyboardButton(text="OTP View / OTP Group ↗️", url="https://t.me/onlyotpchannel"))
                
                # বটের ইনবক্সে মেসেজ আপডেট করা
                bot.edit_message_text(msg_text, chat_id, status_message_id, parse_mode='HTML', reply_markup=inline_markup)
                # একই সাথে ওটিপি গ্রুপে অটোমেটিক রিয়েল-টাইমে ফরোয়ার্ড করা
                bot.send_message(GROUP_CHAT_ID, msg_text, parse_mode='HTML', reply_markup=inline_markup)
                return
        except:
            pass
            
    bot.edit_message_text("⏱️ ওটিপি আসার নির্ধারিত সময় শেষ। দয়া করে নতুন নম্বর ট্রাই করুন।", chat_id, status_message_id)

# 📱 GET NUMBER বাটনে ক্লিক করলে আপনার প্যানেল থেকে লাইভ নম্বর কেনা
@bot.message_handler(func=lambda message: message.text == "📱 GET NUMBER")
def buy_number_from_panel(message):
    sent_msg = bot.send_message(message.chat.id, "⏳ আপনার প্যানেল থেকে লাইভ নম্বর নেওয়া হচ্ছে, অপেক্ষা করুন...")
    
    order_url = f"{PANEL_URL}/get_number"
    params = {
        'api_key': PANEL_API_KEY,
        'service': 'facebook',
        'country': 'cameroon'
    }
    
    try:
        response = requests.get(order_url, params=params)
        try:
            res_data = response.json()
        except:
            res_data = {"status": "success", "phone": response.text.strip(), "order_id": str(int(time.time()))}
        
        if res_data.get('phone') and len(res_data.get('phone')) > 5:
            order_id = res_data.get('order_id') or res_data.get('id') or "12345"
            phone_number = res_data.get('phone') or res_data.get('number')
            
            # প্রাথমিক মেসেজ (ওটিপির জন্য অপেক্ষা করছে)
            msg_text = (
                f"📱 <b>Service:</b> facebook ❞\n"
                f"🌐 <b>Country:</b> Cameroon 🇨🇲 ❞\n\n"
                f"📞 <code>{phone_number}</code> ❞\n"
                f"⏳ <b>OTP:</b> Waiting for SMS...\n"
                f"💰 <b>AVAILABLE WITHDRAW:</b> 0.40 BDT"
            )
            
            inline_markup = InlineKeyboardMarkup()
            inline_markup.row(InlineKeyboardButton(text=f"📋 {phone_number}", callback_data="copy_num"))
            inline_markup.row(InlineKeyboardButton(text="Change Number", callback_data="change_num"),
                              InlineKeyboardButton(text="Change Country", callback_data="change_country"))
            inline_markup.row(InlineKeyboardButton(text="OTP View / OTP Group ↗️", url="https://t.me"))
            
            bot.edit_message_text(msg_text, message.chat.id, sent_msg.message_id, parse_mode='HTML', reply_markup=inline_markup)
            
            # ওটিপি ট্র্যাকিংয়ের জন্য ব্যাকগ্রাউন্ড থ্রেড চালু করা
            threading.Thread(target=fetch_live_otp, args=(message.chat.id, order_id, phone_number, "facebook", sent_msg.message_id)).start()
        else:
            bot.edit_message_text(f"❌ প্যানেলে নম্বর নেই বা টোকেন ভুল। প্যানেল রেসপন্স: {response.text}", message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ কানেকশন এরর। সার্ভার রেসপন্স চেক করুন।", message.chat.id, sent_msg.message_id)

def run_web_server():
    # হোস্টিংয়ের পোর্ট অনুযায়ী অটোমেটিক রান হবে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    threading.Thread(target=run_web_server).start()
    bot.infinity_polling()
