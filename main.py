import cv2
import face_recognition
import pandas as pd
import numpy as np
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, Scrollbar, Frame

# Directory containing known face images
known_faces_dir = r"images"

def load_known_faces(directory):
    known_faces = []
    known_names = []
    for filename in os.listdir(directory):
        if filename.endswith(('.jpg', '.png')):
            image = face_recognition.load_image_file(os.path.join(directory, filename))
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces.append(encodings[0])
                known_names.append(filename.split('.')[0])
    return np.array(known_faces), known_names

def capture_image():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Error", "Camera could not be opened.")
        return None
    ret, frame = cam.read()
    cam.release()
    cv2.destroyAllWindows()
    return frame if ret else None

def recognize_face(captured_image, known_faces, known_names):
    face_encodings = face_recognition.face_encodings(captured_image)
    if not face_encodings:
        messagebox.showinfo("Info", "No faces detected in the image.")
        return None
    captured_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_faces, captured_encoding)
    if True in matches:
        first_match_index = matches.index(True)
        return known_names[first_match_index]
    return None

def mark_attendance(student_name, file='attendance.xlsx'):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    try:
        df = pd.read_excel(file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
    df = pd.concat([df, new_record_df], ignore_index=True)
    df.to_excel(file, index=False)

def reset_attendance(file='attendance.xlsx'):
    if os.path.exists(file):
        os.remove(file)
        messagebox.showinfo("Success", "Attendance records have been reset.")
    else:
        messagebox.showinfo("Info", "No attendance records found to reset.")

def show_attendance_records():
    records_window = Toplevel(root)
    records_window.title("Attendance Records")
    records_window.geometry("400x300")
    
    frame = Frame(records_window)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create a scrollbar
    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a canvas for the attendance records
    records_list = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Helvetica", 12))
    records_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar.config(command=records_list.yview)

    # Load attendance records
    try:
        df = pd.read_excel('attendance.xlsx')
        for index, row in df.iterrows():
            records_list.insert(tk.END, f"{row['Name']} - {row['Date']} - {row['Time']}")
    except FileNotFoundError:
        records_list.insert(tk.END, "No attendance records found.")

def run_attendance_system():
    known_faces, known_names = load_known_faces(known_faces_dir)
    if known_faces.size == 0:
        messagebox.showerror("Error", "No known faces found.")
        return
    
    image = capture_image()
    if image is None:
        return

    student_name = recognize_face(image, known_faces, known_names)
    if student_name is None:
        messagebox.showinfo("Info", "Student not recognized!")
        return
    mark_attendance(student_name)
    messagebox.showinfo("Success", f"Attendance marked for {student_name}")

# Set up the GUI
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Style Configuration
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14), padding=10)
style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
style.configure("TFrame", background="#f0f0f0")

# Title Label
title_label = ttk.Label(root, text="Attendance System", font=("Helvetica", 16, "bold"))
title_label.pack(pady=20)

# Start Button
start_button = ttk.Button(root, text="Start Attendance", command=run_attendance_system)
start_button.pack(pady=10)

# View Records Button
view_records_button = ttk.Button(root, text="View Attendance Records", command=show_attendance_records)
view_records_button.pack(pady=10)

# Reset Attendance Button
reset_button = ttk.Button(root, text="Reset Attendance", command=lambda: reset_attendance())
reset_button.pack(pady=10)

# Exit Button
exit_button = ttk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Run the main loop
root.mainloop()
