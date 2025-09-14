#objects for each section type (1,2,3 columns) and objects for each content type. Each section will have variables which
#reference the child content objects.

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QFileDialog, QFrame, QLineEdit, QScrollArea, QDialog, QComboBox, QTextEdit, QHBoxLayout, QGraphicsPixmapItem,
)
from animated_button import AnimatedButton
import os

from imgcompressor import convert_for_web

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

editor_path = ""
# Read from editorpath to get selected folder
with open("editorpath.txt", 'r') as file:
    editor_path = file.read().strip()
    print(f"Editor path loaded: {editor_path}")

# Global callback for change notifications
_change_callback = None

def set_change_callback(callback):
    """Set the callback function to be called when content changes"""
    global _change_callback
    _change_callback = callback

def notify_change():
    """Notify that content has changed"""
    if _change_callback:
        try:
            _change_callback()
        except Exception as e:
            print(f"Error calling change callback: {e}")

class Section:
    def __init__(self, parent, num_columns):
        self.content_objects = [None] * num_columns
        self.content_widgets = [None] * num_columns  # store current content widgets per slot
        self.parent = parent
        self.section_layout = None
        self.content_layouts = []  # keep layouts to add/remove content widgets

    def add_content(self, content_object, slot):
        # replace content object
        self.content_objects[slot] = content_object

        # only update UI if layouts are initialized (render() was called)
        if self.content_layouts:
            # remove old content widget from UI
            if self.content_widgets[slot]:
                old_widget = self.content_widgets[slot]
                self.content_layouts[slot].removeWidget(old_widget)
                old_widget.setParent(None)
                old_widget.deleteLater()
                self.content_widgets[slot] = None

            # add new rendered widget
            new_widget = content_object.render()
            self.content_layouts[slot].addWidget(new_widget)
            self.content_widgets[slot] = new_widget
        
        print(f"Added content to slot {slot}: {type(content_object).__name__}")

    def render(self):
        self.section_layout = QHBoxLayout()
        self.content_layouts = []

        for i, content in enumerate(self.content_objects):
            content_widget = QWidget()
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(10, 10, 10, 10)

            # Dropdown
            content_dropdown = QComboBox()
            content_dropdown.addItems(["Title", "Paragraph", "Image"])
            idx = self.get_content_index(content)
            content_dropdown.setCurrentIndex(idx if idx >= 0 else 0)
            content_dropdown.currentIndexChanged.connect(
                lambda idx, col=i: self.add_content(self.create_content_object(idx), col)
            )

            content_layout.addWidget(content_dropdown)
            self.content_layouts.append(content_layout)

            # Add existing or default content
            if content is None:
                default_content = self.create_content_object(0)
                self.content_objects[i] = default_content
                rendered_widget = default_content.render()
                self.content_widgets[i] = rendered_widget
                content_layout.addWidget(rendered_widget)
            else:
                rendered_widget = content.render()
                self.content_widgets[i] = rendered_widget
                content_layout.addWidget(rendered_widget)

            content_widget.setLayout(content_layout)
            self.section_layout.addWidget(content_widget)

            # vertical divider except last column
            if i < len(self.content_objects) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.VLine)
                divider.setFrameShadow(QFrame.Shadow.Sunken)
                divider.setLineWidth(1)
                self.section_layout.addWidget(divider)

        section_wrapper = QWidget()
        section_wrapper.setLayout(self.section_layout)
        section_wrapper.setStyleSheet("""
            QWidget {
                border: 1px solid #888;
                border-radius: 4px;
                background-color: #fdfdfd;
                margin: 10px;
            }
        """)

        outer_layout = QHBoxLayout()
        outer_layout.addWidget(section_wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.parent.addLayout(outer_layout)


    def create_content_object(self, idx):
        if idx == 0:
            return Title("")
        elif idx == 1:
            return Paragraph("")
        elif idx == 2:
            return Image()
        else:
            return None

    def get_content_index(self, content):
        if isinstance(content, Title):
            return 0
        elif isinstance(content, Paragraph):
            return 1
        elif isinstance(content, Image):
            return 2
        else:
            return -1




class ContentObject:
    def __init__(self, content):
        self.content = content

class Title(ContentObject):
    def render(self):
        input_field = QLineEdit(self.content)
        input_field.setPlaceholderText("Enter title text")
        
        def update_title():
            self.content = input_field.text()
            print(f"Title updated to: {self.content}")
            notify_change()
        
        input_field.textChanged.connect(update_title)
        
        return input_field
    
class Paragraph(ContentObject):
    def render(self):
        input_field = QTextEdit(self.content)
        input_field.setPlaceholderText("Enter paragraph text")
        
        def update_paragraph():
            self.content = input_field.toPlainText()
            print(f"Paragraph updated to: {self.content}")
            notify_change()
        
        input_field.textChanged.connect(update_paragraph)
        
        return input_field
    
class Image(ContentObject):
    def __init__(self, img_src=None):
        super().__init__(img_src)  # start with provided image path or None
        self.image_label = QLabel()
        if img_src:
            self.load_image(img_src)
        else:
            self.image_label.setText("No Image Selected")

    def load_image(self, img_src):
        # Build full path if it's a relative path
        if not os.path.isabs(img_src):
            img_path = os.path.join(editor_path, img_src)
        else:
            img_path = img_src
        
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
            self.image_label.setText("")  # clear text
            self.content = img_src  # store the original path

    def render(self):
        container = QVBoxLayout()
        file_select_button = AnimatedButton("Select Image")
        file_select_button.clicked.connect(self.select_image)

        container.addWidget(file_select_button)
        container.addWidget(self.image_label)

        wrapper = QWidget()
        wrapper.setLayout(container)
        return wrapper

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            images_folder = os.path.join(editor_path, "images")
            self.content = convert_for_web(file_path, images_folder)  # <-- store path here
            pixmap = QPixmap(self.content)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                self.image_label.setText("")  # clear text
                print(f"Image path set to: {self.content}")
                notify_change()

    def get_relative_path(self):
        if not self.content:
            return ""
        return os.path.relpath(self.content, editor_path).replace("\\", "/")
