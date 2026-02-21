import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import speech_recognition as sr
import pyttsx3
import datetime
import json
import os
import random
import re
import requests
import google.generativeai as genai
import threading
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image
import pyzbar.pyzbar as pyzbar
import base64
import io
import wave
import pyaudio

# KivyMD importları
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.chip import MDChip
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.theming import ThemableBehavior

# KV Language
Builder.load_string('''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<ChatMessage@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: '10dp'
    margin: '5dp'
    md_bg_color: get_color_from_hex('#2e2e2e') if root.is_user else get_color_from_hex('#9400d3')
    radius: [15, 15, 15, 15]
    
    MDLabel:
        text: root.message
        color: 1, 1, 1, 1
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        markup: True
        font_style: 'Body1'
        
    MDLabel:
        text: root.timestamp
        color: 0.8, 0.8, 0.8, 1
        size_hint_y: None
        height: self.texture_size[1]
        font_size: '12sp'
        halign: 'right'

<StartupScreen@MDBoxLayout>:
    orientation: 'vertical'
    padding: '20dp'
    spacing: '20dp'
    md_bg_color: get_color_from_hex('#1a1a1a')
    
    MDBoxLayout:
        orientation: 'vertical'
        adaptive_height: True
        pos_hint: {'center_x': 0.5, 'center_y': 0.6}
        
        MDLabel:
            text: '✨'
            font_size: '80sp'
            halign: 'center'
            color: get_color_from_hex('#9400d3')
            
        MDLabel:
            text: 'NOVA AI'
            font_size: '32sp'
            halign: 'center'
            color: get_color_from_hex('#9400d3')
            font_style: 'H4'
            bold: True
            
        MDLabel:
            text: 'Kişisel Yapay Zeka Asistanınız'
            font_size: '16sp'
            halign: 'center'
            color: 0.8, 0.8, 0.8, 1
            font_style: 'Body1'
    
    MDBoxLayout:
        orientation: 'vertical'
        adaptive_height: True
        pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        spacing: '10dp'
        
        MDRaisedButton:
            text: 'Yazılı İletişim'
            md_bg_color: get_color_from_hex('#9400d3')
            on_press: root.set_mode('text')
            
        MDRaisedButton:
            text: 'Sesli İletişim'
            md_bg_color: get_color_from_hex('#9400d3')
            on_press: root.set_mode('voice')
            
        MDRaisedButton:
            text: 'İkisi de'
            md_bg_color: get_color_from_hex('#9400d3')
            on_press: root.set_mode('both')

<MainScreen@MDBoxLayout>:
    orientation: 'vertical'
    
    MDToolbar:
        title: '✨ NOVA AI'
        elevation: 4
        left_action_items: [['menu', lambda x: None]]
        right_action_items: [['dots-vertical', lambda x: None]]
        md_bg_color: get_color_from_hex('#9400d3')
        specific_text_color: 1, 1, 1, 1
    
    ScrollView:
        id: scroll_view
        do_scroll_x: False
        
        MDList:
            id: chat_list
            padding: '10dp'
            spacing: '5dp'
    
    MDBoxLayout:
        orientation: 'horizontal'
        padding: '10dp'
        spacing: '10dp'
        size_hint_y: None
        height: '70dp'
        md_bg_color: get_color_from_hex('#2e2e2e')
        
        MDTextField:
            id: message_input
            hint_text: 'Mesajınızı yazın...'
            mode: 'fill'
            fill_color: get_color_from_hex('#3e3e3e')
            active_hint_text_color: get_color_from_hex('#9400d3')
            text_color: 1, 1, 1, 1
            hint_text_color: 0.7, 0.7, 0.7, 1
            size_hint_x: 0.8
            
        MDIconButton:
            icon: 'microphone'
            md_bg_color: get_color_from_hex('#9400d3')
            icon_color: 1, 1, 1, 1
            on_press: root.voice_input()
            
        MDRaisedButton:
            text: 'Gönder'
            md_bg_color: get_color_from_hex('#9400d3')
            on_press: root.send_message()
            size_hint_x: 0.2
''')

