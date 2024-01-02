import tkinter as tk
from tkinter import messagebox
import pyaudio
import audioop
import winsound
import time
import threading

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESHOLD = 20000
VOLUME_FLOOR = 1000
DISPLAY_VOLUME = False

class AudioMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Monitor")
        self.running = False
        self.audio = pyaudio.PyAudio()
        self.average_volume = 0

        # UI Elements
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack()

        self.status_label = tk.Label(root, text="Status: Not running")
        self.status_label.pack()

        self.volume_label = tk.Label(root, text="Average Speaking Volume: 0")
        self.volume_label.pack()

    def update_volume_label(self):
        self.volume_label.config(text=f"Average Speaking Volume: {round(self.average_volume, 2)}")
        if self.running:
            self.root.after(1000, self.update_volume_label)  # Update label every second

    def start_monitoring(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")
        threading.Thread(target=self.monitor).start()
        self.update_volume_label()  # Start updating the volume label

    def stop_monitoring(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Not running")

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

                if rms > THRESHOLD:
                    winsound.Beep(1000, 250)

                if rms > VOLUME_FLOOR:
                    total_volume += rms
                    speaking_chunks += 1
                    self.average_volume = total_volume / speaking_chunks if speaking_chunks else 0

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            stream.stop_stream()
            stream.close()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.running = False
            self.audio.terminate()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
