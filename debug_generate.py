import os
from PIL import Image

# Пути к файлам
BASE_IMAGE_PATH = "images/nig.png"
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

# Проверяем базовое изображение
print("Проверяем базовое изображение...")
if not os.path.exists(BASE_IMAGE_PATH):
    print(f"❌ Базовое изображение {BASE_IMAGE_PATH} не найдено!")
else:
    print("✔️ Базовое изображение найдено.")

# Проверяем фоны
print("\nПроверяем фоны...")
for name, path in BACKGROUNDS.items():
    if not os.path.exists(path):
        print(f"❌ Фон '{name}' ({path}) не найден!")
    else:
        print(f"✔️ Фон '{name}' найден.")

# Проверяем аксессуары
def check_accessories(category_name, accessories):
    print(f"\nПроверяем аксессуары для {category_name}...")
    for name, path in accessories.items():
        if not os.path.exists(path):
            print(f"❌ Аксессуар '{name}' ({path}) не найден!")
        else:
            print(f"✔️ Аксессуар '{name}' найден.")

check_accessories("Hand", HAND_ACCESSORIES)
check_accessories("Head", HEAD_ACCESSORIES)
check_accessories("Leg", LEG_ACCESSORIES)

# Попробуем сгенерировать изображение
print("\nТестируем генерацию изображения...")
try:
    base_image = Image.open(BASE_IMAGE_PATH).convert("RGBA")

    # Пример выбора пользователя
    user_selection = {
        "background": "Matrix",
        "hand": "Phantom",
        "head": "Blunt",
        "leg": "Elf",
    }

    # Добавляем фон
    background_file = BACKGROUNDS.get(user_selection["background"])
    if background_file:
        background = Image.open(background_file).resize(base_image.size).convert("RGBA")
        base_image = Image.alpha_composite(background, base_image)
        print(f"✔️ Фон '{user_selection['background']}' добавлен.")

    # Добавляем аксессуары
    positions = {
        "hand": {"Phantom": ([3, 242], 0.3)},
        "head": {"Blunt": ([258, 252], 0.3)},
        "leg": {"Elf": ([240, 183], 0.3)},
    }

    for category, item in user_selection.items():
        if category == "background" or not item:
            continue
        position, scale = positions.get(category, {}).get(item, ([0, 0], 1.0))
        accessory_file = (
            HAND_ACCESSORIES.get(item)
            or HEAD_ACCESSORIES.get(item)
            or LEG_ACCESSORIES.get(item)
        )
        if accessory_file and os.path.exists(accessory_file):
            accessory = Image.open(accessory_file).convert("RGBA")
            accessory = accessory.resize(
                (int(accessory.width * scale), int(accessory.height * scale))
            )
            base_image.paste(accessory, position, accessory)
            print(f"✔️ Аксессуар '{item}' для категории '{category}' добавлен.")
        else:
            print(f"❌ Аксессуар '{item}' для категории '{category}' не найден.")

    # Сохраняем изображение
    output_path = "output/debug_result.png"
    os.makedirs("output", exist_ok=True)
    base_image.save(output_path)
    print(f"✔️ Изображение успешно сохранено в {output_path}")

except Exception as e:
    print(f"❌ Ошибка во время генерации изображения: {e}")
