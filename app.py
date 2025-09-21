import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import cv2
import os
import face_recognition
import pickle
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, date
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- Setup Folders ----------
os.makedirs("data/students", exist_ok=True)
os.makedirs("encodings", exist_ok=True)
os.makedirs("database", exist_ok=True)

# ---------- Database Setup ----------
conn = sqlite3.connect("database/attendance.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                name TEXT,
                date TEXT,
                time TEXT,
                status TEXT)""")
conn.commit()
conn.close()

# ---------- Helper Functions ----------
def validate_input(name, student_id):
    """Validate student name and ID input"""
    if not name.strip():
        messagebox.showerror("Error", "Please enter a valid name!")
        return False
    if not student_id.strip():
        messagebox.showerror("Error", "Please enter a valid student ID!")
        return False
    if not student_id.isalnum():
        messagebox.showerror("Error", "Student ID should contain only letters and numbers!")
        return False
    return True

def register_student(name, student_id):
    """Register a new student with face capture"""
    if not validate_input(name, student_id):
        return
    
    folder_path = f"data/students/{student_id}_{name}"
    if os.path.exists(folder_path):
        messagebox.showerror("Error", f"Student {student_id} already exists!")
        return
    
    os.makedirs(folder_path, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access camera!")
        return
    
    count = 0
    messagebox.showinfo("Info", "Position your face in the camera and press 'SPACE' to capture (press 'q' to stop)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Add text overlay
        cv2.putText(frame, f"Images captured: {count}/10", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press SPACE to capture, 'q' to quit", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Register Student", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space bar to capture
            cv2.imwrite(f"{folder_path}/{count}.jpg", frame)
            count += 1
            if count >= 10:
                break
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if count > 0:
        messagebox.showinfo("Success", f"Student {name} registered with {count} images!")
    else:
        os.rmdir(folder_path)
        messagebox.showwarning("Warning", "No images captured!")

def encode_faces():
    """Generate face encodings for all registered students"""
    students_dir = "data/students/"
    if not os.path.exists(students_dir) or not os.listdir(students_dir):
        messagebox.showerror("Error", "No students registered yet!")
        return
    
    encodings = {}
    total_students = len(os.listdir(students_dir))
    processed = 0
    
    progress_window = tk.Toplevel()
    progress_window.title("Encoding Faces...")
    progress_window.geometry("300x100")
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(pady=20, padx=20, fill='x')
    progress_label = tk.Label(progress_window, text="Processing...")
    progress_label.pack()
    
    for student_folder in os.listdir(students_dir):
        path = os.path.join(students_dir, student_folder)
        if not os.path.isdir(path):
            continue
            
        images = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        student_name = student_folder
        student_encodings = []
        
        progress_label.config(text=f"Processing {student_name}...")
        progress_window.update()
        
        for img_name in images:
            img_path = os.path.join(path, img_name)
            try:
                img = face_recognition.load_image_file(img_path)
                face_encs = face_recognition.face_encodings(img)
                if face_encs:
                    student_encodings.append(face_encs[0])
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        
        if student_encodings:
            encodings[student_name] = np.mean(student_encodings, axis=0)
        
        processed += 1
        progress_var.set((processed / total_students) * 100)
        progress_window.update()

    with open("encodings/encodings.pkl", "wb") as f:
        pickle.dump(encodings, f)
    
    progress_window.destroy()
    messagebox.showinfo("Success", f"Encodings generated for {len(encodings)} students!")

def mark_attendance():
    """Mark attendance using face recognition"""
    try:
        with open("encodings/encodings.pkl", "rb") as f:
            encodings_dict = pickle.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "No encodings found! Encode faces first.")
        return

    if not encodings_dict:
        messagebox.showerror("Error", "No student encodings available!")
        return

    known_face_names = list(encodings_dict.keys())
    known_face_encodings = list(encodings_dict.values())

    conn = sqlite3.connect("database/attendance.db")
    c = conn.cursor()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access camera!")
        conn.close()
        return
    
    messagebox.showinfo("Info", "Attendance marking started. Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            student_id = ""
            
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                name = known_face_names[best_match_index]
                student_id = name.split("_")[0]

                today = datetime.now().date()
                c.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, str(today)))
                if not c.fetchall():
                    c.execute("INSERT INTO attendance (student_id, name, date, time, status) VALUES (?, ?, ?, ?, ?)",
                              (student_id, name, str(today), str(datetime.now().time())[:8], "Present"))
                    conn.commit()
                    print(f"{name} marked present at {datetime.now().time()}")

            # Scale back up face locations
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw rectangle and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Add instructions on frame
        cv2.putText(frame, "Press 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Attendance System", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()
    messagebox.showinfo("Info", "Attendance marking completed!")

def view_attendance():
    """Display attendance records in a new window"""
    conn = sqlite3.connect("database/attendance.db")
    
    # Get attendance data
    df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC, time DESC", conn)
    conn.close()
    
    if df.empty:
        messagebox.showinfo("Info", "No attendance records found!")
        return
    
    # Create new window
    view_window = tk.Toplevel()
    view_window.title("Attendance Records")
    view_window.geometry("800x600")
    
    # Create treeview
    tree = ttk.Treeview(view_window, columns=('ID', 'Student_ID', 'Name', 'Date', 'Time', 'Status'), show='headings')
    
    # Define headings
    tree.heading('ID', text='ID')
    tree.heading('Student_ID', text='Student ID')
    tree.heading('Name', text='Name')
    tree.heading('Date', text='Date')
    tree.heading('Time', text='Time')
    tree.heading('Status', text='Status')
    
    # Configure column widths
    tree.column('ID', width=50)
    tree.column('Student_ID', width=100)
    tree.column('Name', width=200)
    tree.column('Date', width=100)
    tree.column('Time', width=100)
    tree.column('Status', width=80)
    
    # Insert data
    for index, row in df.iterrows():
        tree.insert('', 'end', values=(row['id'], row['student_id'], row['name'], row['date'], row['time'], row['status']))
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(view_window, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack widgets
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

def export_to_excel():
    """Export attendance data to Excel file"""
    conn = sqlite3.connect("database/attendance.db")
    df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC, time DESC", conn)
    conn.close()
    
    if df.empty:
        messagebox.showinfo("Info", "No attendance records to export!")
        return
    
    try:
        filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"Attendance data exported to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {str(e)}")

def generate_statistics():
    """Generate and display attendance statistics"""
    conn = sqlite3.connect("database/attendance.db")
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()
    
    if df.empty:
        messagebox.showinfo("Info", "No attendance data available!")
        return
    
    # Create statistics window
    stats_window = tk.Toplevel()
    stats_window.title("Attendance Statistics")
    stats_window.geometry("600x400")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Create statistics text
    stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD, width=70, height=20)
    stats_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Calculate statistics
    total_records = len(df)
    unique_students = df['student_id'].nunique()
    date_range = f"{df['date'].min().date()} to {df['date'].max().date()}"
    
    # Daily attendance count
    daily_stats = df.groupby('date').size().describe()
    
    # Student attendance frequency
    student_stats = df.groupby(['student_id', 'name']).size().sort_values(ascending=False)
    
    # Generate report text
    report = f"""
