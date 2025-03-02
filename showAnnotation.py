import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox

def draw_annotations(image_folder, annotation_folder, output_folder, result_option):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    images = []
    for image_filename in os.listdir(image_folder):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_filename)
            annotation_path = os.path.join(annotation_folder, os.path.splitext(image_filename)[0] + '.txt')
            
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                continue
            height, width, _ = image.shape

            # If an annotation file exists, draw the boxes
            if os.path.exists(annotation_path):
                with open(annotation_path, 'r') as file:
                    annotations = file.readlines()

                for annotation in annotations:
                    # YOLO format: class_id center_x center_y width height (all normalized)
                    class_id, center_x, center_y, box_width, box_height = map(float, annotation.split())

                    # Convert normalized coordinates to absolute pixel values
                    x1 = int((center_x - box_width / 2) * width)
                    y1 = int((center_y - box_height / 2) * height)
                    x2 = int((center_x + box_width / 2) * width)
                    y2 = int((center_y + box_height / 2) * height)

                    # Draw bounding box and label text on the image
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(image, f'Class {int(class_id)}', (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Save annotated image if user selected "Images" or "Both"
            if result_option in ["Images", "Both"]:
                output_path = os.path.join(output_folder, image_filename)
                cv2.imwrite(output_path, image)
                print(f"Annotated image saved: {output_path}")

            # Collect images for video if user selected "Video" or "Both"
            if result_option in ["Video", "Both"]:
                images.append(image)

    # Create a video from annotated images if requested
    if result_option in ["Video", "Both"]:
        video_output_path = os.path.join(output_folder, 'annotated_video.mp4')
        if images:
            height, width, _ = images[0].shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_output_path, fourcc, 10, (width, height))
            for img in images:
                out.write(img)
            out.release()
            print(f"Annotated video saved: {video_output_path}")

def select_image_folder():
    folder = filedialog.askdirectory(title="Select Image Folder")
    if folder:
        image_folder_var.set(folder)

def select_annotation_folder():
    folder = filedialog.askdirectory(title="Select Annotation Folder")
    if folder:
        annotation_folder_var.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_folder_var.set(folder)

def start_processing():
    image_folder = image_folder_var.get()
    annotation_folder = annotation_folder_var.get()
    output_folder = output_folder_var.get()
    result_option = result_option_var.get()

    if not image_folder or not annotation_folder or not output_folder:
        messagebox.showerror("Error", "Please select all required folders.")
        return

    draw_annotations(image_folder, annotation_folder, output_folder, result_option)
    messagebox.showinfo("Process Completed", "Annotation drawing process completed.")

# Create main Tkinter window
root = tk.Tk()
root.title("Annotation Drawer")
root.geometry("600x250")

# Variables to store folder paths and result option
image_folder_var = tk.StringVar()
annotation_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
result_option_var = tk.StringVar(value="Images")

# Layout configuration
tk.Label(root, text="Image Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=image_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_image_folder).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Annotation Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=annotation_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_annotation_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Output Folder:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2, padx=5, pady=5)

tk.Label(root, text="Result Type:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
result_frame = tk.Frame(root)
result_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
tk.Radiobutton(result_frame, text="Images", variable=result_option_var, value="Images").pack(side="left", padx=5)
tk.Radiobutton(result_frame, text="Video", variable=result_option_var, value="Video").pack(side="left", padx=5)
tk.Radiobutton(result_frame, text="Both", variable=result_option_var, value="Both").pack(side="left", padx=5)

tk.Button(root, text="Process", command=start_processing, width=20).grid(row=4, column=1, pady=20)

root.mainloop()
