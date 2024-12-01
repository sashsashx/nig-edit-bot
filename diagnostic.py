import os
from PIL import Image

HAND_ACCESSORIES = {
    "Phantom": "images/hand/phantom.png",
    "Uzi": "images/hand/uzi.png",
    "Cash": "images/hand/cash.png",
    "US Flag": "images/hand/US_flag.png",
}

HEAD_ACCESSORIES = {
    "Stone Island": "images/head/stone_island.png",
    "Blunt": "images/head/blunt.png",
    "Glasses": "images/head/glasses.png",
    "BK Crown": "images/head/BK_crown.png",
}

LEG_ACCESSORIES = {
    "Elf": "images/leg/elf.png",
}

BACKGROUNDS = {
    "Matrix": "images/background/matrix.png",
    "Mario": "images/background/mario.png",
    "Windows": "images/background/windows.png",
    "Strip": "images/background/strip.png",
    "MLK": "images/background/MLK.png",
}

BASE_IMAGE_PATH = "images/nig.png"

def check_files():
    print("Checking base image...")
    if not os.path.exists(BASE_IMAGE_PATH):
        print(f"Base image not found: {BASE_IMAGE_PATH}")
    else:
        print("Base image found.")

    for category, files in [
        ("Hand Accessories", HAND_ACCESSORIES),
        ("Head Accessories", HEAD_ACCESSORIES),
        ("Leg Accessories", LEG_ACCESSORIES),
        ("Backgrounds", BACKGROUNDS),
    ]:
        print(f"\nChecking {category}...")
        for name, path in files.items():
            if not os.path.exists(path):
                print(f"❌ {name} not found: {path}")
            else:
                try:
                    Image.open(path)
                    print(f"✔️ {name} is valid.")
                except Exception as e:
                    print(f"❌ {name} is invalid: {e}")

if __name__ == "__main__":
    check_files()
