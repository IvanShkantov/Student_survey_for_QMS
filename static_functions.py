from PyQt5.QtWidgets import QSizePolicy

# Цвет из процента
def get_color_from_percent(percent):
    if percent < 50:
        red = 255
        green = int(255 * (percent / 50))
    else:
        red = int(255 * (1 - (percent - 50) / 50))
        green = 255

    return "#{:02X}{:02X}{:02X}".format(red, green, 0)

# Очистка элемента
def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.setParent(None)
            widget.deleteLater()

# Добавление стиля
def add_style(widget, style):
    widget.setStyleSheet(widget.styleSheet() + f"{style}")

# Специальные настройки
def custom_settings(widget, root, place, size, bg):
    if place != -1:
        if place is None:
            root.layout.addWidget(widget)
        elif len(place) == 1:
            root.layout.insertWidget(place[0], widget)
        elif len(place) == 4:
            root.layout.addWidget(widget, place[0], place[1], place[2], place[3])

    if size is not None:
        widget.setSizePolicy(QSizePolicy.Expanding if size[0] == 1 else QSizePolicy.Fixed,
                             QSizePolicy.Expanding if size[1] == 1 else QSizePolicy.Fixed)

    if bg is not None:
        widget.setStyleSheet(f"background-color: {bg};")

# Изменение цвета в анкете
def change_color(but, block, color):
    colors = ["#a2faae", "#d9f7b0", "#f7eeb0", "#f7b0b0"]
    if but.isChecked():
        block.setStyleSheet(
            "#this{background-color: " + colors[color - 1] + "; padding: 10; border: 2px solid black;}")
    else:
        block.setStyleSheet("#this{background-color: #dcdcdc; padding: 10; border: 2px solid black;}")

