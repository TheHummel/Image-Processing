import cv2
import numpy as np
import matplotlib.pyplot as plt
import rawpy

# LOAD THE IMAGE
image_path = ""

# image = cv2.imread(image_path)

with rawpy.imread(image_path) as raw:
    # Convert the raw data to a NumPy array (RGB)
    image = raw.postprocess()

# CONVERT TO GRAYSCALE
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# GAUSSIAN BLURRING
blurred = cv2.GaussianBlur(gray, (7, 7), 2.0)

# THRESHOLDING
threshold = 70
_, thresholded_image = cv2.threshold(blurred, threshold, 255, cv2.THRESH_TOZERO)

# DETECT CIRCLE
# Perform Hough Circle Transform
circles = cv2.HoughCircles(
    thresholded_image,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=1000,  # Increase the minimum distance between circles
    param1=30,  # Higher threshold for Canny edge detector
    param2=20,  # Lower accumulator threshold for the circles
    minRadius=100,
    maxRadius=120,
)

# Print the detected circles
print("Detected circles:", circles)

# Draw the detected circles on the original image
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        # Draw the outer circle
        cv2.circle(image, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # Draw the center of the circle
        cv2.circle(image, (i[0], i[1]), 2, (0, 0, 255), 3)

    # save circles to txt file
    with open("detected_circles.txt", "w") as f:
        for i in circles[0, :]:
            f.write(f"Center: ({i[0]}, {i[1]}), Radius: {i[2]}\n")

# PLOT
plt.figure(figsize=(12, 6))
plt.subplot(121)
plt.imshow(thresholded_image, cmap="gray")
plt.title("Thresholded Image")
plt.axis("off")
plt.subplot(122)
plt.imshow(image)
plt.title("Detected Circles")
plt.axis("off")
plt.show()
