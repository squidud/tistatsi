from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QFrame, QLineEdit, QComboBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from animated_button import AnimatedButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QUrl
import sys, os, glob, threading
from PyQt6.QtWebEngineWidgets import QWebEngineView
from livereload import Server

app = QApplication(sys.argv)

editor_path = ""
src_dir = os.path.dirname(os.path.abspath(__file__))

with open("editorpath.txt", 'r') as file:
    editor_path = file.read().strip()
    print(f"Editor path loaded: {editor_path}")

#create web server
port_number = 5500
prev_server = Server()
prev_server.watch(editor_path)

# Start server in background thread so GUI can run
def start_server():
    prev_server.serve(root=editor_path, port=port_number)

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Set application icon
icon_path = os.path.join(src_dir, "icon.png")
if os.path.exists(icon_path):
    app.setWindowIcon(QIcon(icon_path))

window = QWidget()
window.setObjectName("Window")
window.setWindowTitle("Tistatsi - Preview")
window.setGeometry(100, 100, 1280, 720)

layout = QVBoxLayout() #top section being logo/title, buttom being main content (file list and preview)

titlebar = QHBoxLayout()

#load pyqt styling from style.qss
style_path = os.path.join(src_dir, "style.qss")
if os.path.exists(style_path):
    with open(style_path, 'r') as style_file:
        style_content = style_file.read()
        app.setStyleSheet(style_content)



#creates title bar
logo_scale = 0.08
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
    titlebar.addWidget(logo_label)

title = QLabel("<h2>Site Preview</h2>")
titlebar.addWidget(title)

# Add spacer to push logo and title to the left
spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
titlebar.addItem(spacer)

#main content layout
main_content = QHBoxLayout()

#gui stuff...
#html file selector list
file_selector_layout = QVBoxLayout()
file_selector_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

file_selector_label = QLabel("Select a Page to Preview:")
file_selector_layout.addWidget(file_selector_label)

# Create container widget for file selector with styling
file_selector_container = QWidget()
file_selector_container.setLayout(file_selector_layout)
file_selector_container.setStyleSheet("""
    QWidget {
        background-color: #4a4a4a;
        border: 1px inset #3a3a3a;
        border-radius: 4px;
        padding: 10px;
    }
""")

#selectable html file list as buttons
html_files = glob.glob(os.path.join(editor_path, "*.html"))
html_filenames = [os.path.basename(f) for f in html_files]

file_buttons = []
selected_file = None

def on_file_selected(filename):
    global selected_file
    selected_file = filename
    update_preview(filename, preview_browser)
    # Update button styles to show selection
    for btn in file_buttons:
        if btn.text() == filename:
            btn.setStyleSheet("background-color: #0078d4; color: white;")
        else:
            btn.setStyleSheet("")

for filename in html_filenames:
    file_btn = AnimatedButton(filename)
    file_btn.clicked.connect(lambda checked, f=filename: on_file_selected(f))
    file_selector_layout.addWidget(file_btn)
    file_buttons.append(file_btn)


#web preview section
preview_browser = QWebEngineView()
preview_browser.setUrl(QUrl(f"http://localhost:{port_number}/index.html")) #default blank page
preview_browser.setMinimumWidth(300)
preview_browser.setMinimumHeight(300)
main_content.addWidget(file_selector_container, stretch=1)
main_content.addWidget(preview_browser, stretch=4)

#sets url for preview browser
def update_preview(selected_file, browser):
    if selected_file:
        file_url = f"http://localhost:{port_number}/{selected_file}"
        print(f"Loading preview for: {file_url}")
        browser.setUrl(QUrl(file_url))


# File selection is now handled by button clicks

# Add layouts to main layout
layout.addLayout(titlebar, stretch=1)
layout.addLayout(main_content, stretch=10)

# Set layout and show window
window.setLayout(layout)
window.show()
sys.exit(app.exec())
