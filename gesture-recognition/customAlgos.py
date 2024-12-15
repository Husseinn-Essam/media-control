import cv2
import numpy as np
import math
def convexity_defects(points, hull):
    try:
        points = np.array(points, dtype=np.int32)
        hull = np.array(hull, dtype=np.int32)

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

        rev_orientation = ((hull[1] > hull[0]) + (hull[2] > hull[1]) + (hull[0] > hull[2])) != 2

        hcurr = hull[0] if rev_orientation else hull[-1]

        for i in range(hpoints):
            hnext = hull[hpoints - i - 1] if rev_orientation else hull[i]

            pt0 = points[hcurr]
            pt1 = points[hnext]
            dx0 = pt1[0] - pt0[0]
            dy0 = pt1[1] - pt0[1]
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


