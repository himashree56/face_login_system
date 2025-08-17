# Face Recognition Login System

## Overview
This is a face recognition login system that demonstrates user authentication using face detection with OpenCV. The application provides a real camera feed and allows users to register, login, and logout using face recognition combined with traditional username/password authentication.

## Features
- Real-time face detection using OpenCV
- User registration with face capture
- User login with face verification and password
- User session management (login/logout)
- Attendance logging
- MongoDB integration (with fallback to local JSON storage)
- Simple and intuitive GUI built with Tkinter

## Requirements
- Python 3.6+
- OpenCV (cv2)
- Pillow (PIL)
- Tkinter
- MongoDB (optional)
- PyMongo

All dependencies are installed in the virtual environment.

## How to Run
1. Make sure you have Python installed on your system
2. Activate the virtual environment:
   ```
   .\venv\Scripts\Activate.ps1
   ```
3. Run one of the following applications:
   ```
   python face_login_system.py  # OpenCV-based face detection with MongoDB support
   ```
   or
   ```
   python basic_face_detect.py  # Basic simulated face detection
   ```

## Usage

### Using face_login_system.py (OpenCV-based)
1. Launch the application
2. To register a new user:
   - Position your face in front of the camera
   - Enter your username, email, phone, and password
   - Click "Register"
   - Your face image and credentials will be saved
3. To login:
   - Position your face in front of the camera
   - Enter your username and password
   - Click "Login"
   - If your face and credentials match, you'll be logged in
4. To logout:
   - Click "Logout" to end your session
5. To download logs:
   - After logging in, click "Download Logs" to get a zip file of attendance records

### Using basic_face_detect.py (Simulated)
1. Launch the application
2. To register a new user:
   - Enter a username in the text field
   - Click "Register User"
   - The system will simulate face detection and save the user data
3. To login:
   - Enter your registered username
   - Click "Login"
   - The system will simulate face detection and verification
4. To logout:
   - Click "Logout" when logged in

## How It Works

### face_login_system.py (OpenCV-based)
- Face Detection: The system uses OpenCV's Haar Cascade Classifier to detect faces in the video feed
- User Registration: When a user registers, their face image is captured and stored along with their credentials
- Authentication: During login, the system verifies both the user's credentials and their face
- Data Storage: User data is stored in MongoDB if available, with a fallback to local JSON storage
- Directory Structure:
  - `captured_frames/`: Stores captured face images
  - `tmp/`: Temporary storage for processing
  - `attendance_logs/`: Stores login records
  - `user_data/`: Stores user information (when using JSON fallback)

### basic_face_detect.py (Simulated)
- User data is stored in a JSON file in the `./user_data` directory
- Face data is simulated and stored as text files in the `./captured_frames` directory
- The system tracks registration dates and last login times

## Future Enhancements
- Integration with more advanced face recognition algorithms
- Multi-factor authentication
- Admin panel for user management
- Enhanced attendance tracking and reporting capabilities
- Web-based interface
