import cv2
import numpy as np
import math

def convexity_defects(points, hull):
    try:
        points = np.array(points, dtype=np.int32)
        hull = np.array(hull, dtype=np.int32)
        ## we dont have a closed shape so we can not compute convexity defects
        npoints = len(points)
        if npoints <= 3:
            print("Not enough points to form defects.")
            return []

        hpoints = len(hull)
        if hpoints < 3:
            print("Not enough hull points to form defects.")
            return []

        # print(f"Number of points: {npoints}, Number of hull points: {hpoints}")

        defects = []
        if hpoints < 3:
            print("Hull has less than 3 points, contour is always convex.")
            return defects
        ## check hull orientation (clockwise or anti) to determine the starting point
        rev_orientation = ((hull[1] > hull[0]) + (hull[2] > hull[1]) + (hull[0] > hull[2])) != 2

        hcurr = hull[0] if rev_orientation else hull[-1]

        for i in range(hpoints):
            hnext = hull[hpoints - i - 1] if rev_orientation else hull[i]
            
            # notice that: the hull elements are 0-based indices of the convex hull points 
            # in the contour array (since the set of convex hull points is a subset of the original contour point set).
            pt0 = points[hcurr]
            pt1 = points[hnext]
            dx0 = pt1[0] - pt0[0]
            dy0 = pt1[1] - pt0[1]
            
            ## 1) in case the edge length is 0 (dx = 0 and dy = 0) the scale will be 0 as the distance is 0
            ## 2) othewise the scale will be 1/edge_length for normalization 
            ##    as we dont want the edge length to affect the defect depth calculation
            scale = 0. if dx0 == 0 and dy0 == 0 else 1. / np.sqrt(dx0 * dx0 + dy0 * dy0)

            defect_deepest_point = -1
            defect_depth = 0
            is_defect = False
            j = hcurr

            while True:
                j += 1
                if j >= npoints:
                    j = 0
                if j == hnext:
                    break

                dx = points[j][0] - pt0[0]
                dy = points[j][1] - pt0[1]
                dist = abs(-dy0 * dx + dx0 * dy) * scale

                if dist > defect_depth:
                    defect_depth = dist
                    defect_deepest_point = j
                    is_defect = True

            if is_defect:
                idepth = int(round(defect_depth * 256))
                defects.append([hcurr, hnext, defect_deepest_point, idepth])

            hcurr = hnext

        return defects
    except Exception as e:
        print(f"Error in convexity_defects: {e}")
        print(f"Points: {points}")
        print(f"Hull: {hull}")
        return []

def angle_between_points(pt1, pt2, pt0):
    dx1 = pt1[0] - pt0[0]
    dy1 = pt1[1] - pt0[1]
    dx2 = pt2[0] - pt0[0]
    dy2 = pt2[1] - pt0[1]
    angle = math.atan2(dy1, dx1) - math.atan2(dy2, dx2)
    return abs(angle * 180.0 / math.pi)


def detect_pointing_direction(frame, contour):
            """
                Detect the pointing direction based on the palm center.
                Args:
                    frame: The frame to draw on(not the thresholded).
                    contour: The contour of the hand.
                
            """
            
            ## first we get the center of the palm
            moments = cv2.moments(contour)
            if moments['m00'] != 0:
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
                palm_center = (cx, cy)

                # Draw the palm center
                cv2.circle(frame, palm_center, 5, (255, 0, 0), -1)

                # Detect the fingertip (point farthest from the palm center)
                fingertip = None
                max_distance = 0
                for point in contour:
                    point = tuple(point[0])  # this gets the (x, y) coordinates
                    distance = np.linalg.norm(
                        np.array(point) - np.array(palm_center))  # We Compute the distance from palm center
                    if distance > max_distance:
                        max_distance = distance
                        fingertip = point
                if fingertip:
                    cv2.circle(frame, fingertip, 10, (0, 255, 0), -1)
                    cv2.line(frame, palm_center, fingertip, (255, 0, 0), 2)

                    # Compute pointing direction
                    pointing_vector = np.array(
                        [fingertip[0] - palm_center[0], fingertip[1] - palm_center[1]])
                    pointing_vector = pointing_vector / np.linalg.norm(pointing_vector)

                    # Determine direction of pointing
                    direction = ""
                    if abs(pointing_vector[0]) > abs(pointing_vector[1]):
                        if pointing_vector[0] > 0:
                            direction = "oneFingerRight"
                        else:
                            direction = "oneFingerLeft"
                    else:
                        if pointing_vector[1] > 0:
                            direction = "oneFingerDown"
                        else:
                            direction = "oneFingerUp"
                    return direction
                   

