# 🚀 Installation Guide for Users

This guide will help you download and run the Attendance Management System on your computer.

## 📋 Prerequisites

Before you start, make sure you have:
- **Python 3.8 or higher** installed on your computer
- **Git** installed (optional - you can also download as ZIP)
- **Webcam** (only needed for face recognition features)

## 💻 Method 1: Download using Git (Recommended)

### Step 1: Clone the Repository
Open terminal/command prompt and run:
```bash
git clone https://github.com/YOUR_USERNAME/attendance-management-system.git
cd attendance-management-system
```

### Step 2: Install Dependencies
```bash
# For the simple version (works immediately)
pip install -r requirements_working.txt

# OR for the full version with face recognition (may need additional setup)
pip install -r requirement.txt
```

### Step 3: Run the Application
```bash
# Run the simple version (recommended for first-time users)
python app_simple.py

# OR run the face recognition version (if dependencies installed successfully)
python app.py
```

## 📦 Method 2: Download as ZIP

### Step 1: Download
1. Go to the GitHub repository page
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your desired location

### Step 2: Open Terminal/Command Prompt
Navigate to the extracted folder:
```bash
cd path/to/attendance-management-system
```

### Step 3: Install Dependencies and Run
Follow the same steps as Method 1 (Step 2 and 3)

## 🎯 Quick Start Guide

### Option A: Simple Version (No Face Recognition)
**Best for beginners or if you have installation issues**

1. **Install basic requirements:**
   ```bash
   pip install opencv-python numpy pandas matplotlib openpyxl pillow
   ```

2. **Run the simple app:**
   ```bash
   python app_simple.py
   ```

3. **Start using:**
   - Register students manually
   - Mark attendance by selecting students
   - Generate reports and export data

### Option B: Full Version (With Face Recognition)
**For advanced users with proper setup**

1. **Install all requirements:**
   ```bash
   pip install -r requirement.txt
   ```

2. **If face_recognition fails to install:**
   ```bash
   # Try these alternatives:
   pip install cmake
   pip install dlib
   pip install face_recognition
   
   # OR use conda:
   conda install -c conda-forge dlib
   conda install -c conda-forge face_recognition
   ```

3. **Run the full app:**
   ```bash
   python app.py
   ```

## 🔧 System Requirements

### Minimum Requirements:
- **OS:** Windows 7+, macOS 10.12+, Ubuntu 16.04+
- **Python:** 3.8 or higher
- **RAM:** 4GB (8GB recommended for face recognition)
- **Storage:** 500MB free space
- **Camera:** Any USB webcam (for face recognition only)

### Python Version Compatibility:
- ✅ **Python 3.8-3.12:** Fully supported
- ⚠️ **Python 3.13:** Simple version works, face recognition may need compilation
- ❌ **Python 3.7 and below:** Not supported

## 🐛 Troubleshooting

### Problem: "pip is not recognized"
**Solution:** Add Python to your system PATH or use:
```bash
python -m pip install -r requirements_working.txt
```

### Problem: face_recognition installation fails
**Solution:** Use the simple version instead:
```bash
python app_simple.py
```

### Problem: "No module named 'tkinter'"
**Solution:** 
- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **CentOS/RHEL:** `sudo yum install tkinter`
- **macOS:** Tkinter comes with Python
- **Windows:** Tkinter comes with Python

### Problem: Camera not detected
**Solution:**
- Check if camera is connected
- Close other applications using the camera
- Try changing camera index in code (0, 1, 2, etc.)

### Problem: "Microsoft Visual C++ 14.0 is required"
**Solution:** 
- Install Visual Studio Build Tools
- OR use the simple version: `python app_simple.py`

## 📱 How to Use the Application

### 1. **Register Students**
- Enter student name and ID
- Click "Register New Student"
- (Face recognition version: Capture face photos)

### 2. **Mark Attendance**
- **Simple version:** Use "Manual Attendance" or "Quick Entry"
- **Face recognition version:** Use "Mark Attendance" for automatic recognition

### 3. **View Data**
- Click "View Students" to see registered students
- Click "View Attendance Records" to see attendance history
- Use "Generate Statistics" for detailed reports

### 4. **Export Data**
- Click "Export to Excel" to save data as spreadsheet
- Files are saved in the same folder as the application

## 🆘 Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Use the simple version if face recognition doesn't work:**
   ```bash
   python app_simple.py
   ```
3. **Create an issue on GitHub** with:
   - Your operating system
   - Python version (`python --version`)
   - Error message (if any)
   - What you were trying to do

## 📞 Support

- **GitHub Issues:** Create an issue for bugs or feature requests
- **Documentation:** Check README.md and SETUP.md for detailed information
- **Email:** Contact the developer for urgent issues

## 🎉 Success!

If everything works correctly, you should see:
- A GUI window with the attendance management system
- Ability to register students and mark attendance
- Working reports and data export features

**Enjoy using the Attendance Management System!** 🚀