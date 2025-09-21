import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
import cv2
import os
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

c.execute("""CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE,
                name TEXT,
                registered_date TEXT)""")
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
    """Register a new student (manual entry for now)"""
    if not validate_input(name, student_id):
        return
    
    conn = sqlite3.connect("database/attendance.db")
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO students (student_id, name, registered_date) VALUES (?, ?, ?)",
                  (student_id, name, str(datetime.now().date())))
        conn.commit()
        messagebox.showinfo("Success", f"Student {name} (ID: {student_id}) registered successfully!")
        
        # Clear the entry fields
        name_entry.delete(0, tk.END)
        id_entry.delete(0, tk.END)
        
        # Refresh student list
        refresh_student_list()
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Student ID {student_id} already exists!")
    except Exception as e:
        messagebox.showerror("Error", f"Registration failed: {str(e)}")
    finally:
        conn.close()

def manual_attendance():
    """Manual attendance marking window"""
    attendance_window = tk.Toplevel()
    attendance_window.title("Manual Attendance")
    attendance_window.geometry("400x500")
    
    tk.Label(attendance_window, text="Manual Attendance Marking", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    # Get list of students
    conn = sqlite3.connect("database/attendance.db")
    students_df = pd.read_sql_query("SELECT student_id, name FROM students ORDER BY name", conn)
    conn.close()
    
    if students_df.empty:
        tk.Label(attendance_window, text="No students registered yet!", 
                font=("Arial", 12)).pack(pady=20)
        return
    
    # Create listbox for students
    tk.Label(attendance_window, text="Select students present today:", 
             font=("Arial", 12)).pack(pady=(10, 5))
    
    listbox_frame = tk.Frame(attendance_window)
    listbox_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side='right', fill='y')
    
    student_listbox = tk.Listbox(listbox_frame, selectmode='multiple', 
                                yscrollcommand=scrollbar.set, font=("Arial", 10))
    student_listbox.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=student_listbox.yview)
    
    # Populate listbox
    for index, row in students_df.iterrows():
        student_listbox.insert(tk.END, f"{row['student_id']} - {row['name']}")
    
    def mark_selected_present():
        selected_indices = student_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one student!")
            return
        
        conn = sqlite3.connect("database/attendance.db")
        c = conn.cursor()
        today = str(datetime.now().date())
        current_time = str(datetime.now().time())[:8]
        
        marked_count = 0
        for index in selected_indices:
            student_info = students_df.iloc[index]
            student_id = student_info['student_id']
            name = student_info['name']
            
            # Check if already marked today
            c.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
            if not c.fetchall():
                c.execute("INSERT INTO attendance (student_id, name, date, time, status) VALUES (?, ?, ?, ?, ?)",
                          (student_id, name, today, current_time, "Present"))
                marked_count += 1
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"Marked {marked_count} students as present!")
        attendance_window.destroy()
    
    tk.Button(attendance_window, text="Mark Selected as Present", 
              command=mark_selected_present, font=("Arial", 12, "bold"), 
              bg='#27ae60', fg='white', padx=20, pady=10).pack(pady=20)

