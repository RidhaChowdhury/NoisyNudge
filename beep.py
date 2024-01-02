import tkinter as tk
from tkinter import messagebox, Scale, Entry, IntVar
import pyaudio
import audioop
import winsound
import threading

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
VOLUME_FLOOR = 1000
DISPLAY_VOLUME = False

class AudioMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Monitor")
        self.running = False
        self.audio = pyaudio.PyAudio()
        self.average_volume = 0
        self.threshold_value = IntVar()

        # UI Elements
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack()

        self.status_label = tk.Label(root, text="Status: Not running")
        self.status_label.pack()

        self.threshold_slider = Scale(root, from_=0, to=30000, orient=tk.HORIZONTAL, label="Volume Threshold (Slider)", variable=self.threshold_value)
        self.threshold_slider.set(20000)  # Default value
        self.threshold_slider.pack()

        self.threshold_entry = Entry(root, textvariable=self.threshold_value)
        self.threshold_entry.pack()

        self.threshold_value.trace("w", lambda name, index, mode, sv=self.threshold_value: self.update_threshold())

        self.volume_label = tk.Label(root, text="Average Speaking Volume: 0")
        self.volume_label.pack()

    def update_volume_label(self):
        self.volume_label.config(text=f"Average Speaking Volume: {round(self.average_volume, 2)}")
        if self.running:
            self.root.after(1000, self.update_volume_label)

    def update_threshold(self):
        try:
            new_threshold = int(self.threshold_entry.get())
            self.threshold_slider.set(new_threshold)
        except ValueError:
            pass  # Ignore invalid inputs

    def start_monitoring(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")
        threading.Thread(target=self.monitor).start()
        self.update_volume_label()

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

                threshold = self.threshold_slider.get()
                if rms > threshold:
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
