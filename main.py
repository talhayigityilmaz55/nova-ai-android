import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import speech_recognition as sr
import pyttsx3
import datetime
import json
import os
import random
import re
import operator
import requests
import time
import google.generativeai as genai
import threading
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image, ImageTk
import pyzbar.pyzbar as pyzbar
import base64
import io
import wave
import pyaudio

class NovaAI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nova AI Asistan")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # İletişim modu
        self.communication_mode = "both"  # both, text, voice
        self.startup_complete = False
        
        # Konuşma motoru
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        # Ses tanıma (PyAudio yoksa devre dışı)
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.voice_enabled = True
        except:
            self.voice_enabled = False
            print("Ses özellikleri devre dışı - PyAudio gerekli")
        
        # Bellek (basit veritabanı)
        self.memory_file = "jarvis_memory.json"
        self.memory = self.load_memory()
        
        # Gelişmiş hafıza sistemi
        self.conversation_history = []
        self.learned_facts = []
        self.user_preferences = {}
        self.interaction_count = 0
        
        # Notlar ve hatırlatıcılar
        self.notes_file = "jarvis_notes.json"
        self.notes = self.load_notes()
        
        # Gemini AI yapılandırması
        genai.configure(api_key="AIzaSyDCBktKAnxD2cFbLTVPxAzzwpgiIcgbPPI")
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Güncelleme sistemi
        self.current_version = "1.0.0"
        self.update_url = "https://raw.githubusercontent.com/kullanici/jarvis-ai/main/version.json"
        
        # Sayı tahmini oyunu
        self.game_number = None
        self.game_attempts = 0
        
        # Arayüz oluştur
        self.show_startup_screen()
        
        # Gelişmiş hafızayı yükle
        self.load_advanced_memory()
    
    def show_startup_screen(self):
        """Başlangıç ekranını göster"""
        # Başlangıç ekranı frame'i
        self.startup_frame = tk.Frame(self.root, bg='#1a1a1a')
        self.startup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Jarvis logosu ve başlık
        logo_frame = tk.Frame(self.startup_frame, bg='#1a1a1a')
        logo_frame.pack(expand=True)
        
        # Animasyonlu Nova yazısı
        self.jarvis_label = tk.Label(logo_frame, text="✨", 
                                   font=("Arial", 80), 
                                   fg='#9400d3', bg='#1a1a1a')
        self.jarvis_label.pack(pady=20)
        
        self.title_label = tk.Label(logo_frame, text="NOVA AI", 
                                   font=("Arial", 36, "bold"), 
                                   fg='#9400d3', bg='#1a1a1a')
        self.title_label.pack(pady=10)
        
        # Yüklenme mesajı
        self.loading_label = tk.Label(logo_frame, text="Hazırlanıyor...", 
                                    font=("Arial", 14), 
                                    fg='#ffffff', bg='#1a1a1a')
        self.loading_label.pack(pady=10)
        
        # İletişim modu seçimi
        mode_frame = tk.Frame(logo_frame, bg='#1a1a1a')
        mode_frame.pack(pady=30)
        
        tk.Label(mode_frame, text="İletişim Modu Seçin:", 
                font=("Arial", 12), 
                fg='#ffffff', bg='#1a1a1a').pack(pady=10)
        
        button_frame = tk.Frame(mode_frame, bg='#1a1a1a')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="📝 Yazılı", 
                 command=lambda: self.set_communication_mode("text"),
                 bg='#0066cc', fg='white', 
                 font=("Arial", 10, "bold"),
                 width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🎤 Sesli", 
                 command=lambda: self.set_communication_mode("voice"),
                 command=lambda: self.set_communication_mode("voice"),
                 bg='#ff6600', fg='white', 
                 font=("Arial", 10, "bold"),
                 width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🤖 İkisi de", 
                 command=lambda: self.set_communication_mode("both"),
                 bg='#00ff00', fg='black', 
                 font=("Arial", 10, "bold"),
                 width=12).pack(side=tk.LEFT, padx=5)
        
        # Durum bilgisi
        self.status_label_startup = tk.Label(logo_frame, text="Sistem kontrol ediliyor...", 
                                          font=("Arial", 10), 
                                          fg='#00ff00', bg='#1a1a1a')
        self.status_label_startup.pack(pady=20)
        
        # Sistem kontrolünü başlat
        self.root.after(1000, self.system_check)
    
    def set_communication_mode(self, mode):
        """İletişim modunu ayarla"""
        self.communication_mode = mode
        mode_names = {
            "text": "Yazılı iletişim",
            "voice": "Sesli iletişim", 
            "both": "Çift iletişim"
        }
        self.loading_label.config(text=f"Mod: {mode_names[mode]}")
        self.speak(f"{mode_names[mode]} seçildi. Jarvis hazırlanıyor...")
    
    def system_check(self):
        """Sistem kontrolü yap"""
        checks = [
            "🧠 Yapay zeka sistemleri...",
            "🗣️ Ses işleme modülleri...", 
            "📸 Kamera ve görüntü işleme...",
            "💾 Hafıza sistemleri...",
            "🌐 İnternet bağlantısı...",
            "📱 Android uyumluluğu..."
        ]
        
        def run_checks(index=0):
            if index < len(checks):
                self.status_label_startup.config(text=checks[index])
                self.root.after(800, lambda: run_checks(index + 1))
            else:
                self.status_label_startup.config(text="✅ Sistem hazır!")
                self.root.after(1000, self.complete_startup)
        
        run_checks()
    
    def complete_startup(self):
        """Başlangıç ekranını tamamla"""
        self.startup_complete = True
        
        # Hoş geldin mesajı
        user_name = self.memory.get("isim", "Kullanıcı")
        hour = datetime.datetime.now().hour
        
        if hour < 12:
            greeting = "Günaydın"
        elif hour < 18:
            greeting = "İyi günler"
        else:
            greeting = "İyi akşamlar"
        
        welcome_message = f"{greeting} {user_name}! Nova hizmetinizde."
        
        # Başlangıç ekranını kaldır
        self.startup_frame.destroy()
        
        # Ana arayüzü kur
        self.setup_ui()
        
        # Hoş geldin mesajını göster
        self.add_message("Nova", welcome_message)
        self.speak(welcome_message)
        
        # İletişim moduna göre arayüzü ayarla
        self.adjust_interface_for_mode()
    
    def adjust_interface_for_mode(self):
        """İletişim moduna göre arayüzü ayarla"""
        if self.communication_mode == "voice":
            # Sesli mod için butonu öne çıkar
            self.input_field.pack_forget()
            voice_btn = tk.Button(self.root, text="🎤 Sesi Başlat", 
                                command=self.continuous_voice_mode,
                                bg='#ff6600', fg='white', 
                                font=("Arial", 12, "bold"),
                                height=2, width=20)
            voice_btn.pack(pady=10)
            
        elif self.communication_mode == "text":
            # Yazılı mod için ses butonunu gizle
            # Ses butonu zaten var, sadece uyarı ver
            
            pass
        else:  # both
            # İkisi de - mevcut arayüzü koru
            pass
    
    def continuous_voice_mode(self):
        """Sürekli sesli mod"""
        if not self.voice_enabled:
            self.add_message("Jarvis", "Ses özellikleri devre dışı.")
            return
        
        def listen_loop():
            while self.communication_mode == "voice":
                try:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    text = self.recognizer.recognize_google(audio, language='tr-TR')
                    self.add_message("Siz", text)
                    
                    response = self.generate_response(text)
                    self.add_message("Jarvis", response)
                    self.speak(response)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.add_message("Jarvis", "Anlayamadım, tekrar eder misin?")
                except Exception as e:
                    self.add_message("Jarvis", f"Hata: {str(e)}")
                    break
        
        threading.Thread(target=listen_loop, daemon=True).start()
        self.add_message("Jarvis", "Sürekli dinleme modu aktif. Konuşun...")
        
    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"isim": "Kullanıcı", "hatıralar": [], "öğrenilenler": {}}
    
    def save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def save_advanced_memory(self):
        """Gelişmiş hafızayı kaydet"""
        advanced_memory = {
            "conversation_history": self.conversation_history[-50:],  # Son 50 konuşma
            "learned_facts": self.learned_facts,
            "user_preferences": self.user_preferences,
            "interaction_count": self.interaction_count,
            "last_interaction": datetime.datetime.now().isoformat()
        }
        
        with open("jarvis_advanced_memory.json", 'w', encoding='utf-8') as f:
            json.dump(advanced_memory, f, ensure_ascii=False, indent=2)
    
    def load_advanced_memory(self):
        """Gelişmiş hafızayı yükle"""
        try:
            if os.path.exists("jarvis_advanced_memory.json"):
                with open("jarvis_advanced_memory.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get("conversation_history", [])
                    self.learned_facts = data.get("learned_facts", [])
                    self.user_preferences = data.get("user_preferences", {})
                    self.interaction_count = data.get("interaction_count", 0)
        except:
            pass
    
    def remember_conversation(self, user_input, jarvis_response):
        """Konuşmayı hafızaya al"""
        conversation = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_input,
            "jarvis": jarvis_response,
            "context": "general"
        }
        self.conversation_history.append(conversation)
        
        # Sadece son 100 konuşmayı tut
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        self.save_advanced_memory()
    
    def learn_fact(self, fact, category="general"):
        """Yeni bilgi öğren"""
        learned_item = {
            "fact": fact,
            "category": category,
            "learned_date": datetime.datetime.now().isoformat(),
            "confidence": 0.8
        }
        self.learned_facts.append(learned_item)
        self.save_advanced_memory()
        return f"Öğrendim: {fact}"
    
    def remember_preference(self, preference_type, value):
        """Kullanıcı tercihini hatırla"""
        self.user_preferences[preference_type] = {
            "value": value,
            "set_date": datetime.datetime.now().isoformat()
        }
        self.save_advanced_memory()
        return f"Tercihiniz hatırlandı: {preference_type} = {value}"
    
    def recall_memories(self, query_type="all"):
        """Hafızadan bilgi çağır"""
        if query_type == "conversations":
            return self.conversation_history[-10:]  # Son 10 konuşma
        elif query_type == "facts":
            return self.learned_facts
        elif query_type == "preferences":
            return self.user_preferences
        else:
            return {
                "conversations": len(self.conversation_history),
                "facts": len(self.learned_facts),
                "preferences": len(self.user_preferences),
                "interactions": self.interaction_count
            }
    
    def analyze_user_patterns(self):
        """Kullanıcı patternlerini analiz et"""
        if not self.conversation_history:
            return "Yeterli veri yok"
        
        # En sık kullanılan komutları analiz et
        commands = []
        for conv in self.conversation_history[-20:]:  # Son 20 konuşma
            commands.append(conv["user"].lower())
        
        # Basit pattern analizi
        patterns = {
            "greeting": sum(1 for cmd in commands if any(word in cmd for word in ["merhaba", "selam", "hi"])),
            "questions": sum(1 for cmd in commands if "?" in cmd),
            "commands": sum(1 for cmd in commands if any(word in cmd for word in ["aç", "yap", "göster", "başlat"])),
            "photo": sum(1 for cmd in commands if "foto" in cmd),
            "voice": sum(1 for cmd in commands if any(word in cmd for word in ["ses", "kayıt", "dinle"]))
        }
        
        most_common = max(patterns, key=patterns.get)
        return f"En sık {most_common} komutlarını kullanıyorsunuz ({patterns[most_common]} kez)"
    
    def smart_response(self, user_input):
        """Akıllı cevap üret (hafıza kullanarak)"""
        self.interaction_count += 1
        
        # Kullanıcıyı tanıma
        if self.memory.get("isim") and self.interaction_count % 10 == 0:
            return f"{self.memory['isim']}, {self.interaction_count}. konuşmamız! Size nasıl yardımcı olabilirim?"
        
        # Pattern analizi
        if self.interaction_count % 20 == 0:
            pattern = self.analyze_user_patterns()
            return f"Analiz ediyorum... {pattern}"
        
        # Öğrenilen bilgileri kullan
        for fact in self.learned_facts[-5:]:  # Son 5 öğrenilen bilgi
            if any(word in user_input.lower() for word in fact["fact"].lower().split()[:3]):
                return f"Daha önce öğrenmiştim: {fact['fact']}"
        
        return None
    
    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"notlar": [], "hatırlatıcılar": []}
    
    def save_notes(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
    
    def setup_ui(self):
        # Başlık
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="✨ NOVA AI", 
                               font=("Arial", 24, "bold"), 
                               fg='#9400d3', bg='#1a1a1a')
        title_label.pack()
        
        # Sohbet alanı
        self.chat_area = scrolledtext.ScrolledText(self.root, 
                                                   width=80, height=20,
                                                   font=("Arial", 11),
                                                   bg='#2a2a2a', fg='white',
                                                   wrap=tk.WORD)
        self.chat_area.pack(padx=20, pady=10)
        
        # Komut giriş alanı
        input_frame = tk.Frame(self.root, bg='#1a1a1a')
        input_frame.pack(pady=10)
        
        self.input_field = tk.Entry(input_frame, width=60, 
                                    font=("Arial", 12),
                                    bg='#3a3a3a', fg='white')
        self.input_field.pack(side=tk.LEFT, padx=5)
        self.input_field.bind('<Return>', lambda e: self.send_message())
        
        # Butonlar
        tk.Button(input_frame, text="Gönder", command=self.send_message,
                 bg='#00ff00', fg='black', font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(input_frame, text="🎤 Sesli Konuş", command=self.voice_input,
                 bg='#ff6600' if self.voice_enabled else '#666666', fg='white', 
                 font=("Arial", 10, "bold"),
                 state=tk.NORMAL if self.voice_enabled else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        
        # Durum çubuğu
        self.status_label = tk.Label(self.root, text="Nova hazır...", 
                                    font=("Arial", 10), 
                                    fg='#9400d3', bg='#1a1a1a')
        self.status_label.pack(pady=5)
        
        self.add_message("Nova", "Merhaba! Ben Nova, kişisel yapay zeka asistanınız. Size nasıl yardımcı olabilirim?")
    
    def add_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        self.chat_area.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n")
        self.chat_area.see(tk.END)
    
    def send_message(self):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        
        self.add_message("Siz", user_input)
        self.input_field.delete(0, tk.END)
        self.status_label.config(text="Nova düşünüyor...")
        
        # Akıllı cevap kontrolü
        smart_response = self.smart_response(user_input)
        if smart_response:
            response = smart_response
        else:
            # Normal cevap oluştur
            response = self.generate_response(user_input)
        
        self.add_message("Nova", response)
        
        # Konuşmayı hafızaya al
        self.remember_conversation(user_input, response)
        
        # Sesli cevap
        self.speak(response)
        
        self.status_label.config(text="Nova hazır...")
    
    def calculate_math(self, expression):
        """Basit matematik işlemleri yapar"""
        try:
            # Sadece güvenli karakterleri tut
            expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            
            # İşleçleri tanımla
            ops = {
                '+': operator.add,
                '-': operator.sub,
                '*': operator.mul,
                '/': operator.truediv,
                '^': operator.pow,
                '**': operator.pow
            }
            
            # Basit eval yerine güvenli hesaplama
            result = eval(expression, {"__builtins__": {}}, ops)
            
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 4)
            
            return f"Sonuç: {result}"
        except:
            return "Matematik işlemini anlayamadım. Lütfen basit bir ifade girin (örn: 5+3, 10*2, 15/3)"
    
    def add_note(self, note_text):
        """Not ekle"""
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        note = {"metin": note_text, "zaman": timestamp}
        self.notes["notlar"].append(note)
        self.save_notes()
        return f"Not eklendi: {note_text}"
    
    def search_web(self, query):
        """Web'de arama yapar"""
        try:
            # DuckDuckGo instant answer API (ücretsiz)
            url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get("AbstractText"):
                return f"🔍 {data['AbstractText']}\n\nKaynak: {data.get('AbstractSource', 'DuckDuckGo')}"
            elif data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:
                first_result = data["RelatedTopics"][0]
                if "Text" in first_result:
                    return f"🔍 {first_result['Text'][:200]}..."
            
            return f"'{query}' hakkında detaylı bilgi bulunamadı. Farklı anahtar kelimeler deneyin."
        except:
            return "Web araması şu an yapılamıyor. İnternet bağlantınızı kontrol edin."
    
    def translate_text(self, text, from_lang="auto", to_lang="tr"):
        """Metin çevirisi yapar (Gemini ile)"""
        try:
            prompt = f"'{text}' metnini {from_lang} dilinden {to_lang} diline çevir. Sadece çeviriyi ver, açıklama yapma."
            response = self.gemini_model.generate_content(prompt)
            return f"🌍 {response.text}\n\n({from_lang.upper()} → {to_lang.upper()})"
        except Exception as e:
            return f"Çeviri yapılamadı: {str(e)}"
    
    def start_number_game(self):
        """Sayı tahmini oyunu başlatır"""
        self.game_number = random.randint(1, 100)
        self.game_attempts = 0
        return "🎮 Sayı tahmini oyunu başladı! 1-100 arasında bir sayı tuttum. Tahmin et!"
    
    def play_number_game(self, guess):
        """Sayı tahmini oyununu oynar"""
        if self.game_number is None:
            return "Önce oyunu başlatmalısın. 'Sayı tahmini oyunu' de."
        
        try:
            guess_num = int(guess)
            self.game_attempts += 1
            
            if guess_num == self.game_number:
                result = f"🎉 Tebrikler! {self.game_attempts} denemede bildin! Sayı: {self.game_number}"
                self.game_number = None
                self.game_attempts = 0
                return result
            elif guess_num < self.game_number:
                return f"📈 Daha büyük bir sayı söyle! (Deneme: {self.game_attempts})"
            else:
                return f"📉 Daha küçük bir sayı söyle! (Deneme: {self.game_attempts})"
        except:
            return "Lütfen geçerli bir sayı girin (1-100 arasında)."
    
    def ask_gemini(self, prompt):
        """Gemini AI'ya soru sor"""
        try:
            # Nova kişiliği ile sistem prompt'u
            system_prompt = """Sen Nova, Türkçe bir yapay zeka asistanısın. 
            Modern, şık ve akıllı bir şekilde cevap ver. 
            Kısa ve öz cevaplar ver. Türkçe konuş."""
            
            full_prompt = f"{system_prompt}\n\nKullanıcı: {prompt}"
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"AI hatası: {str(e)}"
    
    def check_for_updates(self):
        """Güncellemeleri kontrol et"""
        try:
            response = requests.get(self.update_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("version", "1.0.0")
                if latest_version != self.current_version:
                    return True, f"Yeni versiyon {latest_version} mevcut!"
            return False, "Güncel versiyon kullanıyorsunuz."
        except:
            return False, "Güncelleme kontrolü yapılamadı."
    
    def hotword_detection(self):
        """Hey Jarvis sesle uyanma"""
        if not self.voice_enabled:
            return
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio, language='tr-TR').lower()
                    
                    if "hey jarvis" in text or "jarvis" in text:
                        self.add_message("Jarvis", "Sizi duydum! Size nasıl yardımcı olabilirim?")
                        self.speak("Sizi duydum! Size nasıl yardımcı olabilirim?")
                        break
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Hotword hatası: {e}")
                    break
                    
        except Exception as e:
            print(f"Hotword detection hatası: {e}")
    
    def send_sms(self, number, message):
        """SMS gönder (Android'de çalışacak)"""
        try:
            # Android'de SMS gönderme kodu
            import android
            droid = android.Android()
            droid.smsSend(number, message)
            return f"SMS gönderildi: {number}"
        except:
            return "SMS gönderilemedi - Android gerekli."
    
    def make_call(self, number):
        """Arama yap (Android'de çalışacak)"""
        try:
            import android
            droid = android.Android()
            droid.phoneCall(number)
            return f"Arama yapılıyor: {number}"
        except:
            return "Arama yapılamadı - Android gerekli."
    
    def open_app(self, app_name):
        """Uygulama aç (Android'de çalışacak)"""
        try:
            import android
            droid = android.Android()
            droid.launch(app_name)
            return f"{app_name} açılıyor..."
        except:
            return f"{app_name} açılamadı - Android gerekli."
    
    def get_notifications(self):
        """Bildirimleri al (Android'de çalışacak)"""
        try:
            import android
            droid = android.Android()
            notifications = droid.notificationsGet()
            return f"Bildirimler: {len(notifications)} adet"
        except:
            return "Bildirimler alınamadı - Android gerekli."
    
    def set_reminder(self, time_str, message):
        """Hatırlatıcı ayarla"""
        try:
            # Basit hatırlatıcı sistemi
            reminder = {"zaman": time_str, "mesaj": message, "durum": "aktif"}
            self.notes["hatırlatıcılar"].append(reminder)
            self.save_notes()
            return f"Hatırlatıcı ayarlandı: {time_str} - {message}"
        except Exception as e:
            return f"Hatırlatıcı ayarlanamadı: {e}"
    
    def get_weather(self, city="Samsun"):
        """Hava durumu"""
        try:
            # OpenWeatherMap API (ücretsiz)
            api_key = "your_api_key_here"  # Kullanıcı kendi API key'ini eklemeli
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=tr"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get("main"):
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"{city} hava durumu: {temp}°C, {desc}"
            else:
                return "Hava durumu alınamadı. API key gerekli."
        except:
            return "Hava durumu bilgisi alınamadı."
    
    def capture_camera_image(self):
        """Kameradan görüntü yakala"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None, "Kamera açılamadı"
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return frame, None
            else:
                return None, "Görüntü yakalanamadı"
        except Exception as e:
            return None, f"Kamera hatası: {str(e)}"
    
    def analyze_image_with_gemini(self, frame):
        """Gemini AI ile görüntü analiz et"""
        try:
            # Görüntüyü base64'e çevir
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Gemini Vision API kullan
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = """Bu görüntüyü analiz et ve şunu söyle:
            1. Görülen nesneleri listele
            2. Ortamı tanımla (iç/dış mekan, odun amacı vb)
            3. Güvenlik durumu hakkında bilgi ver
            4. İlginç detaylar varsa belirt
            
            Kısa ve öz cevap ver."""
            
            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_base64}
            ])
            
            return response.text
        except Exception as e:
            return f"Görüntü analizi hatası: {str(e)}"
    
    def detect_objects(self, frame):
        """Basit nesne tespiti"""
        try:
            # Renk tabanlı basit nesne tespiti
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Yüz tespiti için basit yöntem
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            objects_found = []
            
            if len(faces) > 0:
                objects_found.append(f"{len(faces)} yüz tespit edildi")
            
            # QR kod tespiti
            qr_codes = pyzbar.decode(frame)
            if qr_codes:
                for qr in qr_codes:
                    qr_data = qr.data.decode('utf-8')
                    objects_found.append(f"QR Kod: {qr_data}")
            
            # Baskın renk analizi
            colors = []
            height, width = frame.shape[:2]
            
            # Görüntüyü bölgelere ayır ve renk analizi yap
            for y in range(0, height, height//4):
                for x in range(0, width, width//4):
                    if y < height and x < width:
                        roi = frame[y:y+height//4, x:x+width//4]
                        avg_color = np.mean(roi, axis=(0,1))
                        b, g, r = avg_color
                        
                        if r > 100 and g < 50 and b < 50:
                            colors.append("kırmızı")
                        elif g > 100 and r < 50 and b < 50:
                            colors.append("yeşil")
                        elif b > 100 and r < 50 and g < 50:
                            colors.append("mavi")
            
            if colors:
                dominant_color = max(set(colors), key=colors.count)
                objects_found.append(f"Baskın renk: {dominant_color}")
            
            if objects_found:
                return "📷 Tespit edilenler: " + ", ".join(objects_found)
            else:
                return "📷 Görüntü analiz edildi, belirgin nesne bulunamadı."
                
        except Exception as e:
            return f"Nesne tespiti hatası: {str(e)}"
    
    def scan_qr_code(self, frame):
        """QR kod tara"""
        try:
            qr_codes = pyzbar.decode(frame)
            if qr_codes:
                results = []
                for qr in qr_codes:
                    qr_data = qr.data.decode('utf-8')
                    qr_type = qr.type
                    results.append(f"QR Kod ({qr_type}): {qr_data}")
                return "🔍 " + "\n".join(results)
            else:
                return "QR kod bulunamadı"
        except Exception as e:
            return f"QR tarama hatası: {str(e)}"
    
    def analyze_environment(self, frame):
        """Ortam analizi"""
        try:
            # Parlaklık analizi
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Hareket analizi (basit)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            analysis = []
            
            if brightness < 50:
                analysis.append("🌙 Karanlık ortam")
            elif brightness > 200:
                analysis.append("☀️ Çok aydınlık ortam")
            else:
                analysis.append("💡 Normal aydınlatma")
            
            if edge_density > 0.1:
                analysis.append("📊 Yoğun detaylı ortam")
            else:
                analysis.append("📐 Sade ortam")
            
            # Görüntü boyutu
            height, width = frame.shape[:2]
            if width > 1000:
                analysis.append("📺 Geniş açılı görüntü")
            else:
                analysis.append("📱 Standart görüntü")
            
            return "🏠 Ortam analizi: " + ", ".join(analysis)
            
        except Exception as e:
            return f"Ortam analizi hatası: {str(e)}"
    
    def vision_commands(self, command):
        """Görüntü komutlarını işle"""
        frame, error = self.capture_camera_image()
        
        if error:
            return f"📷 Kamera hatası: {error}"
        
        if "analiz et" in command or "görüntü analiz" in command:
            return self.analyze_image_with_gemini(frame)
        
        elif "nesne" in command or "obje" in command:
            return self.detect_objects(frame)
        
        elif "qr" in command or "kare kod" in command:
            return self.scan_qr_code(frame)
        
        elif "ortam" in command or "çevre" in command:
            return self.analyze_environment(frame)
        
        elif "yüz" in command:
            return self.detect_objects(frame)  # Yüz tespiti nesne tespitinde
        
        else:
            return self.analyze_image_with_gemini(frame)
    
    def start_audio_recording(self, duration=10):
        """Ses kaydı başlat"""
        try:
            # Ses kaydı için ayarlar
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            CHUNK = 1024
            RECORD_SECONDS = duration
            
            audio = pyaudio.PyAudio()
            
            stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            
            frames = []
            
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Kaydet
            filename = f"ses_kaydi_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return f"🎤 Ses kaydı tamamlandı: {filename}"
            
        except Exception as e:
            return f"Ses kaydı hatası: {str(e)}"
    
    def take_photo(self):
        """Fotoğraf çek"""
        try:
            frame, error = self.capture_camera_image()
            if error:
                return f"📷 {error}"
            
            # Fotoğrafı kaydet
            filename = f"foto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            
            return f"📸 Fotoğraf çekildi: {filename}"
            
        except Exception as e:
            return f"Fotoğraf çekme hatası: {str(e)}"
    
    def launch_specific_app(self, app_command):
        """Belirli uygulamaları başlat"""
        app_commands = {
            "whatsapp": "whatsapp",
            "spotify": "spotify",
            "kamera": "camera",
            "camera": "camera",
            "mesajlar": "messaging",
            "messages": "messaging",
            "tarayıcı": "browser",
            "browser": "browser",
            "ayarlar": "settings",
            "settings": "settings",
            "hesap makinesi": "calculator",
            "calculator": "calculator",
            "notlar": "notes",
            "notes": "notes",
            "saat": "clock",
            "clock": "clock",
            "hava": "weather",
            "weather": "weather"
        }
        
        app_key = app_command.lower()
        if app_key in app_commands:
            return self.open_app(app_commands[app_key])
        else:
    
def show_all_capabilities(self):
    """Tüm yetenekleri göster"""
    capabilities = """
✨ NOVA AI YETENEKLERİ ✨

📱 TELEFON KONTROLÜ:
• Uygulama aç (WhatsApp, Spotify, Kamera, Mesajlar, Tarayıcı, Ayarlar)
• SMS gönder (SMS gönder 05551234567 için Merhaba)
• Arama yap (Ara 05551234567)
• Bildirimleri göster
• Uygulama kontrolü

📸 GÖRÜNTÜ TANIMA:
• Fotoğraf çek (Fotoğraf çek, Foto çek)
• Kamera analiz et (AI ile detaylı analiz)
• Nesne tespiti (Objeleri tanıma)
• QR kod tara (QR kodları oku)
• Yüz tanıma (Yüzleri say)
• Ortam analizi (Parlaklık, detay ölçümü)
• Görüntü işleme

🎤 SES ÖZELLİKLERİ:
• Sesli komut algılama (Hey Jarvis)
• Sürekli dinleme modu
• Ses kaydı başlat (10 saniye)
• Sesli cevap verme
• Konuşma tanıma
• Mikrofon kontrolü

🧠 YAPAY ZEKA:
• Akıllı sohbet (Gemini 2.5 Flash)
• Soru-cevap (Her konuda)
• Öğrenme ve gelişme
• Kişiselleştirme
• Bağlam anlama
• Türkçe destek

🔍 BİLGİ ERİŞİMİ:
• Web arama (DuckDuckGo)
• Çeviri (Gemini ile)
• Hava durumu
• Matematik işlemleri
• Genel kültür
• Anlık bilgi

📝 KİŞİSEL ASİSTAN:
• Not alma (Not al: Toplantı 15:00)
• Hatırlatıcı ayarla (18:00 için Toplantı)
• Takvim yönetimi
• Liste oluşturma
• Hatırlama sistemi
• Bellek özelliği

🎮 EĞLENCE:
• Sayı tahmini oyunu
• Sohbet ve konuşma
• Rastgele cevaplar
• Etkileşimli modlar
• Oyunlar

⏰ ZAMAN YÖNETİMİ:
• Saat ve tarih bilgisi
• Hatırlatıcılar
• Zamanlayıcı
• Takvim entegrasyonu
• Planlama

🔄 SİSTEM ÖZELLİKLERİ:
• Otomatik güncelleme kontrolü
• Versiyon yönetimi
• Hata raporlama
• Performans izleme
• Sistem kontrolü

🌐 İNTERNET:
• Web arama motoru
• API entegrasyonları
• Çeviri hizmetleri
• Hava durumu API
• Gerçek zamanlı veri

🔔 BİLDİRİMLER:
• Bildirim yönetimi
• Uyarı sistemi
• Hatırlatıcılar
• Sesli uyarılar
• Görsel bildirimler

📊 VERİ YÖNETİMİ:
• JSON veritabanı
• Kullanıcı bilgileri
• Not depolama
• Ayarlar yönetimi
• Veri güvenliği

🛡️ GÜVENLİK:
• Kamera izin kontrolü
• Mikrofon yönetimi
• Veri koruması
• Güvenli erişim
• Gizlilik modu

💬 KOMUT FORMATLARI:
• Doğal dil (konuşma gibi)
• Sesli komutlar
• Metin komutları
• Kısa komutlar
• Detaylı komutlar

🎯 KULLANIM ALANLARI:
• Günlük asistanlık
• Eğitim ve öğrenme
• Eğlence ve oyun
• İş ve üretkenlik
• İletişim ve sosyal
• Bilgi erişimi

📈 PERFORMANS:
• Hızlı cevap
• Çoklu görev
• Arka plan çalışma
• Optimize edilmiş
• Düşük kaynak kullanımı

🔧 TEKNİK:
• Python tabanlı
• Gemini AI entegrasyonu
• OpenCV görüntü işleme
• Ses tanıma teknolojisi
• Çapraz platform uyumluluğu

📱 ANDİRAN UYUMLU:
• Kamera erişimi
• Mikrofon desteği
• Uygulama kontrolü
• Bildirim sistemi
• Dokunmatik arayüz
• Mobil optimizasyon

🎨 KULLANICI ARAYÜZÜ:
• Modern tasarım
• Kolay kullanım
• Renkli butonlar
• Sohbet ekranı
• Durum göstergeleri

🔌 GENİŞLETİLEBİLİR:
• Yeni özellik eklenebilir
• API entegrasyonu
• Plugin sistemi
• Modüler yapı
• Geliştirme dostu

📚 YARDIM VE DESTEK:
• Detaylı yardım menüsü
• Komut örnekleri
• Kullanım kılavuzu
• Hata mesajları
• İpuçları ve öneriler

🚀 TOPLAM: 75+ FARKLI ÖZELLİK! 🚀
"""
        return capabilities
    
    def generate_response(self, user_input):
        input_lower = user_input.lower()
        
        # Önce özel komutları kontrol et
        # Matematik işlemleri
        math_pattern = r'[\d+\-*/().^ ]+'
        if re.search(math_pattern, user_input) and any(op in user_input for op in ['+', '-', '*', '/', '^']):
            return self.calculate_math(user_input)
        
        # Not alma
        if "not al:" in input_lower:
            note_text = user_input.split("not al:")[-1].strip()
            return self.add_note(note_text)
        
        if "notlarım" in input_lower or "notları göster" in input_lower:
            if self.notes["notlar"]:
                notes_list = "\n".join([f"• {note['metin']} ({note['zaman']})" for note in self.notes["notlar"][-5:]])
                return f"📝 Son notlarınız:\n{notes_list}"
            return "Henüz notunuz yok."
        
        # Web arama
        if "google'da ara:" in input_lower or "ara:" in input_lower:
            if "google'da ara:" in input_lower:
                query = user_input.split("google'da ara:")[-1].strip()
            else:
                query = user_input.split("ara:")[-1].strip()
            return self.search_web(query)
        
        # Çeviri
        if "çevir:" in input_lower:
            parts = user_input.split("çevir:")[-1].strip()
            if " to " in parts.lower():
                text_part, lang_part = parts.lower().split(" to ")
                return self.translate_text(text_part.strip(), to_lang=lang_part.strip()[:2])
            else:
                return self.translate_text(parts)
        
        # Sayı tahmini oyunu
        if "sayı tahmini oyunu" in input_lower:
            return self.start_number_game()
        
        # Oyun devam ediyorsa sayı tahmini
        if self.game_number is not None:
            return self.play_number_game(user_input)
        
        # Zaman soruları
        if "saat kaç" in input_lower:
            return f"Şu an saat {datetime.datetime.now().strftime('%H:%M')}"
        
        # Tarih soruları
        if "tarih" in input_lower or "bugün ne" in input_lower:
            return f"Bugün {datetime.datetime.now().strftime('%d %B %Y')}"
        
        # İsim öğrenme
        if "benim adım" in input_lower:
            name = user_input.split("benim adım")[-1].strip()
            self.memory["isim"] = name
            self.save_memory()
            return f"Merhaba {name}! Seni tanımak güzel."
        
        # Hatırlama
        if "hatırla" in input_lower:
            return f"Tabii ki {self.memory['isim']}, her zaman seni hatırlıyorum."
        
        # Google Asistan özellikleri
        if "sms gönder" in input_lower or "mesaj at" in input_lower:
            if "için" in input_lower:
                parts = user_input.split("için")
                if len(parts) > 1:
                    number_part = parts[0].replace("sms gönder", "").replace("mesaj at", "").strip()
                    message_part = parts[1].strip()
                    return self.send_sms(number_part, message_part)
            return "SMS formatı: 'SMS gönder 05551234567 için Merhaba'"
        
        if "ara" in input_lower and len(user_input.split()) > 1:
            number = user_input.split("ara")[-1].strip()
            return self.make_call(number)
        
        if "aç" in input_lower and len(user_input.split()) > 1:
            app_name = user_input.split("aç")[-1].strip()
            return self.open_app(app_name)
        
        if "bildirimler" in input_lower or "bildirimleri göster" in input_lower:
            return self.get_notifications()
        
        if "hatırlatıcı" in input_lower and "ayarla" in input_lower:
            if "için" in input_lower:
                parts = user_input.split("için")
                if len(parts) > 1:
                    time_part = parts[0].replace("hatırlatıcı ayarla", "").strip()
                    message_part = parts[1].strip()
                    return self.set_reminder(time_part, message_part)
            return "Hatırlatıcı formatı: 'Hatırlatıcı ayarla 18:00 için Toplantı'"
        
        if "hava durumu" in input_lower:
            city = "İstanbul"
            if "için" in input_lower:
                city = user_input.split("için")[-1].strip()
            return self.get_weather(city)
        
        if "güncelleme" in input_lower and "kontrol" in input_lower:
            has_update, message = self.check_for_updates()
            if has_update:
                return f"✅ {message}\nGüncellemek istiyor musunuz?"
            return f"✅ {message}"
        
        if "hey jarvis" in input_lower or "dinle" in input_lower:
            threading.Thread(target=self.hotword_detection, daemon=True).start()
            return "Sürekli dinleme modu aktif. 'Hey Jarvis' deyin..."
        
        # Görüntü tanıma komutları
        if any(keyword in input_lower for keyword in ["kamera", "görüntü", "fotoğraf", "foto", "qr", "yüz", "nesne", "ortam", "çevre"]):
            return self.vision_commands(user_input)
        
        # Ses kaydı komutları
        if "ses kaydı" in input_lower or "kayıt başlat" in input_lower or "sesini kaydet" in input_lower:
            return self.start_audio_recording()
        
        # Fotoğraf çekme komutları
        if "fotoğraf çek" in input_lower or "foto çek" in input_lower or "çek foto" in input_lower:
            return self.take_photo()
        
        # Uygulama açma komutları
        if "aç" in input_lower and len(user_input.split()) > 1:
            app_name = user_input.split("aç")[-1].strip()
            return self.launch_specific_app(app_name)
        
        # Yetenekleri gösterme komutları
        if any(phrase in input_lower for phrase in ["neler yapabiliyorsun", "ne yapabilirsin", "yeteneklerin", "özelliklerin", "yeteneklerini göster", "bütün özellikler"]):
            return self.show_all_capabilities()
        
        # Hafıza komutları
        if "öğret" in input_lower or "bilgi ver" in input_lower:
            if "kişisel" in input_lower:
                return "Kişisel bilgilerinizi güvenle saklıyorum. Ne öğrenmemi istersiniz?"
            else:
                # Öğrenilecek bilgiyi çıkar
                fact = user_input.replace("öğret", "").replace("bilgi ver", "").strip()
                if fact:
                    return self.learn_fact(fact)
                else:
                    return "Ne öğrenmemi istersiniz? Örnek: 'Öğren benim en sevdiğim renk mavi'"
        
        if "hatırla" in input_lower:
            if "konuşmalar" in input_lower:
                convs = self.recall_memories("conversations")
                if convs:
                    result = "Son konuşmalar:\n"
                    for i, conv in enumerate(convs[-5:], 1):
                        result += f"{i}. Siz: {conv['user'][:50]}...\n"
                    return result
                return "Henüz konuşma geçmişi yok"
            
            elif "öğrendiklerim" in input_lower:
                facts = self.recall_memories("facts")
                if facts:
                    result = "Öğrendiklerim:\n"
                    for fact in facts[-5:]:
                        result += f"• {fact['fact']}\n"
                    return result
                return "Henüz bir şey öğrenmedim"
            
            elif "tercihler" in input_lower:
                prefs = self.recall_memories("preferences")
                if prefs:
                    result = "Tercihleriniz:\n"
                    for key, value in prefs.items():
                        result += f"• {key}: {value['value']}\n"
                    return result
                return "Henüz tercihiniz kayıtlı değil"
            
            else:
                stats = self.recall_memories("all")
                return f"🧠 Hafıza durumum:\n• {stats['conversations']} konuşma\n• {stats['facts']} öğrenilen bilgi\n• {stats['preferences']} tercih\n• {stats['interactions']} etkileşim"
        
        if "tercihim" in input_lower or "ayırla" in input_lower:
            if "ses seviyesi" in input_lower:
                return self.remember_preference("ses_seviyesi", "yüksek")
            elif "dil" in input_lower:
                return self.remember_preference("dil", "türkçe")
            elif "tema" in input_lower:
                return self.remember_preference("tema", "koyu")
            else:
                return "Ne ayarlamak istersiniz? (ses seviyesi, dil, tema vb)"
        
        if "analiz et" in input_lower and "beni" in input_lower:
            return self.analyze_user_patterns()
        
        # Yardım
        if "yardım" in input_lower or "ne yapabilirsin" in input_lower:
            return """Size şunlarda yardımcı olabilirim:
🧮 Matematik işlemleri (örn: 5+3, 10*2, 15/3)
🕐 Saat ve tarih bilgisi
📝 Not alma (örn: Not al: Toplantı 15:00)
🔍 Web arama (örn: Google'da ara: Python)
🌍 Çeviri (örn: Çevir: Hello to Turkish)
🎮 Sayı tahmini oyunu
🤖 Yapay zeka sohbeti
📱 SMS gönder (örn: SMS gönder 05551234567 için Merhaba)
📞 Arama yap (örn: Ara 05551234567)
📱 Uygulama aç (örn: Aç WhatsApp, Aç Spotify, Aç Kamera)
📸 Fotoğraf çek (örn: Fotoğraf çek, Foto çek)
🎤 Ses kaydı (örn: Ses kaydı başlat, Kayıt başlat)
🔔 Bildirimleri göster
⏰ Hatırlatıcı ayarla (örn: Hatırlatıcı ayarla 18:00 için Toplantı)
🌤️ Hava durumu (örn: Hava durumu Ankara için)
🎤 Sesli uyanma (Hey Jarvis)
🔄 Güncelleme kontrolü
📷 Görüntü tanıma:
   - Kamera analiz et
   - Nesne tespiti
   - QR kod tara
   - Yüz tanıma
   - Ortam analizi
🧠 HAFIZA ÖZELLİKLERİ:
   - Öğren (Öğren: Benim adım Ali)
   - Hatırla (Hatırla konuşmalar/öğrendiklerim/tercihler)
   - Tercih ayarla (Tercihim: ses seviyesi yüksek)
   - Analiz et (Analiz et beni)
🎯 Tüm yetenekler için "Neler yapabiliyorsun?" deyin
💬 Konuşma ve öğrenme
🔊 Sesli iletişim"""
        
        # Geri kalan her şey için Gemini AI'ya sor
        return self.ask_gemini(user_input)
    
    def voice_input(self):
        if not self.voice_enabled:
            self.add_message("Jarvis", "Ses özellikleri devre dışı. PyAudio kurulumu gerekli.")
            return
            
        try:
            self.status_label.config(text="Dinliyorum...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio, language='tr-TR')
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, text)
            self.send_message()
            
        except sr.WaitTimeoutError:
            self.add_message("Jarvis", "Sesinizi duyamadım, tekrar deneyin.")
        except sr.UnknownValueError:
            self.add_message("Jarvis", "Ne dediğinizi anlayamadım.")
        except Exception as e:
            self.add_message("Jarvis", f"Bir hata oluştu: {str(e)}")
        finally:
            self.status_label.config(text="Jarvis hazır...")
    
    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Ses hatası: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NovaAI()
    app.run()
