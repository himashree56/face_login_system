import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import json
import uuid
import threading
import datetime
import shutil
from pymongo import MongoClient
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["face_recognition_db"]
    users_collection = db["users"]
    print("Connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    pass

CAPTURED_FRAMES_DIR = './captured_frames'
TMP_DIR = './tmp'
ATTENDANCE_DIR = './attendance_logs'
USER_DATA_DIR = './user_data'

os.makedirs(CAPTURED_FRAMES_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)

auth_token = None

USERS_JSON_FILE = os.path.join(USER_DATA_DIR, 'users.json')
if not os.path.exists(USERS_JSON_FILE):
    with open(USERS_JSON_FILE, 'w') as f:
        json.dump([], f)



def load_users_from_json():
    try:
        with open(USERS_JSON_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users from JSON: {e}")
        return []

def save_users_to_json(users):
    try:
        with open(USERS_JSON_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Error saving users to JSON: {e}")

def capture_frame():
    ret, frame = cap.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
        if len(faces) > 0:
            status_label.config(text="Face Detected", fg="green")
        else:
            status_label.config(text="No Face Detected", fg="red")
            
        global current_frame, current_faces
        current_frame = frame.copy()
        current_faces = faces
    
    lbl_video.after(10, capture_frame)

def register_user():
    username = entry_username.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()
    password = entry_password.get().strip()

    if not username or not email or not phone or not password:
        messagebox.showerror("Error", "Please enter all details.")
        return

    if len(current_faces) == 0:
        messagebox.showerror("Error", "No face detected. Please position your face in the camera.")
        return

    user_id = str(uuid.uuid4())
    filepath = os.path.join(CAPTURED_FRAMES_DIR, f'{user_id}.png')
    cv2.imwrite(filepath, current_frame)

    try:
        try:
            existing_user = users_collection.find_one({"username": username})
            if existing_user:
                messagebox.showerror("Error", "Username already exists.")
                return

            user_data = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "phone": phone,
                "password": password,
                "face_image_path": filepath,
                "created_at": datetime.datetime.utcnow(),
            }
            users_collection.insert_one(user_data)
            messagebox.showinfo("Success", "User registered successfully.")
        except NameError:
            users = load_users_from_json()
            
            if any(user["username"] == username for user in users):
                messagebox.showerror("Error", "Username already exists.")
                return
                
            user_data = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "phone": phone,
                "password": password,
                "face_image_path": filepath,
                "created_at": str(datetime.datetime.utcnow()),
            }
            users.append(user_data)
            save_users_to_json(users)
            messagebox.showinfo("Success", "User registered successfully.")
            
        entry_username.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

def login_user():
    global auth_token
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Please enter username and password.")
        return

    if len(current_faces) == 0:
        messagebox.showerror("Error", "No face detected. Please position your face in the camera.")
        return

    try:
        try:
            user = users_collection.find_one({"username": username, "password": password})
            if user:
                auth_token = str(uuid.uuid4())
                messagebox.showinfo("Success", f"Login successful! Welcome {username}.")
                with open(os.path.join(ATTENDANCE_DIR, f"{username}_log.txt"), "a") as lf:
                    lf.write(f"{datetime.datetime.utcnow().isoformat()}Z - LOGIN_OK\n")
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        except NameError:
            users = load_users_from_json()
            user = next((user for user in users if user["username"] == username and user["password"] == password), None)
            if user:
                auth_token = str(uuid.uuid4())
                messagebox.showinfo("Success", f"Login successful! Welcome {username}.")
                with open(os.path.join(ATTENDANCE_DIR, f"{username}_log.txt"), "a") as lf:
                    lf.write(f"{datetime.datetime.utcnow().isoformat()}Z - LOGIN_OK\n")
            else:
                messagebox.showerror("Error", "Invalid username or password.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def logout_user():
    global auth_token
    if auth_token:
        auth_token = None
        messagebox.showinfo("Logout", "You have been logged out.")
    else:
        messagebox.showinfo("Info", "You are not logged in.")

def download_logs():
    if not auth_token:
        messagebox.showerror("Unauthorized", "Please login first.")
        return
    try:
        filename = 'attendance_logs.zip'
        placeholder = os.path.join(ATTENDANCE_DIR, "README.txt")
        if not os.path.exists(placeholder):
            with open(placeholder, "w") as f:
                f.write("Attendance logs for the Face Login system.\n")
        if os.path.exists(filename):
            os.remove(filename)
        shutil.make_archive(filename[:-4], 'zip', ATTENDANCE_DIR)
        messagebox.showinfo("Downloaded", f"Logs saved to: {os.path.abspath(filename)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_closing():
    cap.release()
    root.destroy()



def run_gui():
    global entry_username, entry_email, entry_phone, entry_password, lbl_video, cap, root, status_label, current_frame, current_faces, face_cascade

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    current_frame = None
    current_faces = []

    root = tk.Tk()
    root.title("Face Recognition Login System")

    cap = cv2.VideoCapture(0)

    main_frame = tk.Frame(root)
    main_frame.pack(pady=20)

    video_frame = tk.Frame(main_frame)
    video_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    lbl_video = tk.Label(video_frame)
    lbl_video.pack()

    status_label = tk.Label(video_frame, text="No Face Detected", fg="red")
    status_label.pack(pady=5)

    form_frame = tk.Frame(main_frame)
    form_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    label_username = tk.Label(form_frame, text="Username:")
    label_username.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_username = tk.Entry(form_frame, width=30)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    label_email = tk.Label(form_frame, text="Email:")
    label_email.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_email = tk.Entry(form_frame, width=30)
    entry_email.grid(row=1, column=1, padx=10, pady=5)

    label_phone = tk.Label(form_frame, text="Phone:")
    label_phone.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_phone = tk.Entry(form_frame, width=30)
    entry_phone.grid(row=2, column=1, padx=10, pady=5)

    label_password = tk.Label(form_frame, text="Password:")
    label_password.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_password = tk.Entry(form_frame, width=30, show="*")
    entry_password.grid(row=3, column=1, padx=10, pady=5)

    buttons_frame = tk.Frame(main_frame)
    buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    btn_register = tk.Button(buttons_frame, text="Register", command=register_user, width=15)
    btn_register.grid(row=0, column=0, padx=5, pady=5)

    btn_login = tk.Button(buttons_frame, text="Login", command=login_user, width=15)
    btn_login.grid(row=0, column=1, padx=5, pady=5)

    btn_logout = tk.Button(buttons_frame, text="Logout", command=logout_user, width=15)
    btn_logout.grid(row=1, column=0, padx=5, pady=5)

    btn_logs = tk.Button(buttons_frame, text="Download Logs", command=download_logs, width=15)
    btn_logs.grid(row=1, column=1, padx=5, pady=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    capture_frame()
    
    root.mainloop()
if __name__ == "__main__":
    run_gui()
