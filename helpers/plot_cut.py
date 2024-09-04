import numpy as np
import matplotlib.pyplot as plt


def plot_cut(image: np.ndarray, axis: int = 0, coord: int = 0, show: bool = True):
    """
    Plot a cut of the image along the specified axis.

    Parameters:
    image (np.ndarray): The input image.
    axis (int): The axis along which to plot the cut. 0 means cutting along x-axis, 1 means cutting along y-axis.
    coord (int): The coordinate along the specified axis at which to plot the cut.
    """
    if axis == 0:
        cut = image[coord, :]
    elif axis == 1:
        cut = image[:, coord]
    else:
        raise ValueError("Invalid axis. Must be 0 or 1.")

    print("Cutting along axis", axis, "at coordinate", coord, "on axis" + str(1 - axis))

    plt.plot(cut)

    if show:
        plt.show()
