from __future__ import annotations

import base64
import functools
import math
import os
import pickle
import re
import tempfile
from mimetypes import guess_type
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np
import pandas as pd
import pytesseract
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = current_dir / Path("model.bin")
client = OpenAI()


@functools.lru_cache
def load_is_photo_classifier() -> RandomForestClassifier:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model


def image_properties(image_path) -> dict:
    with Image.open(image_path) as pil_image:
        width, height = pil_image.size
        total_image_area = width * height

        ocr_data = pytesseract.image_to_data(
            pil_image, output_type=pytesseract.Output.DATAFRAME
        )

    total_text_area = 0
    extracted_text = ""
    try:
        if not ocr_data.empty:
            valid_boxes = ocr_data[
                ocr_data["text"].notna() & (ocr_data["text"].str.strip() != "")
            ]
            total_text_area = sum(
                row["width"] * row["height"] for _, row in valid_boxes.iterrows()
            )
            extracted_text = " ".join(valid_boxes["text"].tolist())
    except Exception:
        pass

    text_density = total_text_area / total_image_area if total_image_area > 0 else 0

    cv_image = cv2.imread(str(image_path))
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    total_pixels = height * width

    edges = cv2.Canny(gray, 100, 200)
    edge_pixels = np.count_nonzero(edges)
    edge_density = edge_pixels / total_pixels

    color_std = np.std(cv_image, axis=(0, 1)).mean()

    properties = {
        "width": width,
        "height": height,
        "total_pixels": total_pixels,
        "text_density": text_density,
        "color_std": color_std,
        "edge_density": edge_density,
    }
    is_photo_ = predict_image_quality(load_is_photo_classifier(), properties)
    properties.update(
        {
            "is_photo": is_photo_,
            "has_text": len(extracted_text) > 5,
            "extracted_text": extracted_text,
        }
    )
    return properties


def predict_image_quality(model, properties: dict) -> bool:
    X = pd.DataFrame(
        {
            "width": properties["width"],
            "height": properties["height"],
            "total_pixels": properties["total_pixels"],
            "text_density": properties["text_density"],
            "color_std": properties["color_std"],
            "edge_density": properties["edge_density"],
        },
        index=[0],
    )
    return bool(model.predict(X)[0])


def resize_image(image_path, max_size=512):
    """
    Resize an image if either width or height exceeds max_size while maintaining aspect ratio.
    Saves the result to a temporary file only if resizing is needed.

    Args:
        image_path (str): Path to input image
        max_size (int): Maximum allowed dimension (width or height). Defaults to 500.

    Returns:
        str: Either the original path if no resize needed, or path to temp file if resized
    """
    with Image.open(image_path) as img:
        width, height = img.size

        if width <= max_size and height <= max_size:
            return image_path

        scale = min(max_size / width, max_size / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        file_ext = os.path.splitext(image_path)[1]
        if not file_ext:
            file_ext = ".png"

        temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
        temp_path = temp_file.name

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_img.save(temp_path)

        return temp_path


def local_image_to_data_url(image_path: str) -> str:
    """
    Convert a local image file to a data URL.
    """
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{base64_encoded_data}"


# def generate_image_descriptions(
#     base_dir: str,
#     venue: str,
#     model: str = "gpt-4o",
# ) -> list[dict[str, str]]:
#     """
#     Generate descriptions for images in a directory using OpenAI's API.
#     """
#     print("Generating image descriptions...")
#     client = OpenAI(api_key=secrets.OPENAI_API_KEY.get_secret_value())
#     image_description = []

#     if not os.path.isdir(base_dir):
#         print(f"Directory not found: {base_dir}")
#         return []

#     photo_classifier = load_is_photo_classifier()
#     for i, image_file in enumerate(os.listdir(base_dir)):
#         image_path = os.path.join(base_dir, image_file)
#         print(f"   ({i + 1}/{len(os.listdir(base_dir))}) {image_path}")
#         if not is_photo(photo_classifier, image_path):
#             print(f"skipping {image_path}")
#             continue
#         temp_image_path = resize_image(image_path)
#         try:
#             data_url = local_image_to_data_url(temp_image_path)

#             response = client.chat.completions.create(
#                 model=model,
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": """
#                                         You are tasked with summarizing the description of the images about wedding venues.
#                                         Give a concise summary of the images provided to you. Focus on the
#                                         style and wedding theme. If decorative elements (e.g., illustrations such as leaves and flowers, templates) are present, do not confuse them with real settings.The output should not be more than 30 words. """,
#                             },
#                             {"type": "image_url", "image_url": {"url": data_url}},
#                         ],
#                     }
#                 ],
#                 max_tokens=30,
#             )

#             content = response.choices[0].message.content
#         except Exception as e:
#             print(f"Error processing image {image_path}: {e}")
#             continue

#         output_image_dir = Path(".") / venue
#         output_image_path = output_image_dir / image_file
#         image_description.append(
#             {"image_path": str(output_image_path), "description": content}
#         )

#     return image_description


class WeddingText(BaseModel):
    text: str | None = Field(
        description="""
        Extracted text from the image in markdown format. Returns None if text
        is unreadable or gibberish
        """
    )
    is_photo: bool = Field(
        description="""Indicates if the image is a meaningful photograph (food,
                    decor, venue, or wedding related) rather than a logo,
                    background, or decorative element"""
    )
    description: str = Field(
        description="""Brief description of the image content, particularly
                    useful for categorizing photos of food, decor, or
                    wedding-related scenes"""
    )

    @classmethod
    def from_image(cls, image_path: str) -> "WeddingText":
        return image_to_wedding_text(image_path)

    def to_markdown(self, output_path: str | Path) -> None:
        text = ""
        if self.is_photo:
            text += f"""
                ==== image description ====
                {self.description}
                ==== end of image description ====
                """
        if self.text is not None:
            text += self.text
        with open(output_path, "w") as f:
            f.write(text)


def image_to_wedding_text(image_path: str) -> WeddingText:
    client = OpenAI()

    prompt = """
        You are tasked with summarizing the description of the images about
        wedding venues. Give a concise summary of the images provided to you.
        Focus on the style and wedding theme. If decorative elements (e.g.,
        illustrations such as leaves and flowers, templates) are present, do not
        confuse them with real settings.The output should not be more than 30
        words. If there is text present, please transcribe. If the image is not
        related to a wedding venue, please ignore."""

    data_url = local_image_to_data_url(image_path)

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        response_format=WeddingText,
    )
    return response.choices[0].message.parsed