ATTENDANCE STATISTICS REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
Total attendance records: {total_records}
Unique students: {unique_students}
Date range: {date_range}

DAILY ATTENDANCE STATISTICS:
Average daily attendance: {daily_stats['mean']:.2f}
Maximum daily attendance: {daily_stats['max']:.0f}
Minimum daily attendance: {daily_stats['min']:.0f}

STUDENT ATTENDANCE FREQUENCY:
"""
    
    for (student_id, name), count in student_stats.head(10).items():
        report += f"{name} ({student_id}): {count} days\n"
    
    stats_text.insert(tk.END, report)
    stats_text.config(state=tk.DISABLED)

# ---------- Tkinter GUI ----------
root = tk.Tk()
root.title("Face Recognition Attendance Management System")
root.geometry("600x700")
root.configure(bg='#f0f0f0')

# Create style
style = ttk.Style()
style.theme_use('clam')

# Main title
title_frame = tk.Frame(root, bg='#2c3e50', height=80)
title_frame.pack(fill='x', pady=(0, 20))
title_frame.pack_propagate(False)

title_label = tk.Label(title_frame, text="🎓 Attendance Management System", 
                      font=("Arial", 24, "bold"), fg='white', bg='#2c3e50')
title_label.pack(expand=True)

# Main container
main_frame = tk.Frame(root, bg='#f0f0f0')
main_frame.pack(fill='both', expand=True, padx=20)

# Student Registration Section
reg_frame = tk.LabelFrame(main_frame, text="📝 Student Registration", font=("Arial", 14, "bold"), 
                         bg='#f0f0f0', fg='#2c3e50', padx=20, pady=15)
reg_frame.pack(fill='x', pady=(0, 15))

# Entry fields frame
entry_frame = tk.Frame(reg_frame, bg='#f0f0f0')
entry_frame.pack(fill='x', pady=10)

tk.Label(entry_frame, text="Student Name:", font=("Arial", 12), bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
name_entry = tk.Entry(entry_frame, font=("Arial", 12), width=25)
name_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')

tk.Label(entry_frame, text="Student ID:", font=("Arial", 12), bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
id_entry = tk.Entry(entry_frame, font=("Arial", 12), width=25)
id_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='ew')

entry_frame.columnconfigure(1, weight=1)

# Registration button
reg_btn = tk.Button(reg_frame, text="📷 Register New Student", 
                   command=lambda: register_student(name_entry.get(), id_entry.get()),
                   font=("Arial", 12, "bold"), bg='#3498db', fg='white', 
                   padx=20, pady=10, cursor='hand2')
reg_btn.pack(pady=(10, 0))

# System Operations Section
ops_frame = tk.LabelFrame(main_frame, text="⚙️ System Operations", font=("Arial", 14, "bold"), 
                         bg='#f0f0f0', fg='#2c3e50', padx=20, pady=15)
ops_frame.pack(fill='x', pady=(0, 15))

# Buttons frame
btn_frame = tk.Frame(ops_frame, bg='#f0f0f0')
btn_frame.pack(fill='x')

encode_btn = tk.Button(btn_frame, text="🔄 Generate Face Encodings", command=encode_faces,
                      font=("Arial", 11, "bold"), bg='#f39c12', fg='white', 
                      padx=15, pady=8, cursor='hand2')
encode_btn.pack(fill='x', pady=5)

attendance_btn = tk.Button(btn_frame, text="✅ Mark Attendance", command=mark_attendance,
                          font=("Arial", 11, "bold"), bg='#27ae60', fg='white', 
                          padx=15, pady=8, cursor='hand2')
attendance_btn.pack(fill='x', pady=5)

# Reports and Data Section
reports_frame = tk.LabelFrame(main_frame, text="📊 Reports & Data Management", font=("Arial", 14, "bold"), 
                             bg='#f0f0f0', fg='#2c3e50', padx=20, pady=15)
reports_frame.pack(fill='x', pady=(0, 15))

view_btn = tk.Button(reports_frame, text="👀 View Attendance Records", command=view_attendance,
                    font=("Arial", 11, "bold"), bg='#8e44ad', fg='white', 
                    padx=15, pady=8, cursor='hand2')
view_btn.pack(fill='x', pady=5)

stats_btn = tk.Button(reports_frame, text="📈 Generate Statistics", command=generate_statistics,
                     font=("Arial", 11, "bold"), bg='#e74c3c', fg='white', 
                     padx=15, pady=8, cursor='hand2')
stats_btn.pack(fill='x', pady=5)

export_btn = tk.Button(reports_frame, text="📤 Export to Excel", command=export_to_excel,
                      font=("Arial", 11, "bold"), bg='#34495e', fg='white', 
                      padx=15, pady=8, cursor='hand2')
export_btn.pack(fill='x', pady=5)

# Status bar
status_frame = tk.Frame(root, bg='#ecf0f1', height=30)
status_frame.pack(fill='x', side='bottom')
status_frame.pack_propagate(False)

status_label = tk.Label(status_frame, text="Ready | Face Recognition Attendance System", 
                       font=("Arial", 10), bg='#ecf0f1', fg='#7f8c8d')
status_label.pack(side='left', padx=10, pady=5)

# Instructions
instructions_frame = tk.LabelFrame(main_frame, text="📋 Quick Instructions", font=("Arial", 12, "bold"), 
                                  bg='#f0f0f0', fg='#2c3e50', padx=15, pady=10)
instructions_frame.pack(fill='x')

instructions_text = """
1. Register students by entering their name and ID, then capturing face images
2. Generate face encodings after registering all students
3. Use 'Mark Attendance' to start face recognition for attendance marking
4. View records, generate statistics, and export data using the report functions
"""

instructions_label = tk.Label(instructions_frame, text=instructions_text, 
                             font=("Arial", 10), bg='#f0f0f0', fg='#555555', 
                             justify='left', wraplength=500)
instructions_label.pack(anchor='w')

root.mainloop()
