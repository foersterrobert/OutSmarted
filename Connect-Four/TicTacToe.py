import cv2
import numpy as np

# Functions
def imgshow(name,img):
    cv2.imshow(name,img)
    cv2.moveWindow(name,200,200)
    cv2.waitKey(0)

# Read and process image
file_name = "tictactoe.jpg"
img = cv2.imread(file_name)

new_width = 500 # Resize
img_h,img_w,_ = img.shape
scale = new_width / img_w
img_w = int(img_w * scale)
img_h = int(img_h * scale)
img = cv2.resize(img, (img_w,img_h), interpolation = cv2.INTER_AREA)
img_orig = img.copy()
imgshow('Original Image (Resized)', img_orig)

# Bilateral Filter
bilateral_filtered_image = cv2.bilateralFilter(img, 15, 190, 190) 
imgshow('Bilateral Filter', bilateral_filtered_image)

# Outline Edges
edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 150) 
imgshow('Edge Detection', edge_detected_image)


cv2.destroyAllWindows()