# low light detection configs
CENTERS = {
    "Huawei P20": {
        "original": (1440, 2040),
        "cropped2": (720, 800),
    },
    "Xiaomi 13 Pro": {
        "original": (1540, 2070),
        "cropped4": (370, 390),
    },
    "Arducam": (1250, 1060),
    "OV": (160, 145),
}

RADII = {
    "Smartphone": 80,
    "Arducam": 80,
    "OV": 10,
}

# native / custom app comparison configs
CENTERS_NCC = {
    # "X13P": {"native": (1540, 2100), "dp20": (2090, 1530)},
    # "HP20": {"native": (1450, 1990), "dp20": (1980, 1560)},
    "X13P": {"native": (1540, 2050), "dp20": (2050, 1550)},  # 2nd series of images
}
RADII_NCC = {"X13P": 80, "HP20": 80}
