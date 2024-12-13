import cv2
import threading
from skimage.color import rgb2gray
from skimage.filters import gaussian, threshold_otsu
from skimage.measure import label, regionprops
import numpy as np
from commonfunctions import *

def segmenter(capturedFrame):
    # preprocess the frame
    thresh_frame = preprocess_frame(capturedFrame)
    # segment the hand
    hand_segment = segment_hand(thresh_frame, capturedFrame)
    if hand_segment is not None:
        hand_segment = capturedFrame[hand_segment[1]:hand_segment[1] + hand_segment[3], hand_segment[0]:hand_segment[0] + hand_segment[2]]
        hand = adaptive_thresholding(hand_segment)
        return hand
    else:
        return thresh_frame

def segment_hand(thresh_frame, original_frame):
    # Convert to 8-bit integer if needed
    thresh_frame = thresh_frame.astype(np.uint8)

    # Step 1: Find contours
    contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None, None  # No hand detected

    # Step 2: Filter contours by size and shape
    filtered_contours = []
    frame_area = thresh_frame.shape[0] * thresh_frame.shape[1]

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 0.01 * frame_area or area > 0.8 * frame_area:
            continue  # Ignore contours that are too small or too large

        # Check aspect ratio of bounding box
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        # Draw the bounding rectangle on the image
        cv2.rectangle(original_frame, (x, y), (x + w, y + h), (255, 0, 0), 5)
        if 0.3 < aspect_ratio < 3.0:  # Acceptable aspect ratio range for a hand
            filtered_contours.append(contour)

    if not filtered_contours:
        return None  # No valid hand-like contour found

    # Step 3: Score bounding boxes
    bounding_boxes = []
    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cx, cy = x + w // 2, y + h // 2  # Center of the bounding box


        # Calculate proximity to frame center
        frame_center_x, frame_center_y = original_frame.shape[1] // 2, original_frame.shape[0] // 2
        distance_to_center = ((cx - frame_center_x) ** 2 + (cy - frame_center_y) ** 2) ** 0.5

        # Scoring system (adjust weights as needed)
        size_score = w * h / frame_area
        aspect_ratio_score = 1 - abs(aspect_ratio - 1)  # Closer to 1 is better

        proximity_score = 1 / (1 + distance_to_center)  # Closer to center is better

        # Final score
        final_score = (0.4 * size_score +
                       0.3 * aspect_ratio_score +
                       0.1 * proximity_score)
        
        bounding_boxes.append((final_score, (x, y, w, h)))

    # Step 4: Select the best bounding box
    best_bounding_box = max(bounding_boxes, key=lambda b: b[0])[1]

    # Draw the best bounding box
    cv2.rectangle(original_frame, (x, y), (x + w, y + h), (0, 255, 0), 10)
    # Increase the bounding box size by 25%
    increase_ratio = 0.25
    x, y, w, h = best_bounding_box
    x = max(0, x - int(increase_ratio / 2 * w))
    y = max(0, y - int(increase_ratio / 2 * h))
    w = min(original_frame.shape[1] - x, w + int(increase_ratio * w))
    h = min(original_frame.shape[0] - y, h + int(increase_ratio * h))
    best_bounding_box = (x, y, w, h)

    print("Best Bounding Box: ", best_bounding_box)
    return best_bounding_box

def adaptive_thresholding(image):
    gray_frame = rgb2gray(image)
    
    blurred_frame = gaussian(gray_frame, sigma=2) # to remove noise
    thresh = threshold_otsu(blurred_frame)
    thresh_frame = blurred_frame < thresh
    thresh_frame = thresh_frame.astype(np.uint8) * 255
    thresh_frame = cv2.morphologyEx(thresh_frame, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)
    
    return thresh_frame



def preprocess_frame(capturedFrame, mode='HSV'):
    # capturedFrame = white_balance(capturedFrame)
    # capturedFrame = normalize_lighting_clahe(capturedFrame)
    
    # Constants for finding range of skin color in YCrCb
    if mode == 'Ycrcb':        
        min_YCrCb = np.array([0, 133, 77], np.uint8)
        max_YCrCb = np.array([255, 173, 127], np.uint8)
        imageYCrCb = cv2.cvtColor(capturedFrame,cv2.COLOR_BGR2YCR_CB)
        skinMask = np.all(imageYCrCb >= min_YCrCb, axis=-1) & np.all(imageYCrCb <= max_YCrCb, axis=-1)
        skinMask = skinMask.astype("uint8") * 255  # Convert to 0 and 255
        # imageYCrCb = cv2.cvtColor(capturedFrame, cv2.COLOR_YCrCb2BGR)
    else:   
        # define the upper and lower boundaries of the HSV pixel intensities to be considered 'skin'
        imageHSV = cv2.cvtColor(capturedFrame, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 50, 40], dtype="uint8")
        upper = np.array([20, 255, 255], dtype="uint8")
        skinMask = np.all(imageHSV >= lower, axis=-1) & np.all(imageHSV <= upper, axis=-1)
        skinMask = skinMask.astype("uint8") * 255  # Convert to 0 and 255
        # imageHSV = cv2.cvtColor(capturedFrame, cv2.COLOR_HSV2BGR)
        
    
    # skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
    
    # apply a series of erosions and dilations to the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    # skinMask = cv2.dilate(skinMask, kernel, iterations=5)
    # skinMask = cv2.erode(skinMask, kernel, iterations=2)
    skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # blur the mask to help remove noise
    skinMask = cv2.GaussianBlur(skinMask, (5, 5), 0)
    # capturedFrame = cv2.bitwise_and(capturedFrame, capturedFrame, mask=skinMask)
    return capturedFrame, skinMask

def normalize_lighting_clahe(image):
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Apply CLAHE to the L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])

    # Convert back to BGR
    normalized_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return normalized_image

def normalize_lighting_histogram(image):
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Equalize the histogram of the V channel
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])

    # Convert back to BGR
    normalized_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return normalized_image

def white_balance(image):
    # Split into channels
    result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(result)

    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge channels and convert back to BGR
    balanced = cv2.merge((l, a, b))
    balanced = cv2.cvtColor(balanced, cv2.COLOR_LAB2BGR)
    return balanced

def gamma_correction(image, gamma=1.2):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(256)]).astype("uint8")
    corrected_image = cv2.LUT(image, table)
    return corrected_image