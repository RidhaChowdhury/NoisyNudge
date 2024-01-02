import pyaudio
import audioop
import sys
import winsound
import time
import threading
import tkinter as tk
from tkinter import messagebox

# Constants
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sampling rate
CHUNK = 1024  # Buffer size
THRESHOLD = 20000  # Volume threshold for beep
VOLUME_FLOOR = 1000  # Floor volume for considering as speaking
DISPLAY_VOLUME = False  # Set to True to display volume levels

class AudioMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Monitor")
        self.running = False

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # UI Elements
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack()

        self.status_label = tk.Label(root, text="Status: Not running")
        self.status_label.pack()

    def start_monitoring(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")

        # Start monitoring in a separate thread
        threading.Thread(target=self.monitor).start()

    def stop_monitoring(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Not running")

    def monitor(self):
        device_index = 3
        stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                 rate=RATE, input=True,
                                 frames_per_buffer=CHUNK, input_device_index=device_index)

        total_volume = 0
        speaking_chunks = 0

        try:
            while self.running:
                data = stream.read(CHUNK)
                rms = audioop.rms(data, 2)  # Get volume of the input

                if DISPLAY_VOLUME:
                    print("Volume:", rms)

                if rms > THRESHOLD:
                    # prints the percent exceeded the volume threshold and when
                    difference = rms - THRESHOLD
                    percent = (difference / THRESHOLD) * 100
                    print("Volume exceeded by", round(percent, 3), "at", time.strftime("%H:%M:%S"))
                    winsound.Beep(1000, 250)  # Beep at 1000 Hz for 250 ms

                # Update total volume and speaking chunks if above volume floor
                if rms > VOLUME_FLOOR:
                    total_volume += rms
                    speaking_chunks += 1

                    # Calculate and display average volume
                    average_volume = total_volume / speaking_chunks if speaking_chunks else 0
                    print("Average Speaking Volume:", round(average_volume, 2))

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
