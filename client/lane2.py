import cv2
import numpy as np

def preprocess_image(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    luminance = np.mean(gray)

    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform Canny edge detection
    edges = cv2.Canny(blur, 50, 150)

    return edges, luminance

def region_of_interest(image):
    global height
    height, width = image.shape
    mask = np.zeros_like(image)

    # Define the vertices of the ROI (triangle or trapezoid)
    
    area = np.array([[(0, height), (0, height//1.7),(width , height//1.7), (width, height)]], dtype=np.int32)
    triangle = np.array([[(0, height/1.2), (width / 2, height/2), (width, height)]], dtype=np.int32)


    # Fill the ROI with white color (255)
    cv2.fillPoly(mask, area , 255)

    # Bitwise AND between the edges image and the ROI mask
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image

def detect_lanes(image, edges):
    # Use the Hough transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=50)

    # Create an empty image to draw the lines on
    lines_image = np.zeros_like(image)

    left_slope = []
    right_slope = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            cv2.line(lines_image, (x1, y1), (x2, y2), (0, 0, 255), 4)

            # take slope of frame less than h/2 not whole frame for accuracy
            # if y1< height/2 and y2<height/2:
            #  Check if x2 and x1 are equal to avoid division by zero
            if x2 != x1 :
                slope = (y2 - y1) / (x2 - x1)

                # Classify the lines based on their slope
                if slope < 0:
                    left_slope.append(slope)
                else:
                    right_slope.append(slope)

            # cv2.line(lines_image, (x1, y1), (x2, y2), (0, 0, 255), 4)

    # Calculate the average slope for left and right lines
    left_slope_avg = np.mean(left_slope) if len(left_slope) > 0 else None
    right_slope_avg = np.mean(right_slope) if len(right_slope) > 0 else None

    return lines_image, left_slope_avg, right_slope_avg


def mainn(frame):     
    
    # Preprocess the frame and get luminance value
    edges, luminance = preprocess_image(frame)

    # Check the luminance value
    if luminance > 50:
        masked_edges = region_of_interest(edges)

        # Detect and draw the lanes
        # lines_image = detect_lanes(frame, masked_edges)
        lines_image, left_slope_avg, right_slope_avg = detect_lanes(frame, masked_edges)
        # print("Left slope:", left_slope_avg, ", Right slope:", right_slope_avg)


        if left_slope_avg is not None and right_slope_avg is not None:
            if left_slope_avg < -0.2 and right_slope_avg < 0.2:
                curve_direction = " Turn Left"
            elif left_slope_avg > -0.2 and right_slope_avg > 0.2:
                curve_direction = "Turn Right"
            # else:
            #     curve_direction = "Stay Straight"
        if left_slope_avg is not None and right_slope_avg is None  :
            if  left_slope_avg < -0.6 :   
                curve_direction = "l Turn Left"
            elif left_slope_avg > -0.4:
                curve_direction = "l Turn Right"
            else:
                curve_direction = "l Stay Straight"
            
        elif  right_slope_avg is not None and left_slope_avg is None :
            if right_slope_avg < -0.5  :  
                curve_direction = "r Turn Right"
            elif right_slope_avg > 0.2:    
                curve_direction = "r Turn Left"
            else:
                curve_direction = "r Stay Straight"  
        else:
                curve_direction = "k Stay Straight" 

        # Display the curve direction on the frame
        height, width, _ = frame.shape
        cv2.putText(frame, curve_direction, (width//2 - 50, height//2 + 130), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
        # cv2.putText(frame,  f"Left: {left_slope_avg:.2f}", (150,  110), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
        # cv2.putText(frame,  f"Right: {right_slope_avg:.2f}", (150, 90), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)

        cv2.line(frame, (width//2, height), (width//2, height//2 + 150), (255, 0, 255), 2)

        # Find obstacles
        contours, _ = cv2.findContours(masked_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through the contours and filter out small ones
        min_contour_area = 800  # Minimum area to consider as an obstacle
        obstacles = []
        for contour in contours:
            if cv2.contourArea(contour) < min_contour_area:
                obstacles.append(contour)
                # Get the centroid of the contour
                M = cv2.moments(contour)
                if M["m00"] > 450.0:
                 cX = int(M["m10"] / M["m00"])
                 cY = int(M["m01"] / M["m00"])
        
                #  cv2.drawContours(frame, obstacles, -1, (0, 255, 0), 2)
                 if cX - width // 2 < 100 and width // 2 - cX < 100:
                        # if cY < height :
                            cv2.drawContours(frame, obstacles, -1, (0, 255, 0), 2)
                            cv2.putText(frame, "STOP !!!", (width // 2 - 30, height // 2 + 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)

               
        # Combine the lines image and obstacle rectangles with the original frame
        result = cv2.addWeighted(frame, 0.8, lines_image, 1, 0)
        
        # Display the result
        cv2.imshow("Lane Detection", result)
        
        return result

    else:
        cv2.putText(frame, "Light too dim", (320,  300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        cv2.imshow("Lane Detection", frame)






            
