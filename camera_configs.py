# camera name aliases mapping
CAMERA_ALIASES = {
    "HP20": "Huawei P20",
    "X13P": "Xiaomi 13 Pro",
}


class AliasDict(dict):
    """Dictionary that supports aliases for keys"""

    def __init__(self, data, aliases):
        super().__init__(data)
        self.aliases = aliases

    def __getitem__(self, key):
        canonical_key = self.aliases.get(key, key)
        return super().__getitem__(canonical_key)

    def get(self, key, default=None):
        canonical_key = self.aliases.get(key, key)
        return super().get(canonical_key, default)


# low light detection configs
CENTERS = AliasDict(
    {
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
    },
    CAMERA_ALIASES,
)

RADII = AliasDict(
    {
        "Smartphone": 60,
        "Huawei P20": 60,
        "Xiaomi 13 Pro": 60,
        "Arducam": 60,
        "OV": 10,
    },
    CAMERA_ALIASES,
)

# native / custom app comparison configs
CENTERS_NCC = AliasDict(
    {
        # "Xiaomi 13 Pro": {"native": (1540, 2100), "dp20": (2090, 1530)},
        # "Huawei P20": {"native": (1450, 1990), "dp20": (1980, 1560)},
        # "Xiaomi 13 Pro": {"native": (1540, 2050), "dp20": (2050, 1550)},  # 2nd series of images
        "Xiaomi 13 Pro": {
            "NAPP": (1550, 2080),
            "CAPP": (2085, 1510),
        },  # 3rd series of images
    },
    CAMERA_ALIASES,
)

RADII_NCC = AliasDict({"Xiaomi 13 Pro": 60, "Huawei P20": 60}, CAMERA_ALIASES)
