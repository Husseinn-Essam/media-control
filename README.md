# Media control with gestures Project

# Python libraries required
- pip install opencv-python
- pip install numpy
- pip install skimage
- pip install Flask
- pip install PyAutoGUI
- pip install flask-cors

# Setup
- before we start:
Open PowerShell as an administrator.
Run the following command to change the execution policy:
```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

# To run the project there are two options
# 1. GUI option
- For GUI you need npm and node  

- Once npm and node are installed
- Enter the project directory
```
cd ./GUI
```
- and install the dependencies
```
npm install
```
- Start GUI
```
npm run dev
```
- now go to the gesture-recognition directory
```
cd ..\gesture-recognition\
```
- run the app.py file
- the app.py is a server once it has started you can proceed
- Click on "start feed" button on the GUI and wait for the it to launch, it may take a few seconds
- make sure your camera is open

# 2. No GUI option (only do this if you want to run the project without GUI)
if you want to run the project without the GUI
```
cd .\gesture-recognition\
```
- run noGUI.py
