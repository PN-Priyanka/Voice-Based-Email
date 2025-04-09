from flask import Flask, render_template, request,  jsonify, session
import sqlite3
import speech_recognition as sr
r = sr.Recognizer()

import pygame
import time
from gtts import gTTS
from mutagen.mp3 import MP3

import speech_recognition as sr
import sounddevice as sd
import wave
import numpy as np
import threading

from caption import get_recent_email

import smtplib
from email.message import EmailMessage

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

cursor.execute('create table if not exists user(Name TEXT, Phone TEXT, Email TEXT, password TEXT, Type TEXT)')

def text_to_speech(text1):
    print(text1)
    myobj = gTTS(text=text1, lang='en-us', tld='com', slow=False)
    myobj.save("voice.mp3")
    song = MP3("voice.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load('voice.mp3')
    pygame.mixer.music.play()
    time.sleep(song.info.length)
    pygame.quit()
    time.sleep(2)

def voice_to_text(data):
    while True:	
        duration = 10
        fs = 44100
        channels=2
        filename="input_audio.wav"
        text_to_speech('say '+data)
        print("Recording...")
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype=np.int16)
        sd.wait()
        print("Recording complete.")

        # Save the recorded audio to a WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(filename) as source:
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
            
                text = recognizer.recognize_google(audio_data)
                text = text.lower()
                print(text)
                if text:
                    break 
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    return text

app = Flask(__name__)
app.secret_key = '\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'

@app.route('/compose', methods=['GET', 'POST'])
def compose():
    if request.method == 'POST':
        name = request.form['email']

        emails = {'pooja' : 'poojat0207@gmail.com',
                'jyothika' : 'jyothikareddy151@gmail.com',
                'meghana' : 'meghanaas24@gmail.com'}

        email = emails[name]
        subject = request.form['subject']
        message = request.form['message']
        print(email, subject, message)
        
        msg = EmailMessage()
        msg.set_content(message)
        msg['From'] = session['from']
        msg['To'] = [email]
        msg['Subject'] = subject

        myobj = gTTS(text=message, lang='en-us', tld='com', slow=False)
        myobj.save("voicenote.mp3")

        with open('voicenote.mp3', 'rb') as file:
            file_data = file.read()
            msg.add_attachment(file_data, maintype='audio', subtype='mpeg', filename='voicenote.mp3')

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(session['from'], session['password'])
        server.send_message(msg)
        server.quit()

        text_to_speech('email sent successfully')
        text_to_speech('click anywhere to start')

        return render_template('userlog.html')
    return render_template('userlog.html')

@app.route('/')
def index():
    text_to_speech("Click anywhere to start")
    return render_template("index.html")

@app.route('/logout')
def logout():
    text_to_speech("Click anywhere to start")
    return render_template("index.html")

@app.route('/home')
def home():
    text_to_speech("Click anywhere to start")
    return render_template("userlog.html")

@app.route('/Inbox')
def Inbox():
    from Emails import get_recent_email
    rows = get_recent_email()
    return render_template("emails.html", rows=rows)

@app.route('/adduser',  methods=['POST','GET'])
def adduser():
    if request.method == 'POST':
        Name = request.form['name']
        Phone = request.form['phone']
        Email = request.form['email']
        password = request.form['password']
        Type = 'blind'

        print(Name, Phone, Email, password, Type)

        msg = ['User details Saved for',
            'Name : ' + Name,
            'Phone : ' + Phone,
            'Email : ' + Email,
            'Password : ' + password,
            'Type : ' + Type]

        row = [Name, Phone, Email, password, Type]

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute('insert into user values(?,?,?,?,?)', row)
        connection.commit()

        return render_template("adduser.html", msg=msg)
    return render_template("adduser.html")
                
@app.route('/signin',  methods=['POST','GET'])
def signin():
    if request.method == 'POST':
        Name = request.form['name']
        password = request.form['password']
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute("select * from user where name = '"+Name+"' and password = '"+password+"'")
        result = cursor.fetchone()

        if result:
            result = list(result)
            session['name'] = Name
            session['Type'] = result[-1]
            text_to_speech('logged in successfully')
            session['from'] = 'jyothika.cse.rymec@gmail.com'
            session['password'] = 'nwky vicw mbca qbps'
            # text_to_speech('checking for last email')
            # get_recent_email()
            text_to_speech('click anywhere to start')
            return render_template("userlog.html", msg="WELCOME")
        text_to_speech("you said wrong username or password")
        return render_template("index.html")
    text_to_speech("Click anywhere to start")
    return render_template("index.html")

@app.route("/getename")
def getename():
    text = voice_to_text('your name')
    global dd
    def email_format(sentence):
        sentence = sentence.replace(' ', '')
        return sentence
    def confirmation(text):
        global dd
        print('you said '+text)
        text_to_speech('you said '+text)
        text1 = voice_to_text('say continue to confirm or say again')
        if text1 == 'continue':
            dd = text
            return text
        else:
            text1 = email_format(text1)
            confirmation(text1)
    text = email_format(text)
    resp = confirmation(text)
    print('your name is ',dd)
    return jsonify(dd)

@app.route("/getpassword")
def getpassword():
    text = voice_to_text('password')
    def confirmation(text):
        global ddd
        print('you said '+text)
        text_to_speech('you said '+text)
        text1 = voice_to_text(' continue to confirm or say again')
        if text1 == 'continue':
            ddd = text
            return text
        else:
            confirmation(text1)
    resp = confirmation(text)
    print('password is ',ddd)
    return jsonify(ddd)

@app.route("/getconfirm")
def getconfirm():
    while True:
        text = voice_to_text('continue')
        if 'continue' in text:
            break
    return jsonify(text)

@app.route("/gettoemail")
def gettoemail():
    text = voice_to_text('to recipient name')
    def confirmation(text):
        print('you said '+text)
        text_to_speech('you said '+text)
        text1 = voice_to_text(' yes to continue or say again')
        if text1 == 'continue':
            return text
        else:
            confirmation(text1)
    resp = confirmation(text)

    print('to recipient name is ',resp)
    return jsonify(resp)

@app.route("/getsubject")
def getsubject():
    text = voice_to_text('subject')
    def confirmation(text):
        print('you said '+text)
        text_to_speech('you said '+text)
        text1 = voice_to_text(' continue to confirm or say again')
        if text1 == 'continue':
            return text
        else:
            confirmation(text1)
    resp = confirmation(text)
    print('subject is ',resp)
    return jsonify(resp)

@app.route("/getmessage")
def getmessage():
    text = voice_to_text('message')
    def confirmation(text):
        print('you said '+text)
        text_to_speech('you said '+text)
        text1 = voice_to_text(' continue to confirm or say again')
        if text1 == 'continue':
            return text
        else:
            confirmation(text1)
    resp = confirmation(text)
    print('message is ',resp)
    return jsonify(resp)

@app.route("/getconfirmation")
def getconfirmation():
    while True:
        text = voice_to_text('continue')
        if 'continue' in text:
            break
    return jsonify(text)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
