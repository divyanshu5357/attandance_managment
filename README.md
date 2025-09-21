# 🎓 Attendance Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)](https://opencv.org)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

A comprehensive attendance management system built entirely with Python libraries, featuring both face recognition technology for automated attendance marking and a simple manual entry system.

## 🚀 **Quick Start for New Users**

**Want to run this app on your computer? It's easy!**

### Option 1: Simple Version (Recommended for beginners)
```bash
# 1. Download the repository
git clone https://github.com/YOUR_USERNAME/attendance-management-system.git
cd attendance-management-system

# 2. Install basic requirements
pip install opencv-python numpy pandas matplotlib openpyxl pillow

# 3. Run the simple app
python app_simple.py
```

### Option 2: Full Version with Face Recognition
```bash
# Follow Option 1, then also install:
pip install face_recognition

# Run the full app
python app.py
```

**📖 Need detailed instructions? Check [INSTALLATION.md](INSTALLATION.md)**

## 📱 **Two Apps in One**

| App | Features | Best For |
|-----|----------|----------|
| `app_simple.py` | Manual attendance, reports, Excel export | Quick setup, beginners, any Python version |
| `app.py` | Everything above + face recognition | Advanced users, automatic attendance |

## 🚀 Features

- **Face Recognition**: Automated attendance marking using facial recognition
- **Student Registration**: Easy student enrollment with face capture
- **Modern GUI**: User-friendly interface built with Tkinter
- **Data Management**: SQLite database for reliable data storage
- **Reports & Analytics**: Comprehensive attendance reports and statistics
- **Data Export**: Export attendance data to Excel files
- **Real-time Processing**: Live camera feed for attendance marking

## 🐍 Python Libraries Used

### Core Libraries
- **Tkinter** (`tkinter`) - Built-in GUI framework for desktop application
- **OpenCV** (`cv2`) - Computer vision library for camera access and image processing
- **face_recognition** - Facial recognition and encoding library
- **SQLite3** (`sqlite3`) - Built-in database for data storage
- **NumPy** (`numpy`) - Numerical computations and array operations
- **Pandas** (`pandas`) - Data manipulation and analysis
- **PIL/Pillow** (`PIL`) - Image processing and manipulation

### Additional Libraries
- **Matplotlib** (`matplotlib`) - Data visualization and charts
- **openpyxl** - Excel file creation and manipulation
- **python-dateutil** - Enhanced date/time handling
- **tkcalendar** - Calendar widgets for GUI
- **reportlab** - PDF report generation

## � **Download & Installation**

### For End Users (Just want to use the app):
1. **[📖 Read the Installation Guide](INSTALLATION.md)** - Complete step-by-step instructions
2. **Download:** Click "Code" → "Download ZIP" or use `git clone`
3. **Install:** `pip install -r requirements_working.txt`
4. **Run:** `python app_simple.py`

### For Developers:
- Clone the repository: `git clone https://github.com/YOUR_USERNAME/attendance-management-system.git`
- Install dev dependencies: `pip install -r requirement.txt`
- Check [SETUP.md](SETUP.md) for detailed development setup

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd attendance_management
   ```

2. **Install required packages**
   ```bash
   pip install -r requirement.txt
   ```

   If you encounter issues with `face_recognition`, install these first:
   ```bash
   pip install cmake
   pip install dlib
   pip install face_recognition
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

## 🎯 How to Use

### 1. Student Registration
- Enter student name and ID in the registration form
- Click "Register New Student"
- Position your face in the camera frame
- Press **SPACEBAR** to capture images (10 images recommended)
- Press **'q'** to finish registration

### 2. Generate Face Encodings
- After registering all students, click "Generate Face Encodings"
- This processes all student photos and creates facial recognition data
- Wait for the process to complete

### 3. Mark Attendance
- Click "Mark Attendance" to start the camera
- Students' faces will be automatically recognized
- Attendance is marked once per day per student
- Press **'q'** to stop attendance marking

### 4. View and Manage Data
- **View Attendance Records**: See all attendance data in a table
- **Generate Statistics**: Get detailed attendance analytics
- **Export to Excel**: Save attendance data as Excel file

## 📁 Project Structure

```
attendance_management/
├── app.py                 # Main application file
├── requirement.txt        # Python dependencies
├── README.md             # This documentation
├── data/
│   └── students/         # Student photos storage
├── database/
│   └── attendance.db     # SQLite database
└── encodings/
    └── encodings.pkl     # Face recognition data
```

## 🔧 Configuration

### Camera Settings
- Default camera index: 0 (primary camera)
- To use different camera, modify `cv2.VideoCapture(0)` in the code

### Face Recognition Settings
- Recognition tolerance: 0.6 (adjustable in `mark_attendance()`)
- Lower values = stricter matching
- Higher values = more lenient matching

### Database Schema
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    name TEXT,
    date TEXT,
    time TEXT,
    status TEXT
);
```

## 🎨 Why These Python Libraries?

### **Tkinter** - Perfect for Desktop GUI
- ✅ Built into Python (no extra installation)
- ✅ Cross-platform compatibility
- ✅ Professional-looking interfaces
- ✅ Rich widget set (buttons, forms, tables)

### **OpenCV** - Computer Vision Excellence
- ✅ Industry-standard for image processing
- ✅ Excellent camera access and control
- ✅ Real-time video processing
- ✅ Optimized performance

### **face_recognition** - State-of-the-art Face Recognition
- ✅ Built on top of dlib's face recognition
- ✅ High accuracy facial recognition
- ✅ Easy-to-use Python API
- ✅ Handles face detection and encoding

### **SQLite** - Reliable Data Storage
- ✅ Built into Python
- ✅ No server setup required
- ✅ ACID compliance
- ✅ Perfect for local applications

### **Pandas** - Data Analysis Powerhouse
- ✅ Excel-like data manipulation
- ✅ Easy data export/import
- ✅ Statistical analysis capabilities
- ✅ Integration with visualization libraries

## 🔍 Troubleshooting

### Common Issues

1. **Camera not detected**
   - Check if camera is connected and not used by other applications
   - Try changing camera index in code (0, 1, 2, etc.)

2. **face_recognition installation issues**
   ```bash
   # For Windows users
   pip install cmake
   pip install dlib
   pip install face_recognition
   ```

3. **Poor face recognition accuracy**
   - Ensure good lighting during registration
   - Capture more images per student (increase count in registration)
   - Adjust tolerance value in `mark_attendance()`

4. **Import errors**
   - Make sure all packages are installed: `pip install -r requirement.txt`
   - Use virtual environment to avoid conflicts

## 📊 Features Overview

| Feature | Library Used | Description |
|---------|-------------|-------------|
| GUI Interface | Tkinter | Modern, responsive desktop interface |
| Face Recognition | face_recognition, OpenCV | Accurate facial recognition and detection |
| Database | SQLite3 | Reliable local data storage |
| Data Export | Pandas, openpyxl | Excel export functionality |
| Image Processing | PIL, OpenCV | Image capture and processing |
| Statistics | Pandas, Matplotlib | Attendance analytics and visualization |

## 🚀 Future Enhancements

- **Web Interface**: Use Flask/Django for web-based access
- **Mobile App**: React Native or Flutter integration
- **Cloud Storage**: Integration with cloud databases
- **Advanced Analytics**: More detailed reporting and insights
- **Multi-Camera Support**: Support for multiple camera locations

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section
2. Create an issue in the repository
3. Contact the development team

---

**Built with ❤️ using Python and open-source libraries**