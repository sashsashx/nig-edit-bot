import tkinter as tk
from PIL import Image, ImageTk

# Настройки файлов
BASE_IMAGE = "images/nig.png"  # Базовое изображение
ACCESSORY = {"Stone Island": "images/head/stone_island.png"}

# Класс для работы с интерфейсом
class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Accessory Placement Tool")

        # Загрузка базового изображения
        self.base_image = Image.open(BASE_IMAGE)

        # Инициализация текущего аксессуара
        self.current_accessory_name = list(ACCESSORY.keys())[0]
        self.current_accessory_path = ACCESSORY[self.current_accessory_name]
        self.accessory_image = Image.open(self.current_accessory_path)

        # Начальные параметры
        self.scale = 1.0
        self.position = [50, 50]
        self.results = {}  # Для хранения настроек

        # Преобразование базового изображения для Tkinter
        self.base_tk = ImageTk.PhotoImage(self.base_image)

        # Создание холста для отображения
        self.canvas = tk.Canvas(root, width=self.base_image.width, height=self.base_image.height)
        self.canvas.pack()

        # Отображение базового изображения
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.base_tk)

        # Отображение аксессуара
        self.update_accessory()

        # Элементы управления
        self.create_controls()

        # Перетаскивание мышью
        self.canvas.bind("<B1-Motion>", self.move_accessory)

    def create_controls(self):
        frame = tk.Frame(self.root)
        frame.pack()

        # Кнопки увеличения и уменьшения
        btn_zoom_in = tk.Button(frame, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.pack(side=tk.LEFT)

        btn_zoom_out = tk.Button(frame, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.pack(side=tk.LEFT)

        # Кнопка получения координат текущего аксессуара
        btn_get_coords = tk.Button(frame, text="Get Coordinates", command=self.get_coordinates)
        btn_get_coords.pack(side=tk.LEFT)

    def move_accessory(self, event):
        # Перемещение аксессуара мышью
        self.position = [event.x, event.y]
        self.canvas.coords(self.accessory_id, *self.position)

    def zoom_in(self):
        # Увеличение размера
        self.scale += 0.1
        self.update_accessory()

    def zoom_out(self):
        # Уменьшение размера
        self.scale = max(0.1, self.scale - 0.1)  # Не позволяем масштаб быть меньше 0.1
        self.update_accessory()

    def update_accessory(self):
        # Обновление изображения аксессуара
        resized_accessory = self.accessory_image.resize((int(self.accessory_image.width * self.scale),
                                                         int(self.accessory_image.height * self.scale)))
        self.accessory_tk = ImageTk.PhotoImage(resized_accessory)
        if hasattr(self, "accessory_id"):
            self.canvas.itemconfig(self.accessory_id, image=self.accessory_tk)
            self.canvas.coords(self.accessory_id, *self.position)
        else:
            self.accessory_id = self.canvas.create_image(*self.position, anchor=tk.NW, image=self.accessory_tk)

    def get_coordinates(self):
        # Печать координат и масштаба текущего аксессуара
        print(f"{self.current_accessory_name}: Position: {self.position}, Scale: {self.scale}")
        tk.Label(self.root, text=f"{self.current_accessory_name}: Position: {self.position}, Scale: {self.scale}").pack()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    editor = ImageEditor(root)
    root.mainloop()
