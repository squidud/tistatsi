from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog
)
from animated_button import AnimatedButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
import sys
import os
import subprocess

src_dir = os.path.dirname(os.path.abspath(__file__))

editor_path = ""

def open_folder_dialog():
    global editor_path
    folder_path = QFileDialog.getExistingDirectory(window, 'Select Folder')
    if folder_path:
        selected_folder_label.setText(f'Selected Folder: {folder_path}')
        editor_path = folder_path
        start_button = AnimatedButton("Start Editing")
        start_button.clicked.connect(open_page_selector)  # Placeholder for editor function
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    else:
        selected_folder_label.setText('Folder selection cancelled.')


def open_page_selector():
    #check if tistatsi folder exists within the editor path folder
    global editor_path
    tistatsi_folder = os.path.join(editor_path, "tistatsi")
    images_folder = os.path.join(editor_path, "images")
    if not os.path.exists(tistatsi_folder):
        os.makedirs(tistatsi_folder)
        print(f"Created tistatsi folder at: {tistatsi_folder}")
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"Created images folder at: {images_folder}")
    
    # write the editor path to editorpath.txt
    with open("editorpath.txt", 'w') as file:
        file.write(editor_path)
        print(f"Editor path saved: {editor_path}")

    # copy tistatsi_org.css to the new folder
    css_src = os.path.join(src_dir, "site_resources/tistatsi_org.css")
    css_dest = os.path.join(tistatsi_folder, "tistatsi_org.css")
    if os.path.exists(css_src):
        with open(css_src, 'r') as src_file:
            css_content = src_file.read()
        with open(css_dest, 'w') as dest_file:
            dest_file.write(css_content)
        print(f"Copied tistatsi_org.css to: {css_dest}")

    # if navbar.html doesn't exist in new folder, copy it from site_recources
    navbar_src = os.path.join(src_dir, "site_resources/navbar.html")
    navbar_dest = os.path.join(tistatsi_folder, "navbar.html")
    if not os.path.exists(navbar_dest):
        with open(navbar_src, 'r') as src_file:
            navbar_content = src_file.read()
        with open(navbar_dest, 'w') as dest_file:
            dest_file.write(navbar_content)
        print(f"Copied navbar.html to: {navbar_dest}")
    

    subprocess.Popen(['python3', os.path.join(src_dir, "pageselector.py")])
    window.close()
    app.quit()

app = QApplication([])

# Set application icon
icon_path = os.path.join(src_dir, "icon.png")
if os.path.exists(icon_path):
    app.setWindowIcon(QIcon(icon_path))

window = QWidget()
window.setObjectName("Window")
window.setWindowTitle("Tistatsi")
window.setGeometry(100, 100, 480, 80)

layout = QVBoxLayout()

#load pyqt styling from style.qss
style_path = os.path.join(src_dir, "style.qss")
if os.path.exists(style_path):
    with open(style_path, 'r') as style_file:
        style_content = style_file.read()
        app.setStyleSheet(style_content)


logo_scale = 0.15
logo_path = os.path.join(src_dir, "logo.png")
if os.path.exists(logo_path):
    logo = QPixmap(logo_path)
    logo = logo.scaled(
        round(logo.width() * logo_scale),
        round(logo.height() * logo_scale),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    logo_label = QLabel()
    logo_label.setPixmap(logo)
    logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    layout.addWidget(logo_label)

helloMsg = QLabel("<h3>Welcome to Tistatsi</h3>")
helloMsg.setAlignment(Qt.AlignmentFlag.AlignHCenter)
layout.addWidget(helloMsg)

filebutton = AnimatedButton("Select Edit Folder")
filebutton.clicked.connect(open_folder_dialog)
layout.addWidget(filebutton, alignment=Qt.AlignmentFlag.AlignHCenter)

selected_folder_label = QLabel('No folder selected.')
layout.addWidget(selected_folder_label)

window.setLayout(layout)

window.show()
sys.exit(app.exec())
