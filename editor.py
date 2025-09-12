from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QFileDialog, QFrame, QLineEdit, QScrollArea, QDialog, QComboBox, QCheckBox
)
from animated_button import AnimatedButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from bs4 import BeautifulSoup
from block_components import Section, Title, Paragraph, Image
import sys
import re
import os
from tohtml import convert_to_html
from topython import convert_to_python

app = QApplication([])

#sections list
sections = []

src_dir = os.path.dirname(os.path.abspath(__file__))
editor_path = ""

with open("editorpath.txt", 'r') as file:
    editor_path = file.read().strip()
    print(f"Editor path loaded: {editor_path}")

#load pyqt styling from style.qss
style_path = os.path.join(src_dir, "style.qss")
if os.path.exists(style_path):
    with open(style_path, 'r') as style_file:
        style_content = style_file.read()
        app.setStyleSheet(style_content)

if len(sys.argv) < 2:
    print("No file path provided.")
    sys.exit(1)

html_path = sys.argv[1]
html_content = ""
print(f"Opening editor for: {html_path}")

with open(html_path, 'r') as file:
    s = file.read()

if "<!--START-->" in s and "<!--END-->" in s:
    result = re.search(r'<!--START-->(.*?)<!--END-->', s, re.DOTALL)
    html_content = result.group(1) if result else ""
