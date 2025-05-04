import customtkinter
import numpy as np
from scipy.optimize import minimize
import os
from PIL import Image

def calculate_position_2d(beacon_positions, distances, x_bounds=(0, 8192), y_bounds=(0, 6144)):
    def error_function(position):
        x, y = position
        error = np.sum([(np.sqrt((x - beacon_positions[i, 0])**2 + (y - beacon_positions[i, 1])**2) - distances[i])**2
                       for i in range(len(beacon_positions))])
        return error

    initial_guess = np.mean(beacon_positions, axis=0)
    bounds = (x_bounds, y_bounds)
    result = minimize(error_function, initial_guess, method='L-BFGS-B', bounds=bounds,
                     options={'ftol': 1e-9, 'gtol': 1e-9})

    if result.success:
        x, y = result.x
        return x, y
    else:
        print("Оптимизация не удалась:", result.message)
        return None


def calculate_and_display_coordinates():
    try:
        distances = [float(entry.get()) for entry in distances_entries]
    except ValueError:
        result_label_coordinates.configure(text="Ошибка: Введите числа в поля расстояний.")
        return

    if any(d > 10241 for d in distances):
        result_label_coordinates.configure(text="Ошибка: Неправильно введены расстояния для маяков, слишком большие значения (> 10241).", wraplength=350)
        return


    if any(d < 0 for d in distances):
        result_label_coordinates.configure(text="Ошибка: Расстояния должны быть неотрицательными.", wraplength=350)
        return

    position = calculate_position_2d(beacon_positions, distances, x_bounds, y_bounds)

    if position:
        result_label_coordinates.configure(text="Вычисленные координаты: x={:.2f}, y={:.2f}".format(*position), wraplength=350)
    else:
        result_label_coordinates.configure(text="Не удалось вычислить координаты.", wraplength=350)


def calculate_distances(x, y, beacon_positions):
  distances = []
  for beacon in beacon_positions:
    distance = np.sqrt((x - beacon[0])**2 + (y - beacon[1])**2)
    distances.append(distance)
  return distances

def calculate_and_display_distances():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
    except ValueError:
        result_label_distances.configure(text="Ошибка: Введите числа в поля координат.", wraplength=350)
        return

    if x > 8193 or y > 6145:
        result_label_distances.configure(text="Ошибка: Координаты X и Y не могут быть больше 8193 и 6145 соответственно.", wraplength=350)
        return

    distances = calculate_distances(x, y, beacon_positions)

    result_text = (
        f"Маяк №1 (Красный) = {distances[0]:.2f}\n"
        f"Маяк №2 (Зеленый) = {distances[1]:.2f}\n"
        f"Маяк №3 (Синий) = {distances[2]:.2f}\n"
        f"Маяк №4 (Желтый) = {distances[3]:.2f}"
    )

    result_label_distances.configure(text=result_text, justify="left", wraplength=350)

def move_window(event):
    root.geometry(f'+{event.x_root - startX}+{event.y_root - startY}')

def press_window(event):
    global startX, startY
    startX = event.x
    startY = event.y


