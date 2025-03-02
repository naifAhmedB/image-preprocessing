import os
import shutil
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def split_dataset(images_folder, labels_folder, output_folder, train_ratio):
    # Create the output structure:
    # output_folder/
    #    images/
    #         train/
    #         val/
    #    labels/
    #         train/
    #         val/
    output_images_folder = os.path.join(output_folder, "images")
    output_labels_folder = os.path.join(output_folder, "labels")
    
    os.makedirs(os.path.join(output_images_folder, "train"), exist_ok=True)
    os.makedirs(os.path.join(output_images_folder, "val"), exist_ok=True)
    os.makedirs(os.path.join(output_labels_folder, "train"), exist_ok=True)
    os.makedirs(os.path.join(output_labels_folder, "val"), exist_ok=True)

    # Get all image files (assuming .png files; update extension if needed)
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(".png")]
    if not image_files:
        messagebox.showerror("Error", "No image files found in the images folder!")
        return
    random.shuffle(image_files)
    
    # Calculate the number of training images
    train_size = int(len(image_files) * train_ratio)
    train_images = image_files[:train_size]
    val_images = image_files[train_size:]
    
    # Move training images and corresponding labels
    for img in train_images:
        src_img = os.path.join(images_folder, img)
        dest_img = os.path.join(output_images_folder, "train", img)
        shutil.move(src_img, dest_img)
        
        label_filename = img.replace(".png", ".txt")
        src_label = os.path.join(labels_folder, label_filename)
        if os.path.exists(src_label):
            dest_label = os.path.join(output_labels_folder, "train", label_filename)
            shutil.move(src_label, dest_label)
    
    # Move validation images and corresponding labels
    for img in val_images:
        src_img = os.path.join(images_folder, img)
        dest_img = os.path.join(output_images_folder, "val", img)
        shutil.move(src_img, dest_img)
        
        label_filename = img.replace(".png", ".txt")
        src_label = os.path.join(labels_folder, label_filename)
        if os.path.exists(src_label):
            dest_label = os.path.join(output_labels_folder, "val", label_filename)
            shutil.move(src_label, dest_label)
    
    messagebox.showinfo("Success", "Dataset split completed!")

def select_images_folder():
    folder = filedialog.askdirectory(title="Select Images Folder")
    if folder:
        images_folder_var.set(folder)

def select_labels_folder():
    folder = filedialog.askdirectory(title="Select Labels Folder")
    if folder:
        labels_folder_var.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_folder_var.set(folder)

def start_split():
    images_folder = images_folder_var.get()
    labels_folder = labels_folder_var.get()
    output_folder = output_folder_var.get()
    train_ratio_str = train_ratio_var.get()  # e.g., "80%"
    
    if not images_folder or not labels_folder or not output_folder:
        messagebox.showerror("Error", "Please select all required folders.")
        return
    
    # Convert the training ratio from percentage string to a decimal value
    try:
        train_ratio_decimal = int(train_ratio_str.replace("%", "")) / 100.0
    except ValueError:
        messagebox.showerror("Error", "Invalid training ratio selected.")
        return
    
    split_dataset(images_folder, labels_folder, output_folder, train_ratio_decimal)

# Create main Tkinter window
root = tk.Tk()
root.title("Dataset Splitter")
root.geometry("600x250")

# Tkinter StringVars to hold folder paths and training ratio
images_folder_var = tk.StringVar()
labels_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
train_ratio_var = tk.StringVar(value="80%")  # Default to 80%

# Layout UI components
tk.Label(root, text="Images Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=images_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_images_folder).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Labels Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=labels_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_labels_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Output Folder:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2, padx=5, pady=5)

tk.Label(root, text="Training Ratio:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
# Options for training ratio as percentage from 10% to 90%
train_ratio_options = [f"{i}%" for i in range(10, 100, 10)]
train_ratio_combo = ttk.Combobox(root, textvariable=train_ratio_var, values=train_ratio_options, state="readonly", width=10)
train_ratio_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

tk.Button(root, text="Split Dataset", command=start_split, width=20).grid(row=4, column=1, pady=20)

root.mainloop()
