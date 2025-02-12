import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import pyaudio
import numpy as np
from ttkbootstrap import Style
from pydub import AudioSegment
from pydub.utils import make_chunks
import io
import ffmpeg

class InternetRadioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("PyFM Radio - مصر")
        self.root.geometry("700x500")
        
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        self.volume = 1.0
        self.volume_lock = threading.Lock()
        
        self.stations = {
            "نجوم FM": "https://stream.radio.co/sd6b891a3a/listen",
            "ON Sport": "https://onplayer.live/radio/8030/radio.mp3",
            "راديو 90.90": "https://stream.radio.co/sa49a4be8a/listen",
            "Nile FM": "http://nilefm.out.airtime.pro:8000/nilefm_a",
            "راديو مصر": "http://radio.maspero.eg:8000/radiomasr",
            "راديو هيتس": "http://radiohits.out.airtime.pro:8000/radiohits_a",
            "راديو معاك": "http://radio.media.gov.eg:8000/RadioMakk.mp3",
            "BBC Radio 1": "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one",
            "Radio Paradise": "http://stream.radioparadise.com/flac",
            "France Inter": "http://direct.franceinter.fr/live/franceinter-midfi.mp3"
        }
        
        self.style = Style(theme="minty")
        self.create_widgets()
        
    def create_widgets(self):
        list_frame = ttk.Frame(self.root)
        list_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.station_list = tk.Listbox(
            list_frame, 
            font=('Arial', 12),
            bg='white',
            selectbackground='#e0e0e0'
        )
        self.station_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for station in self.stations:
            self.station_list.insert(tk.END, station)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.station_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.station_list.yview)

        controls = ttk.Frame(self.root)
        controls.pack(pady=20)

        self.play_btn = ttk.Button(
            controls, 
            text="▶ تشغيل",
            command=self.play_pause
        )
        self.play_btn.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            controls, 
            text="⏹ إيقاف",
            command=self.stop
        ).pack(side=tk.LEFT, padx=10)

        vol_frame = ttk.Frame(self.root)
        vol_frame.pack(pady=10)

        ttk.Label(vol_frame, text="الصوت:").pack(side=tk.LEFT)

        self.volume_slider = ttk.Scale(
            vol_frame,
            from_=0,
            to=1,
            value=1,
            command=self.set_volume
        )
        self.volume_slider.pack(side=tk.LEFT, padx=10)

        self.status_bar = ttk.Label(
            self.root,
            text="جاهز",
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def play_pause(self):
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def play(self):
        try:
            selected = self.station_list.get(tk.ACTIVE)
            url = self.stations[selected]
            
            self.stop()
            
            self.stream_thread = threading.Thread(
                target=self.stream_audio, 
                args=(url,)
            )
            self.stream_thread.start()
            
            self.play_btn.config(text="⏸ إيقاف مؤقت")
            self.is_playing = True
            self.status_bar.config(text=f"تشغيل: {selected}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر التشغيل: {str(e)}")
            
    def stream_audio(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            session = requests.Session()
            response = session.get(url, headers=headers, stream=True, timeout=15)
            
            if response.status_code != 200:
                messagebox.showerror("خطأ", "تعذر الاتصال بالمحطة")
                return

            audio_stream = io.BytesIO()
            for chunk in response.iter_content(chunk_size=1024*4):
                if not self.is_playing:
                    break
                audio_stream.write(chunk)
                
            audio_stream.seek(0)
            
            audio = AudioSegment.from_file(audio_stream)
            audio = audio.set_frame_rate(44100).set_channels(2)
            
            self.stream = self.p.open(
                format=self.p.get_format_from_width(audio.sample_width),
                channels=audio.channels,
                rate=audio.frame_rate,
                output=True
            )
            
            for chunk in make_chunks(audio, 100):
                if not self.is_playing:
                    break
                
                with self.volume_lock:
                    adjusted_chunk = chunk.apply_gain(self.volume * 30 - 30)
                    
                self.stream.write(adjusted_chunk.raw_data)
                
        except Exception as e:
            messagebox.showerror("خطأ", f"انقطع البث: {str(e)}")
            
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.is_playing = False

    def stop(self):
        self.is_playing = False
        self.play_btn.config(text="▶ تشغيل")
        self.status_bar.config(text="متوقف")
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def set_volume(self, val):
        with self.volume_lock:
            self.volume = float(val)

if __name__ == "__main__":
    root = tk.Tk()
    app = InternetRadioPlayer(root)
    root.mainloop()