from PIL import Image
import os

def convert_for_web(input_path, output_folder):
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_folder, f"{filename}.webp")

    img = Image.open(input_path).convert("RGB")
    img.save(output_path, "WEBP", quality=80, method=6)

    return output_path
