import pandas as pd
import base64
from PIL import Image
from io import BytesIO

def save_image_from_base64(base64_string, filename):
    # Add padding to the base64 string if needed
    padding_needed = 4 - len(base64_string) % 4
    base64_string += '=' * padding_needed
    
    image_data = base64.b64decode(base64_string)
    with open(filename, 'wb') as f:
        f.write(image_data)

def parse_excel_and_save_images(excel_file):
    df = pd.read_excel(excel_file)
    for index, row in df.iterrows():
        image_base64 = row['Image']
        filename = f"image_{index}.jpg"  # Adjust the filename as needed
        save_image_from_base64(image_base64, filename)

# Example usage
excel_file = "11 inch minatour dildo_results.xlsx"  # Provide the path to your Excel file
parse_excel_and_save_images(excel_file)


