import cv2
import torch
import torch.hub
import numpy as np
from torchvision import transforms

# Check if GPU is available and select the appropriate device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create the model and move it to the GPU (if available)
model = torch.hub.load(
    repo_or_dir='guglielmocamporese/hands-segmentation-pytorch', 
    model='hand_segmentor', 
    pretrained=True
)
model.to(device)  # Move model to GPU

# Set the model to evaluation mode
model.eval()

# Define a transform to preprocess input frames
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

# Start the webcam capture
cap = cv2.VideoCapture(0)

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Preprocess the frame
    input_tensor = transform(frame_rgb)
    input_tensor = input_tensor.unsqueeze(0).to(device)  # Add batch dimension and move to GPU

    # Run the model to get predictions
    with torch.no_grad():
        output = model(input_tensor)
        preds = output.argmax(1)  # Get the class with the highest probability for each pixel

    # Post-process: Convert the prediction to a binary mask
    mask = preds.squeeze().cpu().numpy()  # Remove batch dimension and move back to CPU for further processing
    mask = np.uint8(mask * 255)  # Scale mask to 0-255 for visualization

    # Resize the mask to match the original frame size
    mask_resized = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

    # Apply the mask to the original frame
    hand_segmented = cv2.bitwise_and(frame, frame, mask=mask_resized)

    # Display the original frame and the segmented hand
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Hand Segmentation", hand_segmented)

    # Exit when the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
