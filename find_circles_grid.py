import cv2
import numpy as np
import matplotlib.pyplot as plt

import click

import rawpy


@click.command()
@click.option(
    "--image_path", default="images/iso100expo30.dng", help="Path to the image file"
)
@click.option("--center_x", default=2055, help="Center x coordinate")
@click.option("--center_y", default=1488, help="Center y coordinate")
@click.option(
    "--grid_cell_width", default=376, help="Tolerance range for circle detection"
)
def find_circles_grid(image_path, center_x, center_y, grid_cell_width):
    # LOAD THE IMAGE
    if not image_path.startswith("images/"):
        image_path = "images/" + image_path

    if image_path.endswith(".dng"):
        with rawpy.imread(image_path) as raw:
            # Convert the raw data to a NumPy array (RGB)
            image = raw.postprocess()
    else:
        image = cv2.imread(image_path)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # CONVERT TO GRAYSCALE
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # GAUSSIAN BLURRING
    blurred = cv2.GaussianBlur(gray, (7, 7), 2.0)

    # THRESHOLDING
    threshold = 30
    _, thresholded_image = cv2.threshold(blurred, threshold, 255, cv2.THRESH_TOZERO)

    # DETECT CIRCLES
    # Perform Hough Circle Transform
    circles = cv2.HoughCircles(
        thresholded_image,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=300,  # Increase the minimum distance between circles
        param1=30,  # Higher threshold for Canny edge detector
        param2=20,  # Lower accumulator threshold for the circles
        minRadius=110,
        maxRadius=140,
    )

    # Print the detected circles
    print("Detected circles:", circles)

    # If circles are detected, draw them on the original image
    # if circles is not None:
    #     circles = np.round(circles[0, :]).astype("int")
    #     for x, y, r in circles:
    #         cv2.circle(image, (x, y), r, (0, 255, 0), 4)
    #         cv2.rectangle(image, (x - 70, y - 70), (x + 70, y + 70), (0, 128, 255), 10)

    # FIND THE GRID
    center = (center_x, center_y)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        detected_grid, added_grid, average_r = find_grid_centers(
            circles, center, grid_cell_width
        )

    for row in detected_grid:
        for x, y in row:
            x, y, average_r = int(x), int(y), int(average_r)
            cv2.circle(image, (x, y), average_r, (0, 255, 0), 4)
            cv2.rectangle(image, (x - 70, y - 70), (x + 70, y + 70), (0, 128, 255), 10)

    print("Added circles:", added_grid)

    # draw added circles
    for x, y in added_grid:
        x, y = int(x), int(y)
        cv2.circle(image, (x, y), average_r, (0, 0, 255), 4)
        cv2.rectangle(image, (x - 70, y - 70), (x + 70, y + 70), (0, 128, 255), 10)

    # PLOT IMAGES
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title("Blurred Image")
    plt.imshow(cv2.cvtColor(thresholded_image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.subplot(1, 2, 2)
    plt.title("Detected Circles")
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()


def calculate_mean_coordinates(grid):
    num_rows = len(grid)
    num_cols = len(grid[0]) if grid else 0

    row_means = []
    col_means = []

    # Calculate mean y coordinates for each row
    for row in grid:
        row_sum = sum(y for item in row if item is not None for x, y in [item])
        row_count = sum(1 for item in row if item is not None)
        if row_count > 0:
            row_means.append(row_sum / row_count)
        else:
            row_means.append(None)

    # Calculate mean x coordinates for each column
    for col in range(num_cols):
        col_sum = 0
        col_count = 0
        for row in range(num_rows):
            if grid[row][col] is not None:
                x, y = grid[row][col]
                col_sum += x
                col_count += 1
        if col_count > 0:
            col_means.append(col_sum / col_count)
        else:
            col_means.append(None)

    # TODO: handle case where there is no circle detected in a row or column (use average distance)

    return row_means, col_means


def calculate_average_distance(grid):
    num_rows = len(grid)
    num_cols = len(grid[0]) if grid else 0

    distances = []

    for r in range(num_rows):
        for c in range(num_cols):
            if grid[r][c] is not None:
                # Check neighboring cells (up, down, left, right)
                total_distance = 0
                count = 0
                if r > 0 and grid[r - 1][c] is not None:  # up
                    total_distance += abs(grid[r][c] - grid[r - 1][c])
                    count += 1
                if r < num_rows - 1 and grid[r + 1][c] is not None:  # down
                    total_distance += abs(grid[r][c] - grid[r + 1][c])
                    count += 1
                if c > 0 and grid[r][c - 1] is not None:  # left
                    total_distance += abs(grid[r][c] - grid[r][c - 1])
                    count += 1
                if c < num_cols - 1 and grid[r][c + 1] is not None:  # right
                    total_distance += abs(grid[r][c] - grid[r][c + 1])
                    count += 1

                if count > 0:
                    avg_distance = total_distance / count
                    distances.append(avg_distance)

    if distances:
        average_distance = sum(distances) / len(distances)
    else:
        average_distance = None

    return average_distance


def find_grid_centers(circles, center, grid_cell_width):
    detected_grid = [[None] * 3 for _ in range(3)]
    added_grid = []
    n_detected_circles = 0
    sum_r = 0

    initial_grid = []

    central_circle = None
    for x, y, r in circles:
        diff = np.abs(x - center[0]) + np.abs(y - center[1])
        if diff < grid_cell_width / 2:
            print(diff)
            central_circle = (x, y)
            print("Center circle found at:", (x, y))

    # create initial grid
    if central_circle is not None:
        for j in range(-1, 2):
            row = []
            for i in range(-1, 2):
                row.append(
                    [
                        central_circle[0] + grid_cell_width * i,
                        central_circle[1] + grid_cell_width * j,
                    ]
                )
            initial_grid.append(row)

    else:
        print("Center circle not found")
        for j in range(-1, 2):
            row = []
            for i in range(-1, 2):
                row.append(
                    [
                        center[0] + grid_cell_width * i,
                        center[1] + grid_cell_width * j,
                    ]
                )
            initial_grid.append(row)

        print("Initial grid:", initial_grid)

    # filter circles
    for x, y, r in circles:
        # check if if respecitve circle is within the grid
        for i in range(3):
            for j in range(3):
                if (
                    np.sqrt(
                        (initial_grid[i][j][0] - x) ** 2
                        + (initial_grid[i][j][1] - y) ** 2
                    )
                    < 100
                ):
                    detected_grid[i][j] = (x, y)
                    n_detected_circles += 1
                    sum_r += r
                    break

    print("Filtered circles:", detected_grid)

    # calculate missing circle centers
    row_means, col_means = calculate_mean_coordinates(detected_grid)
    for i in range(3):
        for j in range(3):
            if detected_grid[i][j] is None:
                added_grid.append((col_means[j], row_means[i]))

    detected_grid = [
        [item for item in row if item is not None] for row in detected_grid
    ]

    return detected_grid, added_grid, sum_r / n_detected_circles


if __name__ == "__main__":
    find_circles_grid()