def quick_attendance():
    """Quick attendance by entering student IDs"""
    quick_window = tk.Toplevel()
    quick_window.title("Quick Attendance")
    quick_window.geometry("400x300")
    
    tk.Label(quick_window, text="Quick Attendance Entry", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    tk.Label(quick_window, text="Enter Student ID:", 
             font=("Arial", 12)).pack(pady=5)
    
    id_entry_quick = tk.Entry(quick_window, font=("Arial", 12), width=20)
    id_entry_quick.pack(pady=5)
    
    result_text = scrolledtext.ScrolledText(quick_window, width=40, height=10)
    result_text.pack(pady=10, padx=20, fill='both', expand=True)
    
    def mark_attendance_quick():
        student_id = id_entry_quick.get().strip()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a student ID!")
            return
        
        conn = sqlite3.connect("database/attendance.db")
        c = conn.cursor()
        
        # Check if student exists
        c.execute("SELECT name FROM students WHERE student_id=?", (student_id,))
        student = c.fetchone()
        
        if not student:
            result_text.insert(tk.END, f"❌ Student ID {student_id} not found!\n")
            id_entry_quick.delete(0, tk.END)
            conn.close()
            return
        
        name = student[0]
        today = str(datetime.now().date())
        current_time = str(datetime.now().time())[:8]
        
        # Check if already marked today
        c.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
        if c.fetchall():
            result_text.insert(tk.END, f"⚠️ {name} ({student_id}) already marked today!\n")
        else:
            c.execute("INSERT INTO attendance (student_id, name, date, time, status) VALUES (?, ?, ?, ?, ?)",
                      (student_id, name, today, current_time, "Present"))
            conn.commit()
            result_text.insert(tk.END, f"✅ {name} ({student_id}) marked present!\n")
        
        conn.close()
        id_entry_quick.delete(0, tk.END)
        result_text.see(tk.END)
    
    tk.Button(quick_window, text="Mark Present", command=mark_attendance_quick,
              font=("Arial", 12, "bold"), bg='#3498db', fg='white').pack(pady=10)
    
    # Allow Enter key to mark attendance
    id_entry_quick.bind('<Return>', lambda event: mark_attendance_quick())
    id_entry_quick.focus()

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

def view_students():
    """Display registered students"""
    conn = sqlite3.connect("database/attendance.db")
    
    # Get student data
    df = pd.read_sql_query("SELECT * FROM students ORDER BY name", conn)
    conn.close()
    
    if df.empty:
        messagebox.showinfo("Info", "No students registered yet!")
        return
    
    # Create new window
    view_window = tk.Toplevel()
    view_window.title("Registered Students")
    view_window.geometry("600x400")
    
    # Create treeview
    tree = ttk.Treeview(view_window, columns=('ID', 'Student_ID', 'Name', 'Registered_Date'), show='headings')
    
    # Define headings
    tree.heading('ID', text='ID')
    tree.heading('Student_ID', text='Student ID')
    tree.heading('Name', text='Name')
    tree.heading('Registered_Date', text='Registered Date')
    
    # Configure column widths
    tree.column('ID', width=50)
    tree.column('Student_ID', width=150)
    tree.column('Name', width=200)
    tree.column('Registered_Date', width=150)
    
    # Insert data
    for index, row in df.iterrows():
        tree.insert('', 'end', values=(row['id'], row['student_id'], row['name'], row['registered_date']))
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(view_window, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack widgets
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

def export_to_excel():
    """Export attendance data to Excel file"""
    conn = sqlite3.connect("database/attendance.db")
    attendance_df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC, time DESC", conn)
    students_df = pd.read_sql_query("SELECT * FROM students ORDER BY name", conn)
    conn.close()
    
    if attendance_df.empty and students_df.empty:
        messagebox.showinfo("Info", "No data to export!")
        return
    
    try:
        filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if not attendance_df.empty:
                attendance_df.to_excel(writer, sheet_name='Attendance Records', index=False)
            if not students_df.empty:
                students_df.to_excel(writer, sheet_name='Registered Students', index=False)
        
        messagebox.showinfo("Success", f"Data exported to {filename}")
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

def refresh_student_list():
    """Refresh any displayed student lists"""
    pass  # Placeholder for future use

# ---------- Tkinter GUI ----------
root = tk.Tk()
root.title("Attendance Management System (Simple Version)")
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

subtitle_label = tk.Label(title_frame, text="Simple Version - Manual Entry", 
                         font=("Arial", 12), fg='#ecf0f1', bg='#2c3e50')
subtitle_label.pack()

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
reg_btn = tk.Button(reg_frame, text="📝 Register New Student", 
                   command=lambda: register_student(name_entry.get(), id_entry.get()),
                   font=("Arial", 12, "bold"), bg='#3498db', fg='white', 
                   padx=20, pady=10, cursor='hand2')
reg_btn.pack(pady=(10, 0))

# Attendance Operations Section
ops_frame = tk.LabelFrame(main_frame, text="✅ Attendance Operations", font=("Arial", 14, "bold"), 
                         bg='#f0f0f0', fg='#2c3e50', padx=20, pady=15)
ops_frame.pack(fill='x', pady=(0, 15))

# Buttons frame
btn_frame = tk.Frame(ops_frame, bg='#f0f0f0')
btn_frame.pack(fill='x')

manual_btn = tk.Button(btn_frame, text="📋 Manual Attendance", command=manual_attendance,
                      font=("Arial", 11, "bold"), bg='#27ae60', fg='white', 
                      padx=15, pady=8, cursor='hand2')
manual_btn.pack(fill='x', pady=5)

quick_btn = tk.Button(btn_frame, text="⚡ Quick Entry (by ID)", command=quick_attendance,
                     font=("Arial", 11, "bold"), bg='#f39c12', fg='white', 
                     padx=15, pady=8, cursor='hand2')
quick_btn.pack(fill='x', pady=5)

# Reports and Data Section
reports_frame = tk.LabelFrame(main_frame, text="📊 Reports & Data Management", font=("Arial", 14, "bold"), 
                             bg='#f0f0f0', fg='#2c3e50', padx=20, pady=15)
reports_frame.pack(fill='x', pady=(0, 15))

view_students_btn = tk.Button(reports_frame, text="👥 View Students", command=view_students,
                             font=("Arial", 11, "bold"), bg='#9b59b6', fg='white', 
                             padx=15, pady=8, cursor='hand2')
view_students_btn.pack(fill='x', pady=5)

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

status_label = tk.Label(status_frame, text="Ready | Simple Attendance Management System", 
                       font=("Arial", 10), bg='#ecf0f1', fg='#7f8c8d')
status_label.pack(side='left', padx=10, pady=5)

# Instructions
instructions_frame = tk.LabelFrame(main_frame, text="📋 Quick Instructions", font=("Arial", 12, "bold"), 
                                  bg='#f0f0f0', fg='#2c3e50', padx=15, pady=10)
instructions_frame.pack(fill='x')

instructions_text = """
1. Register students by entering their name and ID
2. Use 'Manual Attendance' to select multiple students at once
3. Use 'Quick Entry' to mark individual students by typing their ID
4. View student lists, attendance records, and generate reports
5. Export data to Excel for external use
"""

instructions_label = tk.Label(instructions_frame, text=instructions_text, 
                             font=("Arial", 10), bg='#f0f0f0', fg='#555555', 
                             justify='left', wraplength=500)
instructions_label.pack(anchor='w')

if __name__ == "__main__":
    root.mainloop()