import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, jsonify
import threading
import os

# =========================================================
# ⚙️ শুধুমাত্র নিচের ৪টি তথ্য আপনার বট ও গ্রুপ অনুযায়ী এডিট করুন
# =========================================================
BOT_TOKEN = '8870112454:AAE5BMAuUqzj7T7Haw5F7U62NNrWQX6VLHQ'
PANEL_SECRET_TOKEN = '35acbab6f40ed83432698af5eaa197e3c113f6cd'
GROUP_CHAT_ID = -1004475062727         # আপনার গ্রুপের আইডি (অবশ্যই -100 সহ)
YOUR_ADMIN_ID = 8243861643             # আপনার নিজের পার্সোনাল টেলিগ্রাম আইডি
# =========================================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# হেলথ চেক রুট (Render সার্ভার সচল রাখার জন্য এটি প্রয়োজন)
@app.route('/')
def home():
    return "OTP Forwarder Server is Online!", 200

# প্যানেল থেকে রিয়েল-টাইম ওটিপি রিসিভ করার এন্ডপয়েন্ট
@app.route('/receive_otp', methods=['POST', 'GET'])
def receive_otp():
    # সিকিউরিটি চেক
    auth_token = request.headers.get('Authorization') or request.args.get('panel_token')
    if auth_token != PANEL_SECRET_TOKEN:
        return jsonify({"status": "error", "message": "Unauthorized Panel Token"}), 401
    
    # প্যানেল GET বা POST যে মেথডেই ডেটা পাঠাক তা রিসিভ করার লজিক
    if request.method == 'POST':
        data = request.json or request.form or {}
    else:
        data = request.args or {}
        
    country = data.get('country', 'Cameroon')
    phone_number = data.get('phone', 'No Number')
    app_name = data.get('app', 'Facebook')
    otp_code = data.get('otp', 'Waiting...')
    price = data.get('price', '0.4 tk')
    group_url = data.get('group_url', 'https://t.me') 

    # স্টাইলিশ মেসেজ লেআউট
    msg_text = (
        f"🌐 <b>{country}</b> | 💬 <code>{phone_number}</code>\n"
        f"<b>{app_name}</b>\n\n"
        f"💚 <b>OTP Code:</b> <code>{otp_code}</code>\n\n"
        f"💰 <i>Added {price}</i>"
    )

    # ইনলাইন কিপ্যাড বাটন
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text=f"📋 Copy Number", callback_data=f"copy_num_{phone_number}"))
    markup.row(InlineKeyboardButton(text=f"📋 Copy OTP", callback_data=f"copy_otp_{otp_code}"))
    markup.row(InlineKeyboardButton(text="OTP Group ↗️", url=group_url))

    try:
        # ইনবক্স ও গ্রুপে রিয়েল-টাইমে পাঠানো
        bot.send_message(YOUR_ADMIN_ID, msg_text, parse_mode='HTML', reply_markup=markup)
        bot.send_message(GROUP_CHAT_ID, msg_text, parse_mode='HTML', reply_markup=markup)
        return jsonify({"status": "success", "message": "OTP forwarded successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_server():
    # Render অটোমেটিক পোর্ট অ্যাসাইন করবে, না পেলে ডিফল্ট ১০০০০ পোর্ট নেবে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
    print("🚀 OTP Forwarder Server is Starting...")
    bot.infinity_polling()
