from urllib import request
import webbrowser as wb
import eel
import windowsapps
import subprocess
import platform
import datetime
import random
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import pyqrcode
import getpass
from pytube import YouTube
import psutil

greetings = ['Hi','Hello','Nice to see you']
thanks = ['My pleasure','Any time!','Happy to help']


def size_utility(size, initials="B"):
    factor = 1024
    for memory_unit in ["", "k", "M", "G", "T", "P"]:
        if size < factor:
            return (f"{size:.2f}{memory_unit}{initials}")
        size /= factor

def wifi():
    data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
    show = "Your saved passwords are shown below: <br>"
    for i in profiles:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split('\n')
        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
        try: show = show+"{:<30} | {:<}".format(i,results[0]) + "<br>"
        except IndexError: show = show+"{:<30} | {:<}".format(i,"")+"<br>"
    return show

def open(app):
    app = app.replace("open","")
    app = app[1:]
    try:
        windowsapps.open_app(app)
        show = "Opened "+app
        return show

    except FileNotFoundError:
        try:
            request.urlopen("www.google.com")
            wb.open(app)
            show = "Opened " + app
            return show
        except Exception:
            show = "Sorry, I couln't open that"
            return show

def sysinfo():
    system = platform.uname()
    memory = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    show = f"Your system information is shown below <br> System: {system.system} <br> PC Name: {system.node} <br> Release: {system.release} <br> Version: {system.version} <br> Processor type: {system.machine} <br> Processor: {system.processor} <br> Total Ram: {size_utility(memory.total)} <br> Current User: {getpass.getuser()} <br> Battery-percent: {battery.percent}"
    return show

def scan_qr_code():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray_img = cv2.cvtColor(frame, 0)
        barcode = decode(gray_img)

        for obj in barcode:
            points = obj.polygon
            (x, y, w, h) = obj.rect
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

            barcodeData = obj.data.decode("utf-8")
            string = "Data: " + str(barcodeData)

            cv2.putText(frame, string, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow('Scan qr code', frame)
        code = cv2.waitKey(1)
        if code == 27 or code == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def read_qr_code():
    path = str(eel.("Data to be inserted")())
    qr = decode(Image.open(path))
    data = ""
    for obj in qr:
        data = data+str(obj.data)
        data = data[1:]
    return "Data: "+data

def generate_qr_code():
    name = str(eel.dialog('Name to save your qr-code as')())
    if name == 'none' or name == '':
        return "Couldn't create qrcode"
    data = str(content)
    data = data.replace("create qr code ", "")
    qr = pyqrcode.create(data)
    path = "C:\\Users\\" + getpass.getuser()+ "\\Downloads\\" + name + '.png'
    qr.png(path, scale=10)
    return "Successfully created qr code<br>Check the downloads for qr-code image"

def youtube():
    try:
        request.urlopen('https://www.google.com')
        link = str(eel.dialog("Enter the url")())
        if link == 'none' or link == '':
            return "Couldn't download"
        yt = YouTube(link)
        ys = yt.streams.get_highest_resolution()
        eel.respond("Downloading...")
        ys.download(output_path="C:\\Users\\" + getpass.getuser()+ "\\Downloads\\")
        return "Download complete<br>Check downloads folder for your file"
    except Exception: return "Unable to download<br>Please check your network connection and try again"

@eel.expose
def chat(data):
    msg = str(data)
    msg = msg.lower()
    if msg == 'hi' or msg == 'hi there' or msg == 'hello' or msg == 'hello there' or msg == 'hey':
       return random.choice(greetings)
    elif msg == "bye" or msg == "good bye":
        return "Bye"
    elif msg == "thanks" or msg == "that's helpfull" or msg == "thank you":
        return random.choice(thanks)
    elif msg == "wifipassword":
        reply = wifi()
        return reply
    elif msg == "sysinfo" or msg == "systeminfo" or msg == "systeminformation":
        reply = sysinfo()
        return reply
    elif 'open' in msg:
        reply = open(msg)
        return reply
    elif 'date and time' in msg:
        reply = f"Date: {datetime.datetime.now().day}-{datetime.datetime.now().month}-{datetime.datetime.now().year}<br>Time: {datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}"
        return reply
    elif 'date' in msg:
        reply = f"Date: {datetime.datetime.now().day}-{datetime.datetime.now().month}-{datetime.datetime.now().year}"
        return reply
    elif 'time' in msg:
        reply = f"Time: {datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}"
        return reply
    elif msg == "scan qr code":
        scan_qr_code()
        return 'Scan your qr code'
    elif 'read qr code' in msg:
        reply = read_qr_code(msg)
        return reply
    elif 'create qr code' in msg:
        reply = generate_qr_code(msg)
        return reply
    elif "what is " in msg or 'who is ' in msg or 'search ' in msg:
        try:
            request.urlopen('https://www.google.com')
            wb.open(msg)
            return "Refer the browser"
        except Exception: return "Please check your network connection and try again"
    elif "youtube download" in msg:
        reply = youtube()
        return reply
    else: return "I didn't get that"

eel.init('web')
eel.start('index.html')
