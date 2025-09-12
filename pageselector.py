from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QFrame, QLineEdit, QComboBox
)
from animated_button import AnimatedButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import sys
import os
import subprocess

src_dir = os.path.dirname(os.path.abspath(__file__))
editor_path = ""

# Read from editorpath to get selected folder
with open("editorpath.txt", 'r') as file:
    editor_path = file.read().strip()
    print(f"Editor path loaded: {editor_path}")

# UI setup



app = QApplication([])

# Set application icon
icon_path = os.path.join(src_dir, "icon.png")
if os.path.exists(icon_path):
    app.setWindowIcon(QIcon(icon_path))

#load pyqt styling from style.qss
style_path = os.path.join(src_dir, "style.qss")
if os.path.exists(style_path):
    with open(style_path, 'r') as style_file:
        style_content = style_file.read()
        app.setStyleSheet(style_content)

window = QWidget()
window.setObjectName("Window")
window.setWindowTitle("Select a Page")
window.setGeometry(100, 100, 480, 280)



layout = QVBoxLayout()

file_buttons = []

def on_html_file_clicked(filename):
    print(f"Selected file: {filename}")
    full_path = os.path.join(editor_path, filename)
    subprocess.Popen(['python3', os.path.join(src_dir, "editor.py"), full_path])

def refresh_file_buttons():
    # Remove old buttons from layout and memory
    for btn in file_buttons:
        layout.removeWidget(btn)
        btn.setParent(None)
    file_buttons.clear()

    # Get updated list of .html files
    html_files = [f for f in os.listdir(editor_path) if f.endswith('.html')]
    for html_file in html_files:
        button = AnimatedButton(html_file)
        button.clicked.connect(lambda _, f=html_file: on_html_file_clicked(f))
        layout.addWidget(button)
        file_buttons.append(button)

#dropdown for theme selection. populates with folder names in site_resources/themes
theme_section = QVBoxLayout()
layout.addLayout(theme_section)
theme_label = QLabel("Select Theme:")
theme_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
theme_section.addWidget(theme_label, alignment=Qt.AlignmentFlag.AlignHCenter)

theme_dropdown = QComboBox()
theme_dir = os.path.join(src_dir, "themes")

def on_theme_selected(theme_name):
    theme_path = os.path.join(src_dir, "themes", theme_name, "theme.css")
    dest_path = os.path.join(editor_path, "tistatsi", "theme.css")
    if os.path.exists(theme_path):
        with open(theme_path, 'r') as src_file:
            theme_content = src_file.read()
        with open(dest_path, 'w') as dest_file:
            dest_file.write(theme_content)
        print(f"Theme {theme_name} applied. Copied to {dest_path}")
    else:
        print(f"Theme {theme_name} not found.")
    
print(theme_dir)
if os.path.exists(theme_dir):
    themes = [d for d in os.listdir(theme_dir) if os.path.isdir(os.path.join(theme_dir, d))]
    theme_dropdown.addItems(themes)
    print(f"Available themes: {themes}")
theme_dropdown.currentTextChanged.connect(on_theme_selected)
theme_section.addWidget(theme_dropdown, alignment=Qt.AlignmentFlag.AlignHCenter)
on_theme_selected(theme_dropdown.currentText())  # Apply the initial theme
#when a theme is selected, the theme.css file in the selected folder is copied to editor_path/tistatsi/theme.css

helloMsg = QLabel("<h3>Select a page, or create a new one.</h3>")
helloMsg.setAlignment(Qt.AlignmentFlag.AlignHCenter)
layout.addWidget(helloMsg)
    

def create_new():
    print("Creating a new page...")
    namedialog = QWidget()
    namedialog.setWindowTitle("New Page")
    namedialog.setGeometry(150, 150, 300, 100)
    vlayout = QVBoxLayout()
    label = QLabel("Enter the name for the new page (without .html):")
    vlayout.addWidget(label)
    name_input = QLineEdit()
    vlayout.addWidget(name_input)
    create_button = AnimatedButton("Create")

    def on_create():
        template_content = ""
        with open("site_resources/template.html", 'r') as template_file:
            template_content = template_file.read()

        new_name = name_input.text().strip()
        if new_name:
            updated_template = template_content.replace('<!--TITLE-->', new_name)
            new_file_path = os.path.join(editor_path, f"{new_name}.html")
            with open(new_file_path, 'w') as new_file:
                new_file.write(updated_template)
            print(f"New page created: {new_file_path}")

            subprocess.Popen(['python3', os.path.join(src_dir, "editor.py"), new_file_path])
            refresh_file_buttons()
            namedialog.close()
        else:
            print("Page name cannot be empty.")

    create_button.clicked.connect(on_create)
    vlayout.addWidget(create_button)
    namedialog.setLayout(vlayout)
    namedialog.show()

# Create New Page button
create_new_button = AnimatedButton("Create New Page")
create_new_button.clicked.connect(create_new)
layout.addWidget(create_new_button, alignment=Qt.AlignmentFlag.AlignHCenter)

# Divider line
line = QFrame()
line.setFrameShape(QFrame.Shape.HLine)
line.setFrameShadow(QFrame.Shadow.Sunken)
layout.addWidget(line)

# Populate the initial file list
refresh_file_buttons()

window.setLayout(layout)
window.show()
sys.exit(app.exec())
