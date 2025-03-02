import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox

def flip_image(image):
    # Flip image horizontally
    return cv2.flip(image, 1)

def flip_annotation(annotation_path, image_width):
    flipped_annotations = []
    with open(annotation_path, 'r') as file:
        for line in file:
            # Each line is expected to be: class_id center_x center_y box_width box_height
            class_id, center_x, center_y, box_width, box_height = map(float, line.split())
            # Flip the x-coordinate (assuming normalized coordinates)
            flipped_center_x = 1 - center_x
            flipped_annotations.append(f"{int(class_id)} {flipped_center_x:.6f} {center_y:.6f} {box_width:.6f} {box_height:.6f}\n")
    return flipped_annotations

def process_images_with_flip(image_folder, label_folder, output_folder, prefix='fl_'):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
            # Annotation file is expected to have the same basename with .txt extension
            annotation_filename = os.path.splitext(filename)[0] + '.txt'
            annotation_path = os.path.join(label_folder, annotation_filename)

            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not read image: {image_path}")
                continue
            height, width, _ = image.shape

            # Flip the image
            flipped_image = flip_image(image)
            output_image_filename = prefix + filename
            output_image_path = os.path.join(output_folder, output_image_filename)
            cv2.imwrite(output_image_path, flipped_image)
            print(f"Flipped image saved: {output_image_path}")

            # Process and save flipped annotation file if it exists
            if os.path.exists(annotation_path):
                flipped_annotations = flip_annotation(annotation_path, width)
                output_annotation_filename = prefix + os.path.basename(annotation_path)
                output_annotation_path = os.path.join(output_folder, output_annotation_filename)
                with open(output_annotation_path, 'w') as output_file:
                    output_file.writelines(flipped_annotations)
                print(f"Flipped annotation saved: {output_annotation_path}")

def select_image_folder():
    folder = filedialog.askdirectory(title="Select Image Directory")
    if folder:
        image_folder_var.set(folder)

def select_label_folder():
    folder = filedialog.askdirectory(title="Select Label Directory")
    if folder:
        label_folder_var.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_folder_var.set(folder)

def start_process():
    image_folder = image_folder_var.get()
    label_folder = label_folder_var.get()
    output_folder = output_folder_var.get()

    if not image_folder or not label_folder or not output_folder:
        messagebox.showerror("Error", "Please select all directories: image, label, and output.")
        return

    process_images_with_flip(image_folder, label_folder, output_folder)
    messagebox.showinfo("Process Completed", "All flipped images and labels have been saved.")

# Create main Tkinter window
root = tk.Tk()
root.title("Flip Images & Annotations")
root.geometry("600x200")

# Variables to store directory paths
image_folder_var = tk.StringVar()
label_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()

# Create UI components
tk.Label(root, text="Image Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=image_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_image_folder).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Label Directory:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=label_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_label_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Output Folder:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2, padx=5, pady=5)

tk.Button(root, text="Process", command=start_process, width=20).grid(row=3, column=1, padx=5, pady=20)

root.mainloop()
