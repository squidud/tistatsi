from block_components import Section, Title, Paragraph, Image
import os
import re

def convert_to_python(html_content, parent):
    sections = []
    section_pattern = re.compile(r'<section class=[\'"]tsection[\'"]>(.*?)</section>', re.DOTALL)
    title_pattern = re.compile(r'<h2 class=[\'"]ttitle[\'"]>(.*?)</h2>', re.DOTALL)
    paragraph_pattern = re.compile(r'<p class=[\'"]tparagraph[\'"]>(.*?)</p>', re.DOTALL)
    image_pattern = re.compile(r'<img class=[\'"]timage[\'"] src=[\'"](.*?)[\'"]>', re.DOTALL)

    section_matches = section_pattern.findall(html_content)
    for sec in section_matches:
        widgets = []
        title_matches = title_pattern.findall(sec)
        paragraph_matches = paragraph_pattern.findall(sec)
        image_matches = image_pattern.findall(sec)
        columns = 0

        max_len = max(len(title_matches), len(paragraph_matches), len(image_matches))
        for i in range(max_len):
            if i < len(title_matches):
                title_text = title_matches[i].strip()
                if title_text:
                    widgets.append(Title(title_text))
                    columns += 1
            if i < len(paragraph_matches):
                para_text = paragraph_matches[i].strip()
                if para_text:
                    widgets.append(Paragraph(para_text))
                    columns += 1
            if i < len(image_matches):
                img_src = image_matches[i].strip()
                if img_src:
                    widgets.append(Image(img_src))
                    columns += 1
        section = Section(parent, columns)
        slotcounter = 0
        for item in widgets:
            section.add_content(item, slotcounter)
            slotcounter += 1
        sections.append(section)
    return sections