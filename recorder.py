import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import threading
import datetime
import os

class StreamEntry:
    def __init__(self, parent, row):
        self.rtsp_var = tk.StringVar()
        self.fps_var = tk.StringVar(value="Check")
        self.max_fps = 1
        self.selected_fps = tk.IntVar(value=1)
        self.recording = False
        self.thread = None
        self.display_var = tk.BooleanVar(value=False)  # New: for display checkbox

        self.rtsp_entry = tk.Entry(parent, textvariable=self.rtsp_var, width=50)
        self.rtsp_entry.grid(row=row, column=0, padx=5, pady=5)

        self.check_btn = tk.Button(parent, text="Check", command=self.check_fps)
        self.check_btn.grid(row=row, column=1, padx=5)

        self.fps_dropdown = ttk.Combobox(parent, textvariable=self.selected_fps, state="readonly", width=5)
        self.fps_dropdown['values'] = [1]
        self.fps_dropdown.grid(row=row, column=2, padx=5)

        self.start_btn = tk.Button(parent, text="Start", command=self.toggle_recording, state="disabled")
        self.start_btn.grid(row=row, column=3, padx=5)

        self.display_cb = tk.Checkbutton(parent, text="Display", variable=self.display_var)
        self.display_cb.grid(row=row, column=4, padx=5)  # New: Display checkbox

    def check_fps(self):
        rtsp_url = self.rtsp_var.get()
        if not rtsp_url:
            messagebox.showerror("Error", "Please enter RTSP link.")
            return
        cap = cv2.VideoCapture(rtsp_url)
        # Timeout logic
        start_time = datetime.datetime.now()
        while not cap.isOpened():
            if (datetime.datetime.now() - start_time).total_seconds() > 30:
                messagebox.showerror("Error", "Cannot open stream (timeout after 30 seconds).")
                return
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or fps > 120:
            # fallback: estimate fps
            frame_count = 0
            start = cv2.getTickCount()
            while frame_count < 30:
                ret, _ = cap.read()
                if not ret:
                    break
                frame_count += 1
            end = cv2.getTickCount()
            time = (end - start) / cv2.getTickFrequency()
            fps = frame_count / time if time > 0 else 1
        cap.release()
        self.max_fps = int(fps) if fps > 0 else 1
        self.fps_dropdown['values'] = list(range(1, self.max_fps + 1))
        self.selected_fps.set(self.max_fps)
        self.start_btn.config(state="normal")
        messagebox.showinfo("FPS Checked", f"Max FPS: {self.max_fps}")

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.start_btn.config(text="Stop")
            self.thread = threading.Thread(target=self.record_stream)
            self.thread.start()
        else:
            self.recording = False
            self.start_btn.config(text="Start")

    def record_stream(self):
        rtsp_url = self.rtsp_var.get()
        fps = self.selected_fps.get()
        cap = cv2.VideoCapture(rtsp_url)
        # Timeout logic
        start_time = datetime.datetime.now()
        while not cap.isOpened():
            if (datetime.datetime.now() - start_time).total_seconds() > 30:
                messagebox.showerror("Error", "Cannot open stream for recording (timeout after 30 seconds).")
                self.recording = False
                self.start_btn.config(text="Start")
                return
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        stream_name = rtsp_url.split('/')[-1].split('?')[0] or "stream"
        dt_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dt_str}_{stream_name}.mp4"
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        frame_interval = int(round(self.max_fps / fps)) if self.max_fps > fps else 1
        frame_count = 0
        display = self.display_var.get()
        window_name = f"Stream: {stream_name}"
        while self.recording:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                out.write(frame)
                if display:
                    cv2.imshow(window_name, frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.recording = False
                        break
            frame_count += 1
        cap.release()
        out.release()
        if display:
            cv2.destroyWindow(window_name)
        self.start_btn.config(text="Start")
        self.recording = False
        messagebox.showinfo("Recording stopped", f"Saved to {filename}")

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RTSP Recorder")
        self.entries = []
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)
        self.add_entry_btn = tk.Button(root, text="Add RTSP Link", command=self.add_entry)
        self.add_entry_btn.pack(pady=5)
        self.add_entry()  # Add first entry

    def add_entry(self):
        row = len(self.entries)
        entry = StreamEntry(self.frame, row)
        self.entries.append(entry)

if __name__ == "__main__":
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()