import click


input_dir_option: click.option() = click.option(
    "--input_dir", type=str, default="images/", prompt="Path to the image folder"
)

is_raw_option: click.option() = click.option(
    "--is_raw", type=bool, default=False, prompt="Are the images in RAW format?"
)

format_option: click.option() = click.option(
    "--format",
    type=click.Choice(["dng", "tiff"], case_sensitive=False),
    default="dng",
    prompt="Image format",
)

center_x_option: click.option() = click.option(
    "--center_x", type=int, prompt="x-cordinate of the LED's center"
)

center_y_option: click.option() = click.option(
    "--center_y", type=int, prompt="y-cordinate of the LED's center"
)

radius_option: click.option = click.option(
    "--radius", type=int, prompt="Radius of the LED"
)

offset_option: click.option() = click.option(
    "--offset", type=int, prompt="Offset for the SNR calculation"
)

kernel_option: click.option() = click.option(
    "--kernel",
    type=click.Choice(["CA", "GB"], case_sensitive=False),
    default="CA",
    prompt="NREA: Low-pass filter used (Circular Averaging or Gaussian Blurring)",
)

kernel_size_option: click.option() = click.option(
    "--kernel_size", type=int, prompt="NREA: Kernel size"
)

crop_factor_option: click.option() = click.option(
    "--crop_factor",
    type=int,
    default=2,
    prompt="Factor by which the images shall be cropped",
)

weight_option: click.option() = click.option(
    "--weight",
    type=float,
    default=0.9,
    prompt="ROF: Weight for ROF denoising",
)

accumulate_option: click.option() = click.option(
    "--accumulate",
    type=bool,
    default=False,
    prompt="NREA: Accumulate images?",
)

normalize_option: click.option() = click.option(
    "--normalize",
    type=bool,
    default=False,
    prompt="NREA: Normalize images?",
)

channel_wise_option: click.option() = click.option(
    "--channel_wise",
    type=bool,
    default=False,
    prompt="Calculate metrics channel-wise?",
)
