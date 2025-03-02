import cv2
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

def process_video(video_path, save_frame, target_width, target_height):
    # Open video stream
    cap = cv2.VideoCapture(video_path)

    # Get frames per second (FPS)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f'Frames per second (FPS): {fps}')

    # Extract video name for output directory
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = f'{video_name}_frames'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_count = 0
    image_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    progress_bar['maximum'] = total_frames

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        progress_bar['value'] = frame_count
        root.update_idletasks()

        # Resize the frame if its size doesn't match the selected dimensions
        if target_width > 0 and target_height > 0:
            if frame.shape[1] != target_width or frame.shape[0] != target_height:
                frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

        # Save the frame every 'save_frame' frames
        if frame_count % save_frame == 0:
            image_filename = os.path.join(output_dir, f'{video_name}_frame_{image_count:04d}.png')
            cv2.imwrite(image_filename, frame)
            print(f'Stored {image_filename}')
            image_count += 1

    cap.release()
    cv2.destroyAllWindows()

    messagebox.showinfo("Process Completed", f"Frames saved to: {os.path.abspath(output_dir)}")

def select_video():
    video_path = filedialog.askopenfilename(title="Select Video File", 
                                            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
    if video_path:
        video_path_var.set(video_path)

        # Get FPS and update label
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        
        fps_label.config(text=f"Frames per second (FPS): {fps}")

def start_process():
    video_path = video_path_var.get()
    save_frame = int(frame_interval_var.get())

    # Validate width and height inputs
    try:
        target_width = int(width_var.get())
        target_height = int(height_var.get())
        if target_width <= 0 or target_height <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive integers for width and height.")
        return

    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return

    process_video(video_path, save_frame, target_width, target_height)

# Create main window
root = tk.Tk()
root.title("Video Frame Extractor")
root.geometry("400x400")

video_path_var = tk.StringVar()
frame_interval_var = tk.StringVar(value="30")
# Set default image size to 640x640 for YOLOv8
width_var = tk.StringVar(value="640")
height_var = tk.StringVar(value="640")

# Video Selection
video_label = tk.Label(root, text="Select Video File:")
video_label.pack(pady=5)
video_button = tk.Button(root, text="Browse", command=select_video)
video_button.pack()

video_entry = tk.Entry(root, textvariable=video_path_var, width=50)
video_entry.pack()

# FPS Display Label
fps_label = tk.Label(root, text="Frames per second (FPS): -", font=("Arial", 10, "bold"))
fps_label.pack(pady=5)

# Frame Interval Dropdown
frame_label = tk.Label(root, text="Select Frame Interval (1-50):")
frame_label.pack(pady=5)
frame_dropdown = ttk.Combobox(root, textvariable=frame_interval_var, values=[str(i) for i in range(1, 51)])
frame_dropdown.pack()

# Image Size Entry
size_label = tk.Label(root, text="Enter Image Size (Width x Height):")
size_label.pack(pady=5)
size_frame = tk.Frame(root)
size_frame.pack()
width_entry = tk.Entry(size_frame, textvariable=width_var, width=10)
width_entry.pack(side=tk.LEFT, padx=5)
height_entry = tk.Entry(size_frame, textvariable=height_var, width=10)
height_entry.pack(side=tk.LEFT, padx=5)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=20)

# Start Button
start_button = tk.Button(root, text="Start", command=start_process)
start_button.pack(pady=10)

root.mainloop()