def downsize_image(image_path, max_size=1024):
    resized_path = resize_image(image_path, max_size)
    return local_image_to_data_url(resized_path)


def get_cost(properties):
    width, height = properties["width"], properties["height"]
    tokens = 85 + math.ceil(width / 512) * math.ceil(height / 512) * 170
    return tokens * 2.5 / 1_000_000


def figure_to_md(figure, force_extract=False, delete_if_false_image=True) -> None:
    markdown_path = Path(figure).with_suffix(".md")
    if markdown_path.exists() and not force_extract:
        return

    figure_resized = resize_image(figure, 1024)
    properties = image_properties(figure_resized)
    is_photo = properties["is_photo"]
    has_text = properties["has_text"]

    if not has_text and not is_photo:
        if delete_if_false_image:
            figure.unlink()
        return

    try:
        wedding_text = WeddingText.from_image(figure)
    except Exception as e:
        print(f"Error processing image {figure}: {e}")
        return
    if not wedding_text.is_photo and not wedding_text.text:
        if delete_if_false_image:
            figure.unlink()
        return
    wedding_text.to_markdown(markdown_path)


def replace_images_with_markdown(file_path: str | Path, inplace=False) -> str:
    """
    Replace image references in a markdown file with their corresponding markdown content.

    Parameters
    ----------
    file_path : str | Path
        Path to the markdown file to process
    inplace : bool, optional
        If True, write the processed markdown back to the file.
        If False, return the processed markdown content.

    Returns
    -------
    str
        Processed markdown content with image references replaced where possible

    Notes
    -----
    For each image reference of format ![Image](path/to/image.png), checks if a
    corresponding .md file exists at path/to/image.md. If it exists, replaces the
    image reference with the markdown content. If not, keeps the original reference.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file {file_path} not found")

    # Read input markdown
    content = file_path.read_text()

    # Find all image references
    img_pattern = r"!\[Image\]\((.*?)\)"

    def replace_match(match: re.Match) -> str:
        img_path = match.group(1)
        md_path = Path(file_path.parent / Path(img_path).with_suffix(".md"))

        if md_path.exists():
            # print(f"replace {img_path} with {md_path}")
            return md_path.read_text().strip()
        # print(f"no {md_path}")
        return match.group(0)

    # Replace all matches
    processed_content = re.sub(img_pattern, replace_match, content)

    if inplace:
        file_path.write_text(processed_content)
    return processed_content
