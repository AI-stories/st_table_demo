import logging
import time
from pathlib import Path

from docling_core.types.doc import ImageRefMode

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.utils.export import generate_multimodal_pages

IMAGE_RESOLUTION_SCALE = 2.0

logging.basicConfig(level=logging.INFO)


def extract_text_from_file_docling(input_doc_path, output_dir, force_extract=False):
    input_doc_path = Path(input_doc_path)
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    if not force_extract and any(output_dir.glob("*.md")):
        logging.info(f"Skipping {input_doc_path} because it already exists")
        return

    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting PdfPipelineOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    # The PdfPipelineOptions.generate_* are the selectors for the document elements which will be enriched
    # with the image field
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem

    # Save markdown with externally referenced pictures
    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    # save full page image if not present in markdown
    with open(md_filename, "a") as f:
        md_content = "\n"
        for (
            content_text,
            _,
            _,
            _,
            _,
            page,
        ) in generate_multimodal_pages(conv_res):
            if content_text == "":
                page_image_filename = (
                    output_dir
                    / (input_doc_path.stem + "-with-image-refs_artifacts")
                    / f"{doc_filename}-page-{page.page_no}.png"
                )
                with page_image_filename.open("wb") as fp:
                    page.image.save(fp, format="PNG")
                relative_path = (
                    Path((input_doc_path.stem + "-with-image-refs_artifacts"))
                    / f"{doc_filename}-page-{page.page_no}.png"
                )
                md_content += f"\n![Image]({relative_path})\n"
        f.write(md_content)

    end_time = time.time() - start_time

    logging.info(f"Document converted and figures exported in {end_time:.2f} seconds.")
    return conv_res