else:
    # create error message
    window = QDialog()
    window.setWindowTitle("File Error")
    window.setGeometry(150, 150, 300, 100)
    layout = QVBoxLayout()
    title_label = QLabel("<h3>Error: Invalid HTML File</h3>")
    title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    layout.addWidget(title_label)
    error_label = QLabel("This HTML file does not appear to be formatted to work in Tistatsi.")
    layout.addWidget(error_label)
    okay_button = AnimatedButton("OK")
    okay_button.clicked.connect(window.close)
    layout.addWidget(okay_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    window.setLayout(layout)
    window.exec()
    sys.exit(1)


# Optional: verify path exists
if not os.path.exists(html_path):
    print("File does not exist.")
    sys.exit(1)

# UI setup

# Set application icon
icon_path = os.path.join(src_dir, "icon.png")
if os.path.exists(icon_path):
    app.setWindowIcon(QIcon(icon_path))

window = QWidget()
window.setObjectName("Window")
window.setWindowTitle("HTML Editor")
window.setGeometry(580, 100, 900, 580)
layout = QVBoxLayout()

helloMsg = QLabel(f"<h3>Editing: {os.path.basename(html_path)}</h3>")
helloMsg.setAlignment(Qt.AlignmentFlag.AlignHCenter)
layout.addWidget(helloMsg)

def set_navbar_status(in_navbar):
    # if in_navbar is true and the page is not currently in the navbar, add a link to this html file in the navbar present in editor_path/tistatsi/navbar.html between <!--START--> and <!--END-->
    navbar_path = os.path.join(editor_path, "tistatsi", "navbar.html")
    print(f"Navbar path: {navbar_path}")
    
    with open(navbar_path, 'r') as file:
        navbar_content = file.read()
    
    # Extract current content between START and END markers
    start_marker = "<!--START-->"
    end_marker = "<!--END-->"
    
    start_index = navbar_content.find(start_marker)
    end_index = navbar_content.find(end_marker)
    
    if start_index == -1 or end_index == -1:
        print("Error: Could not find START/END markers in navbar.html")
        return
    
    # Get the content between markers
    current_content = navbar_content[start_index + len(start_marker):end_index].strip()
    
    # Create the link for this page
    page_link = f'<a href="/{os.path.basename(html_path)}" class="navlink">{os.path.basename(html_path)}</a>'
    
    if in_navbar:
        # Check if the link already exists
        if page_link not in current_content:
            # Add the new link to existing content
            if current_content:
                updated_content = current_content + '\n' + page_link
            else:
                updated_content = page_link
            
            # Replace the content between markers
            new_navbar_content = (
                navbar_content[:start_index + len(start_marker)] + 
                '\n' + updated_content + '\n' +
                navbar_content[end_index:]
            )
            
            with open(navbar_path, 'w') as file:
                file.write(new_navbar_content)
            print(f"Added {os.path.basename(html_path)} to navbar.")
        else:
            print(f"{os.path.basename(html_path)} already in navbar.")
    
    else:
        # Remove the link from navbar
        if page_link in current_content:
            # Remove the specific link
            updated_content = current_content.replace(page_link, '')
            # Clean up any double newlines
            updated_content = re.sub(r'\n\s*\n', '\n', updated_content).strip()
            
            # Replace the content between markers
            if updated_content:
                new_navbar_content = (
                    navbar_content[:start_index + len(start_marker)] + 
                    '\n' + updated_content + '\n' +
                    navbar_content[end_index:]
                )
            else:
                # If no content left, just put the markers together
                new_navbar_content = (
                    navbar_content[:start_index + len(start_marker)] + 
                    navbar_content[end_index:]
                )
            
            with open(navbar_path, 'w') as file:
                file.write(new_navbar_content)
            print(f"Removed {os.path.basename(html_path)} from navbar.")
        else:
            print(f"{os.path.basename(html_path)} not found in navbar.")
# checks if current html file is not index.html
if os.path.basename(html_path) != "index.html":
    # include in navbar checkbox
    navbar_checkbox = QCheckBox("Include in Navbar")
    navbar_checkbox.setChecked(True)  # Default to checked
    navbar_checkbox.stateChanged.connect(lambda state: set_navbar_status(state == Qt.CheckState.Checked.value))


    layout.addWidget(navbar_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter)
    set_navbar_status(navbar_checkbox.isChecked())

# Scroll area setup
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
layout.addWidget(scroll_area)

# Main content layout inside scroll area
main_content = QVBoxLayout()
main_content.setAlignment(Qt.AlignmentFlag.AlignHCenter)
main_content.setContentsMargins(10, 10, 10, 10)

# Wrap layout in a QWidget
content_widget = QWidget()
content_widget.setLayout(main_content)
scroll_area.setWidget(content_widget)




def add_section_dialog():
    dialog = QDialog()
    dialog.setWindowTitle("Add Section")
    dialog.setGeometry(150, 150, 300, 100)
    vlayout = QVBoxLayout()
    
    label = QLabel("Select section type to add:")
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    vlayout.addWidget(label)
    
    dropdown = QComboBox()
    dropdown.addItems(["1 column", "2 column", "3 column"])
    vlayout.addWidget(dropdown)
    
    def sec_but_create():
        section_type = dropdown.currentText()
        if section_type == "1 column":
            sections.append(Section(main_content, 1))
        elif section_type == "2 column":
            sections.append(Section(main_content, 2))
        elif section_type == "3 column":
            sections.append(Section(main_content, 3))
        sections[-1].render()
        dialog.accept()
    
    create_button = AnimatedButton("Add Section")  
    create_button.clicked.connect(sec_but_create)
    vlayout.addWidget(create_button, alignment=Qt.AlignmentFlag.AlignHCenter)

    dialog.setLayout(vlayout)
    dialog.exec()

# add section button
add_section_button = AnimatedButton("Add Section")
add_section_button.clicked.connect(add_section_dialog)  # Placeholder for add section logic
layout.addWidget(add_section_button, alignment=Qt.AlignmentFlag.AlignHCenter)

#import sections from html_content
if "<!--START-->" in s and "<!--END-->" in s:
    result = re.search(r'<!--START-->(.*?)<!--END-->', s, re.DOTALL)
    html_content = result.group(1) if result else ""
    if html_content.strip():
        import_sections = convert_to_python(html_content, main_content)
        for section in import_sections:
            sections.append(section)
            section_widget = section.render()
            layout.addWidget(section_widget)


def saved_dialog():
    dialog = QDialog()
    dialog.setWindowTitle("Save Confirmation")
    dialog.setGeometry(150, 150, 300, 100)
    vlayout = QVBoxLayout()
    label = QLabel("<h3>Changes saved successfully!</h3>")
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    vlayout.addWidget(label)
    okay_button = AnimatedButton("OK")
    okay_button.clicked.connect(dialog.close)
    vlayout.addWidget(okay_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    dialog.setLayout(vlayout)
    dialog.exec()

def save_html():
    new_inner_html = convert_to_html(sections)

    # Use regex to replace the content between the markers
    updated_html = re.sub(
        r'<!--START-->(.*?)<!--END-->',
        f'<!--START-->{new_inner_html}<!--END-->',
        s,
        flags=re.DOTALL
    )

    # Write the updated HTML back to the file
    with open(html_path, 'w') as file:
        file.write(updated_html)
    print(f"Changes saved to {html_path}")
    saved_dialog()

save_button = AnimatedButton("Save Changes to HTML")
save_button.clicked.connect(save_html) # Placeholder for save logic
layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignHCenter)

# Set layout and show window
window.setLayout(layout)
window.show()
sys.exit(app.exec())
