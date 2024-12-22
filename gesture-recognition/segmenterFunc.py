import cv2
import threading
from skimage.color import rgb2gray
from skimage.filters import gaussian, threshold_otsu
from skimage.measure import label, regionprops
import numpy as np
from math import ceil
from customAlgos import calcSolidity, detect_pointing_direction, angle_between_points, convexity_defects


def isolate_hand(capturedFrame):
    """
    Isolates the hand in the input frame, making the rest of the frame black.
    
    Args:
        capturedFrame (numpy.ndarray): Input frame.
    
    Returns:
        numpy.ndarray: Output frame with only the hand visible, the rest black.
    """
    # apply preprocessing on frame
    preprocessed_frame, thresh_frame = preprocess_frame(capturedFrame)
    hand_segment = segment_hand(thresh_frame, preprocessed_frame)

    if hand_segment is not None and len(hand_segment) == 4:
        # Get the bounding box of the hand
        x, y, w, h = hand_segment
        # Create a black frame with the same dimensions as the input frame
        black_frame = np.zeros_like(capturedFrame)
        # we get the ROI (cropped image where hand is located)
        roi = capturedFrame[y:y + h, x:x + w]
        # apply thresholding to get the mask of the hand
        hand_mask = skin_thresholding(roi)
        # Place the isolated hand on the black frame which will have the same demensions as the input frame
        black_frame[y:y + h, x:x + w] = cv2.bitwise_and(roi, roi, mask=hand_mask)
        return black_frame

    else:
        # If no hand is detected, return a completely black frame
        return np.zeros_like(capturedFrame)


def segmenter(capturedFrame, mode='HSV',increase_ratio=0.25):
    # preprocess the frame
    capturedFrame, thresh_frame = preprocess_frame(capturedFrame, mode)
    # segment the hand
    hand_segment = segment_hand(thresh_frame, capturedFrame, increase_ratio)
    if hand_segment is not None and len(hand_segment) == 4:
        roi = capturedFrame[hand_segment[1]:hand_segment[1] + hand_segment[3], hand_segment[0]:hand_segment[0] + hand_segment[2]]
        
        # Set the bottom rows to 0
        rows_roi, cols_roi, _ = roi.shape
        if rows_roi > 0 and int(rows_roi * 0.27) > 0:
            roi[-int(rows_roi * 0.27):] = 0 
            
        isolated_hand = isolate_hand(capturedFrame)
        hand = skin_thresholding(roi) # the mask of the bounded hand (will be used for gesture recognition)
        isolated_hand_mask = skin_thresholding(isolated_hand)  # get the mask of the hand (will be used for centroid tracking)  
        return hand, roi, capturedFrame, isolated_hand_mask
    else:
        return thresh_frame, capturedFrame


