import seaborn as sns
import matplotlib.pyplot as plt

# font
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial"]

# Palette 1C7B8B, https://venngage.com/tools/accessible-color-palette-generator
CUSTOM_PALETTE = sns.color_palette(
    ["#b8a719", "#8c750a", "#1c7b8b", "#0c5463", "#9348a4"]
)  # #5d226f
marker_size = 1.2
line_width = 1

# figure dimensions
FIG_WIDTH_MM = 95
FIG_HEIGHT_MM = 55


def create_figure(subplot_layout=(1, 1), height_ratios=None):
    """
    Create a matplotlib figure with specified dimensions and layout.

    Args:
        subplot_layout (tuple): Number of rows and columns for subplots (default: (1, 1)).
        height_ratios (list): Ratios of subplot heights if using multiple rows.

    Returns:
        fig, axes: The created matplotlib figure and axes.
    """
    fig, axes = plt.subplots(
        *subplot_layout,
        # figsize=(FIG_WIDTH_MM / 25.4, FIG_HEIGHT_MM / (25.4)),
        figsize=(FIG_WIDTH_MM / 10, FIG_HEIGHT_MM / (10)),
        gridspec_kw={"height_ratios": height_ratios}
    )
    return fig, axes


def configure_axes(ax, xlabel="", ylabel="", legend_title=""):
    """
    Apply common styling and labels to a given axis.

    Args:
        ax: Matplotlib axis to configure.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        legend_title (str): Title for the legend.
    """
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if ax.get_legend():
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(
            handles[: len(labels)],
            labels[: len(labels)],
            title=legend_title,
            loc="upper left",
            bbox_to_anchor=(0, 1),
            frameon=True,
        )
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)


def save_plot(output_path):
    """
    Save a matplotlib figure to a file with specified DPI and tight bounding box.

    Args:
        fig: Matplotlib figure to save.
        output_path (str): Path to save the figure to.
    """
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
