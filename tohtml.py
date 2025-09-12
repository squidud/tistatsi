from block_components import Section, Title, Paragraph, Image
import os

src_dir = os.path.dirname(os.path.abspath(__file__))
editor_path = ""

# Read from editorpath to get selected folder
with open("editorpath.txt", 'r') as file:
    editor_path = file.read().strip()
    print(f"Editor path loaded: {editor_path}")

def convert_to_html(sections):
    html_content = ""
    for section in sections:
        section_html = "<section class='tsection'>\n"
        for i in range(len(section.content_objects)):
            content = section.content_objects[i]
            if isinstance(content, Title):
                section_html += ("<div class='column"+str(i+1)+"'><h2 class='ttitle'>"+content.content+"</h2></div>\n")
            elif isinstance(content, Paragraph):
                section_html += ("<div class='column"+str(i+1)+"'><p class='tparagraph'>"+content.content+"</p></div>\n")
            elif isinstance(content, Image):
                section_html += ("<div class='column"+str(i+1)+"'><img class='timage' src='"+content.get_relative_path()+"'></div>\n")
            else: 
                section_html += "<!-- Nothing here! -->\n"
        section_html += "</section>\n"
        html_content += section_html
    return html_content