def segment_hand(thresh_frame, original_frame, increase_ratio=0.25, min_score_threshold=0):
    # Convert to 8-bit integer if needed
    thresh_frame = thresh_frame.astype(np.uint8)

    # Step 1: Find contours
    contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None  # No hand detected

    # Step 2: Filter contours by size and shape
    filtered_contours = []
    frame_area = thresh_frame.shape[0] * thresh_frame.shape[1]

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 0.01 * frame_area or area > 0.8 * frame_area:
            continue  # Ignore contours that are too small or too large
        
        # calculate defects
        hull_indices = cv2.convexHull(contour, returnPoints=False).flatten()

        defects = convexity_defects(contour[:, 0, :], hull_indices)
        
        count_defects = 0
        
        # Filter defects with approximately 90 degrees
        filtered_defects = []
        for defect in defects:
            start_idx, end_idx, far_idx, depth = defect
            start = tuple(contour[start_idx][0])
            end = tuple(contour[end_idx][0])
            far = tuple(contour[far_idx][0])
            angle = angle_between_points(start, end, far)
            if  angle < 90:  # Allow a small margin around 90 degrees
                count_defects += 1
                filtered_defects.append(defect)
        
        # calculate solidity and direction
        solidity = calcSolidity(contour)
        direction = detect_pointing_direction(original_frame, contour)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        
        # Filter out faces and other non-hand shapes (rectangular faces)
        if (solidity > 0.53 and count_defects == 0 and 0.4 < aspect_ratio < 0.69) and (direction not in ["oneFingerRight", "oneFingerLeft", "oneFingerUp"]):    
            print(f"REFUSED1 Aspect ratio: {aspect_ratio}, Solidity: {solidity}, Defects: {count_defects}, Direction: {direction}")
            continue
        # Filter out faces and other non-hand shapes (circular faces)
        if (solidity > 0.6 and count_defects == 0 and aspect_ratio > 1) and (direction in ["oneFingerRight", "oneFingerLeft"]):
            print(f"REFUSED2 Aspect ratio: {aspect_ratio}, Solidity: {solidity}, Defects: {count_defects}, Direction: {direction}")
            continue

        # Check aspect ratio of bounding box
        print(f"ACCEPTED Aspect ratio: {aspect_ratio}, Solidity: {solidity}, Defects: {count_defects}, Direction: {direction}")
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        if 0.3 < aspect_ratio < 3:  # Acceptable aspect ratio range for a hand
            filtered_contours.append(contour)

    if not filtered_contours:
        return None  # No valid hand-like contour found

    # Step 3: Score bounding boxes
    bounding_boxes = []
    scores_list = []
    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cx, cy = x + w // 2, y + h // 2  # Center of the bounding box

        # Calculate solidity
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = cv2.contourArea(contour) / hull_area
        else:
            solidity = 0

        # Calculate circularity
        perimeter = cv2.arcLength(contour, True)
        circularity = (4 * np.pi * cv2.contourArea(contour)) / (perimeter ** 2) if perimeter > 0 else 0

        # Calculate convexity defects
        hull_indices = cv2.convexHull(contour, returnPoints=False)
        if len(hull_indices) > 3:  # Ensure enough points to compute defects
            defects = cv2.convexityDefects(contour, hull_indices)
            if defects is not None:
                defect_count = defects.shape[0]
                defect_density = defect_count / perimeter if perimeter > 0 else 0
            else:
                defect_density = 0
        else:
            defect_density = 0

        # Calculate proximity to frame center
        frame_center_x, frame_center_y = original_frame.shape[1] // 2, original_frame.shape[0] // 2
        distance_to_center = ((cx - frame_center_x) ** 2 + (cy - frame_center_y) ** 2) ** 0.5

       # Scoring system
        size_score = w * h / frame_area
        aspect_ratio_score = 1 - abs(aspect_ratio - 1)  # Closer to 1 is better
        solidity_score = solidity  # Higher solidity preferred
        circularity_penalty = max(0, 1 - circularity)  # Penalize overly circular shapes
        defect_score = defect_density * 10  # Boost based on defect density
        proximity_score = 1 / (1 + distance_to_center)  # Closer to center is better

        # Final score with reduced size weight
        final_score = (0.2 * size_score +           # Reduced weight for size
                    0.3 * aspect_ratio_score +   # Increased weight for aspect ratio
                    0.3 * solidity_score +       # High weight for solidity
                    0.15 * defect_score -        # Moderate weight for defects
                    0.05 * circularity_penalty + # Slight penalty for circularity
                    0.05 * proximity_score)      # Slight weight for proximity


        # Only add bounding box if final score is above threshold
        if final_score >= min_score_threshold:
            bounding_boxes.append((final_score, (x, y, w, h), contour))
            scores_list.append([final_score, size_score, aspect_ratio_score, solidity_score, circularity_penalty, defect_score, proximity_score])

    # Step 4: Select the best bounding box
    if bounding_boxes:
        _, best_bounding_box, _ = max(bounding_boxes, key=lambda b: b[0])
        best_scores = scores_list[bounding_boxes.index(max(bounding_boxes, key=lambda b: b[0]))]
        second_best_scores = scores_list[bounding_boxes.index(sorted(bounding_boxes, key=lambda b: b[0])[-1])]
        print(f"BEST SCORES. final_score: {best_scores[0]}, size_score: {best_scores[1]}, aspect_ratio_score: {best_scores[2]}, solidity_score: {best_scores[3]}, circularity_penalty: {best_scores[4]}, defect_score: {best_scores[5]}, proximity_score: {best_scores[6]}")
        print(f"SECOND BEST SCORES. final_score: {second_best_scores[0]}, size_score: {second_best_scores[1]}, aspect_ratio_score: {second_best_scores[2]}, solidity_score: {second_best_scores[3]}, circularity_penalty: {second_best_scores[4]}, defect_score: {second_best_scores[5]}, proximity_score: {second_best_scores[6]}")
        # Increase the bounding box size, Default: by 25%
        x, y, w, h = best_bounding_box
        x = max(0, x - int(increase_ratio / 2 * w))
        y = max(0, y - int(increase_ratio / 2 * h))
        w = min(original_frame.shape[1] - x, w + int(increase_ratio * w))
        h = min(original_frame.shape[0] - y, h + int(increase_ratio * h))

        return (x, y, w, h)
    else:
        return None  # No valid hand found above the threshold
    


