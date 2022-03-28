import cv2
import numpy as np

def pre_processing(img):
    img = cv2.pyrMeanShiftFiltering(src=img, sp=11, sr=43)
    img = cv2.GaussianBlur(img, (7, 7), 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((5, 5), np.uint8)
    img = cv2.erode(img, kernel)
    return img

def build_around_to_500(img):
    new_img = np.ones((500, 500), np.uint8)
    new_img.fill(255)
    counter = 0
    for i in range(len(new_img)):
        if 10 <= i < 490:
            new_img[i][10:490] = img[counter]
            counter += 1
    return new_img

def find_maxes(data, how_many):
    tmp_list = data.copy()
    tmp_list.sort()
    return tmp_list[-how_many:]
    
def find_biggest_contours_indices(contours, how_many):
    sizes = []
    indices = []
    for i in range(len(contours)):
        sizes.append(cv2.contourArea(contours[i]))
    maxes = find_maxes(sizes, how_many)
    for i in range(how_many):
        indices.append(sizes.index(maxes[i]))
    return indices

def filter_contours(contour_vector, hierarchy_vector, how_many_biggest_to_ignore):
    if 0 < how_many_biggest_to_ignore <= len(contour_vector):
        contours = []
        indices = find_biggest_contours_indices(contour_vector, how_many_biggest_to_ignore)
        for i in range(len(contour_vector)):
            if cv2.contourArea(contour_vector[i]) > 300:
                if i in indices:
                    continue
                elif hierarchy_vector[0][i][3] in indices:
                    contours.append(contour_vector[i])
        return contours
    else:
        return contour_vector

def find_contours(img, how_many_biggest_to_ignore):
    contour_vector, hierarchy_vector = cv2.findContours(image=img, mode=cv2.RETR_TREE,
                                                           method=cv2.CHAIN_APPROX_SIMPLE)
    contours = filter_contours(contour_vector, hierarchy_vector, how_many_biggest_to_ignore)
    return contours

def move_contours_back_to_480(contours):
    for i in range(len(contours)):
        for j in range(len(contours[i])):
            contours[i][j][0][0] -= 10
            contours[i][j][0][1] -= 10
    return contours

def recognize_contour_type(contour):
    poly = get_approx_poly(contour)
    is_convex = cv2.isContourConvex(poly)
    contour_type = "unknown"
    if is_convex:
        contour_type = 1
    elif not is_convex:
        contour_type = -1
    return contour_type

def get_approx_poly(contour):
    epsilon = 0.05 * cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, epsilon, True)

def find_digital_game_array(contours, recognize_contour_type):
    array = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for contour in range(len(contours)):
        for i in range(3):
            for j in range(3):
                contour_inside = get_contour_inside_area(contours[contour], [j * 160, i * 160],
                                                         [j * 160 + 160, i * 160 + 160])
                if len(contour_inside) > 0:
                    original_poly_participation = cv2.contourArea(contour_inside) / cv2.contourArea(contours[contour])
                    if original_poly_participation > 0.6:
                        array[i][j] = recognize_contour_type(contours[contour])
    return array

