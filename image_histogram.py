import cv2
import matplotlib.pyplot as plt
import rawpy
import numpy as np

# Load the image
image = cv2.imread("images/MyImage_1718745368063.jpg")

# image_path = "images/iso100expo30.dng"
# with rawpy.imread(image_path) as raw:
#     # Convert the raw data to a NumPy array (RGB)
#     rgb_image = raw.postprocess()

image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# Convert the image to grayscale (histogram works best with grayscale images)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Calculate the histogram using cv2.calcHist
hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

zero_mask = hist == 0
log_hist = np.where(zero_mask, -1e-8, np.log(hist))

# Plotting all in one figure with subplots
plt.figure(figsize=(12, 8))

# Plot the histogram of the image
plt.subplot(2, 2, 1)
plt.hist(hist, bins=256)  # Adjust bins for finer or coarser visualization
plt.xlabel("Pixel Intensity")
plt.ylabel("Number of Pixels")
plt.title("Histogram of the Image")

# Plot the original image
plt.subplot(2, 2, 2)
plt.imshow(image)
plt.title("Original Image")

# Plot the log histogram
plt.subplot(2, 2, 3)
plt.hist(log_hist, bins=256)
plt.title("Log Histogram")

# Plot the thresholded image
threshold = 50
_, thresholded_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)
plt.subplot(2, 2, 4)
plt.imshow(thresholded_image, cmap="gray")
plt.title("Thresholded Image")

# Show all plots
plt.tight_layout()
plt.show()