class NovaAIApp(MDApp):
    theme_cls = ObjectProperty()
    communication_mode = StringProperty('both')
    
    def build(self):
        # Tema ayarları
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "A700"
        
        # Pencere ayarları
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        Window.size = (400, 700)
        
        # Başlangıç ekranı
        self.startup_screen = StartupScreen()
        self.startup_screen.set_mode = self.set_communication_mode
        
        # Ana ekran
        self.main_screen = MainScreen()
        self.main_screen.send_message = self.send_message
        self.main_screen.voice_input = self.voice_input
        
        # Sistem başlatma
        self.init_system()
        
        return self.startup_screen
    
    def init_system(self):
        """Sistem bileşenlerini başlat"""
        # Konuşma motoru
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            self.voice_enabled = True
        except:
            self.voice_enabled = False
            print("Ses özellikleri devre dışı")
        
        # Ses tanıma
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except:
            self.voice_enabled = False
            print("Mikrofon bulunamadı")
        
        # Gemini AI
        genai.configure(api_key="AIzaSyDCBktKAnxD2cFbLTVPxAzzwpgiIcgbPPI")
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Hafıza sistemleri
        self.conversation_history = []
        self.learned_facts = []
        self.user_preferences = {}
        self.interaction_count = 0
        self.memory_file = "nova_memory.json"
        self.notes_file = "nova_notes.json"
        
        # Dosyaları yükle
        self.load_memory()
        self.load_notes()
    
    def set_communication_mode(self, mode):
        """İletişim modunu ayarla"""
        self.communication_mode = mode
        self.complete_startup()
    
    def complete_startup(self):
        """Başlangıç ekranını tamamla"""
        # Ana ekrana geç
        self.root_window.clear_widgets()
        self.root_window.add_widget(self.main_screen)
        
        # Hoş geldin mesajı
        welcome_msg = "✨ Hoş geldin! Ben Nova, kişisel yapay zeka asistanınız."
        self.add_message("Nova", welcome_msg)
        
        if self.voice_enabled:
            self.speak(welcome_msg)
    
    def add_message(self, sender, message):
        """Mesaj ekle"""
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        # Mesaj kartı oluştur
        chat_item = ChatMessage(
            message=f"[b]{sender}[/b]\n{message}",
            timestamp=timestamp,
            is_user=(sender == "Siz")
        )
        
        # Listeye ekle
        self.main_screen.ids.chat_list.add_widget(chat_item)
        
        # Otomatik aşağı kaydır
        self.main_screen.ids.scroll_view.scroll_to(chat_item)
    
    def send_message(self, instance=None):
        """Mesaj gönder"""
        message_input = self.main_screen.ids.message_input
        user_input = message_input.text.strip()
        
        if not user_input:
            return
        
        self.add_message("Siz", user_input)
        message_input.text = ""
        
        # Cevap oluştur
        response = self.generate_response(user_input)
        self.add_message("Nova", response)
        
        # Sesli cevap
        if self.voice_enabled:
            threading.Thread(target=self.speak, args=(response,), daemon=True).start()
    
    def voice_input(self, instance=None):
        """Sesli giriş"""
        if not self.voice_enabled:
            self.add_message("Nova", "Ses özellikleri devre dışı.")
            return
        
        def listen():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio, language='tr-TR')
                self.main_screen.ids.message_input.text = text
                self.send_message()
                
            except sr.WaitTimeoutError:
                self.add_message("Nova", "Dinleme zaman aşımı...")
            except sr.UnknownValueError:
                self.add_message("Nova", "Anlayamadım, tekrar eder misin?")
            except Exception as e:
                self.add_message("Nova", f"Ses hatası: {str(e)}")
        
        threading.Thread(target=listen, daemon=True).start()
        self.add_message("Nova", "🎤 Dinliyorum...")
    
    def generate_response(self, user_input):
        """Cevap oluştur"""
        input_lower = user_input.lower()
        
        # Basit komutlar
        if "saat kaç" in input_lower:
            return f"Şu an saat {datetime.datetime.now().strftime('%H:%M')}"
        
        if "merhaba" in input_lower or "selam" in input_lower:
            greetings = ["Merhaba!", "Selam!", "Nasılsın?", "Görüşmek güzel!"]
            return random.choice(greetings)
        
        if "yardım" in input_lower:
            return """[b]✨ NOVA AI Özellikleri:[/b]

🤖 [b]Yapay Zeka:[/b]
• Akıllı sohbet (Gemini 2.5 Flash)
• Soru-cevap
• Öğrenme ve gelişme

🎤 [b]Sesli Özellikler:[/b]
• Sesli komutlar
• Konuşma tanıma
• Sesli cevap

📸 [b]Görüntü İşleme:[/b]
• Fotoğraf analizi
• Nesne tanıma
• QR kod okuma

🌍 [b]Bilgi Erişimi:[/b]
• Web arama
• Çeviri
• Hava durumu

📝 [b]Kişisel Asistan:[/b]
• Not alma
• Hatırlatıcılar
• Takvim yönetimi

🎮 [b]Eğlence:[/b]
• Oyunlar
• Sohbet
• Rastgele cevaplar"""
        
        # Gemini AI'ya sor
        try:
            system_prompt = """Sen Nova, Türkçe bir yapay zeka asistanısın. 
            Modern, şık ve akıllı bir şekilde cevap ver. 
            Kısa ve öz cevaplar ver. Türkçe konuş."""
            
            full_prompt = f"{system_prompt}\n\nKullanıcı: {user_input}"
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"AI hatası: {str(e)}"
    
    def speak(self, text):
        """Sesli konuşma"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Ses hatası: {e}")
    
    def load_memory(self):
        """Hafızayı yükle"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get("conversation_history", [])
                    self.learned_facts = data.get("learned_facts", [])
                    self.user_preferences = data.get("user_preferences", [])
                    self.interaction_count = data.get("interaction_count", 0)
        except:
            pass
    
    def load_notes(self):
        """Notları yükle"""
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"notlar": [], "hatırlatıcılar": []}

if __name__ == '__main__':
    NovaAIApp().run()
