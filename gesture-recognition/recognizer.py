import cv2
import threading
from skimage.color import rgb2gray
from skimage.filters import gaussian, threshold_otsu
from skimage.measure import label, regionprops
import numpy as np
from commonfunctions import *
def Recognizer(capturedFrame):
    # preprocess the frame
    gray_frame = rgb2gray(capturedFrame)
    
    blurred_frame = gaussian(gray_frame, sigma=1) # to remove noise

    thresh_value = threshold_otsu(blurred_frame) # to get the threshold value
    thresh_frame = blurred_frame > thresh_value # to get the binary image
    show_images([gray_frame, blurred_frame, thresh_frame], ['Gray Frame', 'Blurred Frame', 'Thresholded Frame'])
    
    # segment the hand 

    # countour hand outline 

    # convex hull for fingers

    # finger count logic

    # gesture classification

    # W?