def adaptive_thresholding(image):
    gray_frame = rgb2gray(image)
    
    thresh = threshold_otsu(gray_frame)
    thresh_frame = gray_frame < thresh
    thresh_frame = thresh_frame.astype(np.uint8) * 255
    thresh_frame = cv2.morphologyEx(thresh_frame, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=3)
    
    return thresh_frame

def skin_thresholding(image, mode='Ycrcb'):
    if mode.lower() == "hsv":
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_vals = np.array([0, 50, 40], np.uint8)
        upper_vals = np.array([20, 255, 255], np.uint8)
        skinMask = cv2.inRange(hsv_image, lower_vals, upper_vals)
    else:
        # Constants for finding range of skin
        min_YCrCb = np.array([0, 133, 77], np.uint8)
        max_YCrCb = np.array([255, 173, 127], np.uint8)
        imageYCrCb = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)
        skinMask = cv2.inRange(imageYCrCb, min_YCrCb, max_YCrCb)
    # skinMask = cv2.GaussianBlur(skinMask, (5, 5), 0)
    skinMask = cv2.medianBlur(skinMask, 5)
    skinMask = cv2.GaussianBlur(skinMask, (5, 5), 0)
    
    skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)
    skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=3)
    skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)

    skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=6)
    
    return skinMask

def preprocess_frame(capturedFrame, mode='HSV'):
    # capturedFrame = white_balance(capturedFrame)
    #capturedFrame = normalize_lighting_clahe(capturedFrame)
    capturedFrame = normalize_lighting_histogram(capturedFrame, mode= "YCrCb")
    capturedFrame = cv2.GaussianBlur(capturedFrame, (3, 3), 0)
    capturedFrame = cv2.medianBlur(capturedFrame, 5)
    
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
        
    
    
    # apply a series of erosions and dilations to the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    # skinMask = cv2.dilate(skinMask, kernel, iterations=5)
    # skinMask = cv2.erode(skinMask, kernel, iterations=2)
    skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_CLOSE, kernel, iterations=4)

    # blur the mask to help remove noise
    skinMask = cv2.GaussianBlur(skinMask, (5, 5), 0)
    # capturedFrame = cv2.bitwise_and(capturedFrame, capturedFrame, mask=skinMask)
    return capturedFrame, skinMask

def normalize_lighting_clahe(image):
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Apply CLAHE to the L channel
    #clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    #lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    lab[:, :, 0] = manual_clahe(lab[:, :, 0], tileGridSize=8, clipLimit=2.0)
    # Convert back to BGR
    normalized_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return normalized_image

def manual_clahe(channel, tileGridSize=4, clipLimit=2.0):

    height, width = channel.shape
    tileHeight = ceil(height / tileGridSize)
    tileWidth = ceil(width / tileGridSize)
    output = np.zeros_like(channel, dtype=np.uint8)

    for ty in range(tileGridSize):
        for tx in range(tileGridSize):
            y1, y2 = ty * tileHeight, min((ty + 1) * tileHeight, height)
            x1, x2 = tx * tileWidth, min((tx + 1) * tileWidth, width)
            subregion = channel[y1:y2, x1:x2]
            hist, _ = np.histogram(subregion, bins=256, range=(0, 256))

            limit = int(clipLimit * (subregion.size / 256.0))
            excess = np.maximum(hist - limit, 0).sum()
            hist = np.minimum(hist, limit)
            spread = excess // 256
            hist += spread
            remainder = excess % 256
            hist[:remainder] += 1

            cdf = np.cumsum(hist).astype(np.float32)
            cdf = (cdf / cdf[-1]) * 255
            eq = np.interp(subregion.flatten(), np.arange(256), cdf).reshape(subregion.shape).astype(np.uint8)
            output[y1:y2, x1:x2] = eq

    return output

def normalize_lighting_histogram(image, mode='YCrCb'):
    if mode == 'YCrCb':
        # Convert to YCrCb color space
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        # Equalize the Y channel
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        # Convert back to BGR
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    elif mode == 'Lab':
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        # Equalize the L channel
        lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0])
        # Convert back to BGR
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    elif mode == 'HSV':
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv_img[:, :, 2] = cv2.equalizeHist(hsv_img[:, :, 2])
        return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    else :# RGB
        channels = cv2.split(image)
        eq_channels = [cv2.equalizeHist(ch) for ch in channels]
        return cv2.merge(eq_channels)

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