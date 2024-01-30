import tkinter as tk
import customtkinter as ctk
import pyaudio
import audioop
import winsound
import threading
import time

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
VOLUME_FLOOR = 1000
DISPLAY_VOLUME = False

class AudioMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Audio Monitor")
        self.running = False
        self.audio = pyaudio.PyAudio()
        self.average_volume = 0
        self.threshold = 20000  # Default threshold
        self.threshold_log = []

        self.background_frame = ctk.CTkFrame(self, bg_color="#333333")
        self.background_frame.pack(fill="both", expand=True)

        self.app_frame = ctk.CTkFrame(self.background_frame, bg_color="#333333")
        self.app_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.controls_frame = ctk.CTkFrame(self.app_frame)
        self.controls_frame.pack(side='left', fill='both', expand=True)

        self.log_frame = ctk.CTkFrame(self.app_frame)
        self.log_frame.pack(side='right', fill='both', expand=True)

        # UI Elements
        self.start_button = ctk.CTkButton(self.controls_frame, text="Start", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.threshold_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=30000, command=self.update_threshold_from_slider)
        self.threshold_slider.set(self.threshold)
        self.threshold_slider.pack()

        self.threshold_entry = ctk.CTkEntry(self.controls_frame)
        self.threshold_entry.insert(0, str(self.threshold))
        self.threshold_entry.bind("<Return>", self.update_threshold_from_entry)
        self.threshold_entry.pack()

        self.volume_label = ctk.CTkLabel(self.controls_frame, text="Average Speaking Volume: 0")
        self.volume_label.pack()

        self.log_listbox = tk.Listbox(self.log_frame, height=5, bg="#333333")
        self.log_listbox.pack(pady=10, padx=10, fill="both", expand=True)

    def update_volume_label(self):
        self.volume_label.configure(text=f"Average Speaking Volume: {round(self.average_volume, 2)}")
        if self.running:
            self.after(1000, self.update_volume_label)

    def update_threshold_from_slider(self, val):
        self.threshold = int(val)
        self.threshold_entry.delete(0, ctk.END)
        self.threshold_entry.insert(0, str(self.threshold))

    def update_threshold_from_entry(self, event):
        try:
            self.threshold = int(self.threshold_entry.get())
            self.threshold_slider.set(self.threshold)
        except ValueError:
            ctk.messagebox.showerror("Error", "Please enter a valid integer for the threshold.")

    def update_log_listbox(self):
        self.log_listbox.delete(0, ctk.END)
        for log_entry in self.threshold_log:
            self.log_listbox.insert(ctk.END, log_entry)

    def start_monitoring(self):
        self.running = True
        self.start_button.configure(state="disabled", text = "Stop", text_color = "white")
        threading.Thread(target=self.monitor).start()
        self.update_volume_label()

    def stop_monitoring(self):
        self.running = False
        self.start_button.configure(state="normal")

    def monitor(self):
        device_index = 3
        stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=device_index)

        total_volume = 0
        speaking_chunks = 0

        try:
            while self.running:
                data = stream.read(CHUNK)
                rms = audioop.rms(data, 2)

                if DISPLAY_VOLUME:
                    print("Volume:", rms)

                if rms > self.threshold:
                    difference = rms - self.threshold
                    percent = (difference / self.threshold) * 100
                    timestamp = time.strftime("%H:%M:%S")
                    log_entry = f"{timestamp} - {round(percent, 1)}%"
                    self.threshold_log.append(log_entry)
                    self.threshold_log = self.threshold_log[-5:]
                    self.after(0, self.update_log_listbox)

                    winsound.Beep(1000, 250)

                if rms > VOLUME_FLOOR:
                    total_volume += rms
                    speaking_chunks += 1
                    self.average_volume = total_volume / speaking_chunks if speaking_chunks else 0

        except Exception as e:
            ctk.messagebox.showerror("Error", str(e))
        finally:
            stream.stop_stream()
            stream.close()

    def on_closing(self):
        self.running = False
        self.audio.terminate()
        self.destroy()

if __name__ == "__main__":
    app = AudioMonitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()