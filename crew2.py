"""
Auto Keyboard Presser
Made by Talha
Enhanced with modern UI and additional features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import time
import threading
from tkinter.scrolledtext import ScrolledText

class AutoKeyboardPresser:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Keyboard Presser PRO - Made by Talha")
        self.root.geometry("800x650")
        style = ttk.Style()
        style.theme_use('clam')

        self.recorded_keys = []
        self.recording = False
        self.playing = False
        self.hotkey_start = "F8"
        self.hotkey_play = "F9"
        self.hotkey_stop = "F10"

        self.setup_ui()
        self.bind_hotkeys()

    def setup_ui(self):
        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)

        # Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(header_frame, text="Auto Keyboard Presser PRO", font=('Helvetica', 16, 'bold'), 
                 foreground="#2c3e50").pack(pady=5)
        ttk.Label(header_frame, text="Record and replay keyboard sequences with ease", 
                 font=('Helvetica', 10), foreground="#7f8c8d").pack()

        # Hotkey Panel
        hotkey_frame = ttk.LabelFrame(self.root, text=" Hotkeys ", padding=10)
        hotkey_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        hotkey_text = (f"• Start/Stop Recording: {self.hotkey_start}\n"
                       f"• Play Recorded Sequence: {self.hotkey_play}\n"
                       f"• Emergency Stop: {self.hotkey_stop}")
        ttk.Label(hotkey_frame, text=hotkey_text, font=('Helvetica', 10)).pack(anchor="w")

        # Controls Frame
        controls_frame = ttk.Frame(self.root)
        controls_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.record_btn = ttk.Button(controls_frame, text="▶ Start Recording", command=self.toggle_recording)
        self.play_btn = ttk.Button(controls_frame, text="⏯ Play", command=self.play_keys)
        self.stop_btn = ttk.Button(controls_frame, text="⏹ Stop", command=self.stop_playing)
        self.clear_btn = ttk.Button(controls_frame, text="❌ Clear All", command=self.clear_keys)
        
        self.record_btn.pack(side='left', padx=5)
        self.play_btn.pack(side='left', padx=5)
        self.stop_btn.pack(side='left', padx=5)
        self.clear_btn.pack(side='left', padx=5)

        # Settings Frame
        settings_frame = ttk.Frame(self.root)
        settings_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Label(settings_frame, text="Delay (sec):").pack(side='left')
        self.delay_entry = ttk.Entry(settings_frame, width=8)
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.pack(side='left', padx=5)
        
        ttk.Label(settings_frame, text="Repeats:").pack(side='left', padx=10)
        self.repeat_spin = ttk.Spinbox(settings_frame, from_=1, to=999, width=5)
        self.repeat_spin.set(1)
        self.repeat_spin.pack(side='left')
        
        self.infinite_var = tk.BooleanVar()
        self.infinite_check = ttk.Checkbutton(settings_frame, text="Infinite", variable=self.infinite_var)
        self.infinite_check.pack(side='left', padx=5)

        # Sequence List
        list_frame = ttk.LabelFrame(self.root, text=" Recorded Sequence ", padding=10)
        list_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        
        self.tree = ttk.Treeview(list_frame, columns=("Order", "Key", "Time"), show="headings", height=8)
        self.tree.heading("Order", text="Order")
        self.tree.heading("Key", text="Key")
        self.tree.heading("Time", text="Time (s)")
        self.tree.column("Order", width=60, anchor='center')
        self.tree.column("Key", width=120, anchor='center')
        self.tree.column("Time", width=120, anchor='center')
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Status Bar
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        
        self.status_label = ttk.Label(status_frame, text="Status: Ready", font=('Helvetica', 10))
        self.status_label.pack(side='left', anchor='w')
        
        self.progress = ttk.Progressbar(status_frame, orient='horizontal', mode='determinate')
        self.progress.pack(side='right', fill='x', expand=True)
        self.progress.pack_forget()

    def bind_hotkeys(self):
        keyboard.add_hotkey(self.hotkey_start, self.toggle_recording)
        keyboard.add_hotkey(self.hotkey_play, self.play_keys)
        keyboard.add_hotkey(self.hotkey_stop, self.stop_playing)

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recorded_keys = []
        self.recording = True
        self.status_label.config(text="Status: Recording...", foreground="#e74c3c")
        self.record_btn.config(text="⏹ Stop Recording")
        self.start_time = time.time()
        keyboard.start_recording()

    def stop_recording(self):
        self.recording = False
        recorded_events = keyboard.stop_recording()
        self.record_btn.config(text="▶ Start Recording")
        self.status_label.config(text="Status: Recording Stopped", foreground="#2ecc71")
        
        self.recorded_keys = [e for e in recorded_events if e.name != self.hotkey_start.lower()]
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for idx, event in enumerate(self.recorded_keys):
            time_offset = round(event.time - self.start_time, 2)
            self.tree.insert("", "end", values=(idx+1, event.name, time_offset))

    def play_keys(self):
        if not self.recorded_keys:
            messagebox.showerror("Error", "No keys recorded! Record a sequence first.")
            return
        
        try:
            delay = float(self.delay_entry.get())
            if delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid delay value. Please enter a positive number.")
            return

        self.playing = True
        self.progress.pack(side='right', fill='x', expand=True)
        self.status_label.config(text="Status: Playing...", foreground="#3498db")
        threading.Thread(target=self.playback_thread, daemon=True).start()

    def playback_thread(self):
        total_keys = len(self.recorded_keys)
        repeats = 9999 if self.infinite_var.get() else int(self.repeat_spin.get())
        total_actions = total_keys * repeats
        
        if self.infinite_var.get():
            self.progress.config(mode='indeterminate')
            self.progress.start()
        else:
            self.progress.config(mode='determinate', maximum=total_actions)
            self.progress['value'] = 0

        try:
            for _ in range(repeats):
                if not self.playing:
                    break
                for idx, event in enumerate(self.recorded_keys):
                    if not self.playing:
                        break
                    keyboard.press(event.name)
                    time.sleep(0.1)
                    keyboard.release(event.name)
                    time.sleep(float(self.delay_entry.get()))
                    if not self.infinite_var.get():
                        self.progress['value'] += 1
        finally:
            self.playing = False
            self.progress.stop()
            self.progress.pack_forget()
            self.status_label.config(text="Status: Ready", foreground="#2ecc71")

    def stop_playing(self):
        self.playing = False
        self.status_label.config(text="Status: Stopped by User", foreground="#e67e22")

    def clear_keys(self):
        self.recorded_keys = []
        self.refresh_tree()
        self.status_label.config(text="Status: Sequence Cleared", foreground="#e67e22")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoKeyboardPresser(root)
    root.mainloop()