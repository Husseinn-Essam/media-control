# Media control with gestures Project

## Setup
```
# For GUI you need npm and node  

## Once npm and node are installed
# Enter the project directory
cd GUI

Open PowerShell as an administrator.
Run the following command to change the execution policy:

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
npm install


# Develop
npm run dev

## to start backend
## run the video-feed-api.py

## for auto restart backend
pip install watchdog
pip install flask
pip install flask-cors

cd gesture-recognition
watchmedo auto-restart --patterns="*.py" --recursive -- python app.py

```
## notes
- feed-extract.py was just for testing opencv