def get_contour_inside_area(contour, left_top_corner, right_bottom_corner):
    if check_if_belongs(contour, left_top_corner, right_bottom_corner):
        new_contour_elements = []

        points_over_top_edge = get_points_over_top_edge(contour, left_top_corner[1])
        points_below_bottom_edge = get_points_below_bottom_edge(contour, right_bottom_corner[1])
        points_behind_left_edge = get_points_behind_left_edge(contour, left_top_corner[0])
        points_behind_right_edge = get_points_behind_right_edge(contour, right_bottom_corner[0])

        left_top_corner_intersection = []
        if points_over_top_edge and points_behind_left_edge:
            left_top_corner_intersection = find_intersection(points_over_top_edge, points_behind_left_edge)

        right_top_corner_intersection = []
        if points_over_top_edge and points_behind_right_edge:
            right_top_corner_intersection = find_intersection(points_over_top_edge, points_behind_right_edge)

        left_bottom_corner_intersection = []
        if points_below_bottom_edge and points_behind_left_edge:
            left_bottom_corner_intersection = find_intersection(points_below_bottom_edge, points_behind_left_edge)

        right_bottom_corner_intersection = []
        if points_below_bottom_edge and points_behind_right_edge:
            right_bottom_corner_intersection = find_intersection(points_below_bottom_edge, points_behind_right_edge)

        # LEFT TOP CORNER
        if left_top_corner_intersection:
            new_contour_elements.append(left_top_corner)
            for i in range(len(contour)):
                if contour[i][0][0] > left_top_corner[0] and contour[i][0][1] > left_top_corner[1]:
                    new_contour_elements.append([contour[i][0][0], contour[i][0][1]])

        # RIGHT TOP CORNER
        elif right_top_corner_intersection:
            new_contour_elements.append([right_bottom_corner[0], left_top_corner[1]])
            for i in range(len(contour)):
                if contour[i][0][0] < right_bottom_corner[0] and contour[i][0][1] > left_top_corner[1]:
                    new_contour_elements.append([contour[i][0][0], contour[i][0][1]])

        # LEFT BOTTOM CORNER
        elif left_bottom_corner_intersection:
            new_contour_elements.append([left_top_corner[0], right_bottom_corner[1]])
            for i in range(len(contour)):
                if contour[i][0][0] > left_top_corner[0] and contour[i][0][1] < right_bottom_corner[1]:
                    new_contour_elements.append([contour[i][0][0], contour[i][0][1]])

        # RIGHT BOTTOM CORNER
        elif right_bottom_corner_intersection:
            new_contour_elements.append(right_bottom_corner)
            for i in range(len(contour)):
                if contour[i][0][0] < right_bottom_corner[0] and contour[i][0][1] < right_bottom_corner[1]:
                    new_contour_elements.append([contour[i][0][0], contour[i][0][1]])

        # OVER TOP EDGE
        elif points_over_top_edge:
            for i in range(len(contour)):
                tmp = [contour[i][0][0], contour[i][0][1]]
                if tmp not in points_over_top_edge:
                    new_contour_elements.append(tmp)

        # BELOW BOTTOM EDGE
        elif points_below_bottom_edge:
            for i in range(len(contour)):
                tmp = [contour[i][0][0], contour[i][0][1]]
                if tmp not in points_below_bottom_edge:
                    new_contour_elements.append(tmp)

        # BEHIND LEFT EDGE
        elif points_behind_left_edge:
            for i in range(len(contour)):
                tmp = [contour[i][0][0], contour[i][0][1]]
                if tmp not in points_behind_left_edge:
                    new_contour_elements.append(tmp)

        # BEHIND RIGHT EDGE
        elif points_behind_right_edge:
            for i in range(len(contour)):
                tmp = [contour[i][0][0], contour[i][0][1]]
                if tmp not in points_behind_right_edge:
                    new_contour_elements.append(tmp)
        else:
            return contour
            
        new_contour = np.array(new_contour_elements).reshape((-1, 1, 2)).astype(np.int32)
        return new_contour
    else:
        return []

def check_if_belongs(contour, left_top_corner, right_bottom_corner):
    for i in range(len(contour)):
        if left_top_corner[0] <= contour[i][0][0] <= right_bottom_corner[0] and left_top_corner[1] <= contour[i][0][1] \
                <= right_bottom_corner[1]:
            return True
    return False

def get_points_over_top_edge(contour, y):
    if y > 0:
        points = []
        for i in range(len(contour)):
            if contour[i][0][1] < y:
                tmp = [contour[i][0][0], contour[i][0][1]]
                points.append(tmp)
        return points
    else:
        return []

def get_points_below_bottom_edge(contour, y):
    if y < 480:
        points = []
        for i in range(len(contour)):
            if contour[i][0][1] > y:
                tmp = [contour[i][0][0], contour[i][0][1]]
                points.append(tmp)
        return points
    else:
        return []

def get_points_behind_left_edge(contour, x):
    if x > 0:
        points = []
        for i in range(len(contour)):
            if contour[i][0][0] < x:
                tmp = [contour[i][0][0], contour[i][0][1]]
                points.append(tmp)
        return points
    else:
        return []

def get_points_behind_right_edge(contour, x):
    if x < 480:
        points = []
        for i in range(len(contour)):
            if contour[i][0][0] > x:
                tmp = [contour[i][0][0], contour[i][0][1]]
                points.append(tmp)
        return points
    else:
        return []

def find_intersection(list1, list2):
    intersectiong_list = []
    for i in range(len(list1)):
        if list1[i] in list2:
            intersectiong_list.append(list1[i])
    return intersectiong_list


