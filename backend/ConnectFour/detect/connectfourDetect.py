import cv2
import numpy as np

def detectBoard(image):
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_w, img_h = 500, 500
    img = cv2.resize(img, (img_w,img_h), interpolation = cv2.INTER_AREA)
    
    bilateral_filtered_image = cv2.bilateralFilter(img, 15, 190, 190)
    edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 150) 
    
    contours, hierarchy = cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Edges to contours
    contour_list = []
    rect_list = []
    position_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True) # Contour Polygons
        area = cv2.contourArea(contour)
        rect = cv2.boundingRect(contour) # Polygon bounding rectangles
        x_rect,y_rect,w_rect,h_rect = rect
        x_rect +=  w_rect/2
        y_rect += h_rect/2
        area_rect = w_rect*h_rect
        
        if ((len(approx) > 8) & (len(approx) < 23) & (area > 250) & (area_rect < (img_w*img_h)/5)) & (w_rect in range(h_rect-10,h_rect+10)): # Circle conditions
            contour_list.append(contour)
            position_list.append((x_rect,y_rect))
            rect_list.append(rect)

    img_circle_contours = img.copy()
    cv2.drawContours(img_circle_contours, contour_list,  -1, (0,255,0), thickness=1) # Display Circles
    for rect in rect_list:
        x,y,w,h = rect
        cv2.rectangle(img_circle_contours,(x,y),(x+w,y+h),(0,0,255),1)

    # Interpolate Grid
    rows, cols = (6,7)
    mean_w = sum([rect[2] for r in rect_list]) / len(rect_list)
    mean_h = sum([rect[3] for r in rect_list]) / len(rect_list)
    position_list.sort(key = lambda x:x[0])
    max_x = int(position_list[-1][0])
    min_x = int(position_list[0][0])
    position_list.sort(key = lambda x:x[1])
    max_y = int(position_list[-1][1])
    min_y = int(position_list[0][1])
    grid_width = max_x - min_x
    grid_height = max_y - min_y
    col_spacing = int(grid_width / (cols-1))
    row_spacing = int(grid_height / (rows - 1))

    # Find Colour Masks
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # Convert to HSV space

    lower_red = np.array([150, 150, 100])  # Lower range for red colour space
    upper_red = np.array([255, 255, 255])  # Upper range for red colour space
    mask_red = cv2.inRange(img_hsv, lower_red, upper_red)

    lower_yellow = np.array([10, 150, 100])
    upper_yellow = np.array([60, 255, 255])
    mask_yellow = cv2.inRange(img_hsv, lower_yellow, upper_yellow)

    grid = np.zeros((rows,cols))
    id_red = 1
    id_yellow = -1
    img_grid_overlay = img.copy()

    for x_i in range(0,cols):
        x = int(min_x + x_i * col_spacing)
        for y_i in range(0,rows):
            y = int(min_y + y_i * row_spacing)
            r = int((mean_h + mean_w)/5)
            img_grid_circle = np.zeros((img_h, img_w))
            cv2.circle(img_grid_circle, (x,y), r, (255,255,255),thickness=-1)
            img_res_red = cv2.bitwise_and(img_grid_circle, img_grid_circle, mask=mask_red)
            img_grid_circle = np.zeros((img_h, img_w))
            cv2.circle(img_grid_circle, (x,y), r, (255,255,255),thickness=-1)
            img_res_yellow = cv2.bitwise_and(img_grid_circle, img_grid_circle,mask=mask_yellow)
            cv2.circle(img_grid_overlay, (x,y), r, (0,255,0),thickness=1)
            if img_res_red.any() != 0:
                grid[y_i][x_i] = id_red
            elif img_res_yellow.any() != 0 :
                grid[y_i][x_i] = id_yellow
    cv2.imwrite('image.png', img_grid_overlay)
    return grid.astype(int)