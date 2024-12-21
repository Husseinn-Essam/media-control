import torch
import cv2
import numpy as np
from model_3.hand_segnet import handsegnet

# Configuration
use_gpu = True
device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"

# Initialize the model and move to appropriate device
model = handsegnet(pretrained=True).to(device)

# Start video capture
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break
    
    # Apply Gaussian Blur to reduce noise
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Resize and normalize the image
    image_resized = cv2.resize(image_rgb, (320, 240))
    image_normalized = np.expand_dims((image_resized.astype("float") / 255.0) - 0.5, 0)
    
    # Convert to PyTorch tensor and adjust dimensions
    input_tensor = torch.from_numpy(image_normalized.transpose(0, 3, 1, 2)).float().to(device)
    
    # Model inference
    with torch.no_grad():
        hand_scoremap = model(input_tensor)
    
    # Post-process output
    hand_scoremap = hand_scoremap.permute(0, 2, 3, 1).detach().cpu().numpy()
    hand_scoremap = np.squeeze(hand_scoremap)
    hand_scoremap = np.argmax(hand_scoremap, axis=2)
    
    # Display the frame and the hand segmentation mask
    cv2.imshow("Frame", frame)
    cv2.imshow("Hand Segmentation Mask", hand_scoremap.astype(np.float64))

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