if __name__ == "__main__":
    beacon_positions = np.array([
        [0, 0],
        [8192, 0],
        [8192, 6144],
        [0, 6144]
    ])

    x_bounds = (0, 8192)
    y_bounds = (0, 6144)

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")

    root = customtkinter.CTk()
    root.title("ScrapCoords")
    root.geometry("400x600")
    root.resizable(False, False)

    bg_color = "#29282a"
    menu_color = "#212022"
    border_color = "#2b2e31"
    text_color = "white"
    entry_bg_color = "#302e2f"
    entry_border_color = "#444345"

    main_frame = customtkinter.CTkFrame(root, corner_radius=0, fg_color=bg_color)
    main_frame.pack(fill="both", expand=True)

    top_frame = customtkinter.CTkFrame(main_frame, height=30, corner_radius=0, fg_color=menu_color)
    top_frame.pack(fill="x")

    top_frame.bind("<B1-Motion>", move_window)
    top_frame.bind("<ButtonPress-1>", press_window)

    try:
        icon_image = customtkinter.CTkImage(Image.open("textures/icon.png"), size=(20, 20))
    except FileNotFoundError:
        print("Не найден файл icon.png в директории textures/. Иконка отображаться не будет.")
        icon_image = None

    if icon_image:
        icon_label = customtkinter.CTkLabel(top_frame, image=icon_image, text="", fg_color="transparent")
        icon_label.pack(side="left", padx=(10, 0))
    title_label = customtkinter.CTkLabel(top_frame, text="ScrapCoords", fg_color="transparent", text_color=text_color)
    title_label.pack(side="left", padx=10)

    try:
        close_image = customtkinter.CTkImage(Image.open("textures/close.png"), size=(20, 20))
    except FileNotFoundError:
        print("Не найден файл close.png в директории textures/. Будет использован текстовый крестик.")
        close_image = None

    if close_image:
        close_button = customtkinter.CTkButton(top_frame, image=close_image, text="", width=30, height=30,
                                            fg_color="transparent", hover_color="#505050", command=root.destroy, border_width=0)
    else:
        close_button = customtkinter.CTkButton(top_frame, text="X", width=30, height=30,
                                            fg_color="transparent", hover_color="#505050", command=root.destroy, border_width=0, text_color=text_color)


    close_button.pack(side="right", padx=10)

    tabview = customtkinter.CTkTabview(main_frame, fg_color=bg_color)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tabview.add("Координаты")
    tabview.add("Расстояния")

    direction_info = """
    +X - Между зелёным и синим маяком
    -X - Между Жёлтым и красным маяком
    +Y - Между жёлтым и синим маяком
    -Y - Между зелёным и красным маяком
    """
    direction_label = customtkinter.CTkLabel(tabview.tab("Координаты"), text=direction_info, justify="left", text_color=text_color, fg_color="transparent")
    direction_label.pack(pady=10)

    distances_entries = []
    colors = ["Красный", "Зелёный", "Синий", "Жёлтый"]
    placeholders = [f"Расстояние до маяка №{i+1} ({color})" for i, color in enumerate(colors)]

    for i, (color, placeholder) in enumerate(zip(colors, placeholders)):
        label = customtkinter.CTkLabel(tabview.tab("Координаты"), text=f"Расстояние до маяка №{i+1} ({color}):", text_color=text_color, fg_color="transparent")
        label.pack()
        entry = customtkinter.CTkEntry(tabview.tab("Координаты"), width=200, placeholder_text=placeholder,
                                      fg_color=entry_bg_color, text_color=text_color, border_color=entry_border_color)
        distances_entries.append(entry)
        entry.pack(pady=5)

    calculate_coordinates_button = customtkinter.CTkButton(tabview.tab("Координаты"), text="Вычислить координаты", command=calculate_and_display_coordinates,
                                            fg_color=menu_color, text_color=text_color, border_width=0, corner_radius=8)
    calculate_coordinates_button.pack(pady=10)

    result_label_coordinates = customtkinter.CTkLabel(tabview.tab("Координаты"), text="", text_color=text_color, fg_color="transparent", wraplength=350)
    result_label_coordinates.pack(pady=10)


    direction_info_distances = """
    +X - Между зелёным и синим маяком
    -X - Между Жёлтым и красным маяком
    +Y - Между жёлтым и синим маяком
    -Y - Между зелёным и красным маяком
    """
    direction_label_distances = customtkinter.CTkLabel(tabview.tab("Расстояния"), text=direction_info_distances, justify="left", text_color=text_color, fg_color="transparent", wraplength=350)
    direction_label_distances.pack(pady=10)

    x_label = customtkinter.CTkLabel(tabview.tab("Расстояния"), text="Координата X:", text_color=text_color, fg_color="transparent")
    x_label.pack()
    x_entry = customtkinter.CTkEntry(tabview.tab("Расстояния"), width=200, placeholder_text="Введите координату X",
                                      fg_color=entry_bg_color, text_color=text_color, border_color=entry_border_color)
    x_entry.pack(pady=5)

    y_label = customtkinter.CTkLabel(tabview.tab("Расстояния"), text="Координата Y:", text_color=text_color, fg_color="transparent")
    y_label.pack()
    y_entry = customtkinter.CTkEntry(tabview.tab("Расстояния"), width=200, placeholder_text="Введите координату Y",
                                      fg_color=entry_bg_color, text_color=text_color, border_color=entry_border_color)
    y_entry.pack(pady=5)

    calculate_distances_button = customtkinter.CTkButton(tabview.tab("Расстояния"), text="Вычислить расстояния", command=calculate_and_display_distances,
                                            fg_color=menu_color, text_color=text_color, border_width=0, corner_radius=8)
    calculate_distances_button.pack(pady=10)

    result_label_distances = customtkinter.CTkLabel(tabview.tab("Расстояния"), text="", text_color=text_color, fg_color="transparent", justify="left", wraplength=350)
    result_label_distances.pack(pady=10)


    if os.path.exists("icon.ico"):
        try:
            root.iconbitmap("icon.ico")
        except:
            print("Не удалось установить иконку.")

    root.mainloop()