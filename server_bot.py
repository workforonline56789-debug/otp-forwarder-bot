import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import threading
import os
from flask import Flask

# =========================================================
# ⚙️ শুধুমাত্র নিচের ৪টি তথ্য আপনার অ্যাকাউন্ট অনুযায়ী এডিট করুন
# =========================================================
BOT_TOKEN = '8870112454:AAE5BMAuUqzj7T7Haw5F7U62NNrWQX6VLHQ'
GROUP_CHAT_ID = -1004475062727         # ওটিপি যে গ্রুপে যাবে (অবশ্যই -100 সহ)
PANEL_API_KEY = '35acbab6f40ed83432698af5eaa197e3c113f6cd'
YOUR_ADMIN_ID = 8243861643             # আপনার নিজের পার্সোনাল টেলিগ্রাম আইডি
# =========================================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
PANEL_URL = "https://axnumberserver.shop/number/api"

# হোস্টিং হেলথ চেক
@app.route('/')
def home():
    return "AX Number Server Bot is Online!", 200

# 📱 বটের নিচের মেইন কিপ্যাড বাটনসমূহ
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📱 GET NUMBER"))
    markup.row(KeyboardButton("🔍 SEARCH OTP"), KeyboardButton("🔑 GET 2FA"))
    markup.row(KeyboardButton("🎁 REFER AND EARN"), KeyboardButton("👤 PROFILE"))
    markup.row(KeyboardButton("🏆 LEADERBOARD"))
    markup.row(KeyboardButton("🎧 SUPPORT"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "👋 **FAST SMS BOT**-এ আপনাকে स्वागतম!\n\nলাইভ নম্বর নিতে নিচের বাটনটি ব্যবহার করুন।", reply_markup=main_menu())

# 🔄 আপনার প্যানেল (axnumberserver.shop) থেকে ওটিপি চেক করার লাইভ লুপ
def fetch_live_otp(chat_id, order_id, phone_number, app_name, status_message_id):
    # ৫ মিনিট পর্যন্ত প্রতি ৫ সেকেন্ড পর পর আপনার প্যানেলে ওটিপি চেক করবে
    for _ in range(60): 
        time.sleep(5) 
        
        # প্যানেলের ওটিপি চেক করার অফিশিয়াল রিকোয়েস্ট ইউআরএল
        check_url = f"{PANEL_URL}/get_otp"
        params = {'api_key': PANEL_API_KEY, 'order_id': order_id}
        
        try:
            response = requests.get(check_url, params=params).json()
            
            # প্যানেল ওটিপি কোড পাঠালে (ধরে নিচ্ছি রেসপন্সে 'otp' বা 'sms' থাকবে)
            if response.get('status') == 'success' or response.get('otp'):
                otp_code = response.get('otp') or response.get('code')
                
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
                
                # বটের ইনবক্সে আপডেট পাঠানো
                bot.edit_message_text(msg_text, chat_id, status_message_id, parse_mode='HTML', reply_markup=inline_markup)
                # আপনার টেলিগ্রাম গ্রুপে লাইভ ফরোয়ার্ড করা
                bot.send_message(GROUP_CHAT_ID, msg_text, parse_mode='HTML', reply_markup=inline_markup)
                return
                
            elif response.get('status') == 'canceled':
                bot.edit_message_text("❌ নম্বরটি প্যানেল থেকে বাতিল করা হয়েছে।", chat_id, status_message_id)
                return
        except Exception as e:
            print(f"OTP Pull Error: {e}")
            
    bot.edit_message_text("⏱️ ওটিপি আসার নির্ধারিত সময় শেষ। দয়া করে নতুন নম্বর ট্রাই করুন।", chat_id, status_message_id)

# 📱 GET NUMBER বাটনে ক্লিক করলে আপনার প্যানেল থেকে লাইভ নম্বর কেনা
@bot.message_handler(func=lambda message: message.text == "📱 GET NUMBER")
def buy_number_from_panel(message):
    sent_msg = bot.send_message(message.chat.id, "⏳ আপনার প্যানেল থেকে লাইভ নম্বর নেওয়া হচ্ছে, অপেক্ষা করুন...")
    
    # আপনার প্যানেল থেকে নম্বর অর্ডার করার এপিআই রিকোয়েস্ট (ডিফল্ট: Facebook ও Cameroon সেট করা)
    order_url = f"{PANEL_URL}/get_number"
    params = {
        'api_key': PANEL_API_KEY,
        'service': 'facebook',
        'country': 'cameroon'
    }
    
    try:
        response = requests.get(order_url, params=params).json()
        
        # প্যানেল সফলভাবে নম্বর দিলে (ধরে নিচ্ছি রেসপন্সে order_id এবং phone থাকবে)
        if response.get('status') == 'success' or response.get('phone'):
            order_id = response.get('order_id') or response.get('id')
            phone_number = response.get('phone') or response.get('number')
            
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
            
            # ব্যাকগ্রাউন্ড লুপে ওটিপি রিড করা চালু করা
            threading.Thread(target=fetch_live_otp, args=(message.chat.id, order_id, phone_number, "facebook", sent_msg.message_id)).start()
        else:
            bot.edit_message_text(f"❌ প্যানেলে নম্বর বা ব্যালেন্স নেই। বার্তা: {response.get('message', 'Error')}", message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ প্যানেল সার্ভার কানেকশন এরর: {str(e)}", message.chat.id, sent_msg.message_id)

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    threading.Thread(target=run_web_server).start()
    print("🚀 AX Number Server Bot is Polling...")
    bot.infinity_polling()