def is_rock_on(contour, drawing, cx, cy, count_defects):
    """
    Detect if the gesture is 'Rock On' (index and pinky extended).
    Args:
        contour: The contour of the hand.
        drawing: The image to draw on.
        cx: The x-coordinate of the palm center.
        cy: The y-coordinate of the palm center.
        count_defects: The number of convexity defects.
    """
    ## early exit if we have more than 1 defect, (the three, four and five finger gestures) 
    if count_defects > 1:
        return False
    
    # Draw the palm center for debugging
    palm_center = (cx, cy)
    cv2.circle(drawing, palm_center, 5, (255, 80, 255), -1)

    
    ## draw vertical line at center of the palm for debugging
    cv2.line(drawing, (cx, cy), (cx, 0), (255, 255), 2)  # Yellow vertical line
    
    ## Find the furthest points (fingertips) in each half of the hand
    ## then check if they are above the palm center and that each fingertip is far from each other
    ## we also check if one of the fingertips is  is above the other (index and pinky height difference)
    left_furthest = None
    right_furthest = None
    max_left_dist = 0
    max_right_dist = 0

    for point in contour:
        ## converts to (x, y) format
        point = tuple(point[0])  
        dist_to_palm = np.linalg.norm(np.array(point) - np.array(palm_center))

        if point[1] < palm_center[1]:  # Consider only points above the palm center
            if point[0] < cx:  # Point in the left half (pinky)
                if dist_to_palm > max_left_dist:
                    max_left_dist = dist_to_palm
                    left_furthest = point
            else:  # Point in the right half (index)
                if dist_to_palm > max_right_dist:
                    max_right_dist = dist_to_palm
                    right_furthest = point

    # Draw fingertips points
    if left_furthest:
        cv2.circle(drawing, left_furthest, 10, (0, 255, 0), -1)  
    if right_furthest:
        cv2.circle(drawing, right_furthest, 10, (255, 0, 0), -1)  

    
    if left_furthest and right_furthest:
        if (
            max_left_dist > 100 and max_right_dist > 100  # Both points are far enough from palm center
            and left_furthest[0] < palm_center[0]  # Left point is in the left half
            and right_furthest[0] > palm_center[0]  # Right point is in the right half
            and right_furthest[0] - left_furthest[0] > 100  # Horizontal distance between points is big enough
            and (right_furthest[1] > left_furthest[1])  ## we also check if right fingertip(index) is higher than pinky (index and pinky height difference)
        ):
            return True 

    return False


def get_palm_center(contour):
    moments = cv2.moments(contour)
    if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])  
        cy = int(moments['m01'] / moments['m00'])  
        return (cx, cy)
    else:
        return None
    
def calcSolidity(contour):
        x, y, w, h = cv2.boundingRect(contour)
        rect_area = w * h
        contour_area = cv2.contourArea(contour)
        return contour_area / rect_area if rect_area != 0 else 0


def filterDefects( defects, contour):
        try:
            filtered_defects= []
            count_defects = 0
            for defect in defects:
                start_idx, end_idx, far_idx, depth = defect
                start = tuple(contour[start_idx][0])
                end = tuple(contour[end_idx][0])
                far = tuple(contour[far_idx][0])
                angle = angle_between_points(start, end, far)
                if  angle < 90:  # Allow a small margin around 90 degrees
                    count_defects += 1
                    filtered_defects.append(defect)
            
            return filtered_defects,count_defects 
        except Exception as e:
            print(e)