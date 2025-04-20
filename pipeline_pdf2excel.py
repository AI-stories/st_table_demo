import logging
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from wedding_venues import (
    extract_text_from_file_docling,
    figure_to_md,
    markdown_to_structured_output,
    replace_images_with_markdown,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

OUTPUT_DIR = Path("test_output2")
EXCEL_FILE = Path("wedding_venues_database.xlsx")
PDF_DIR = Path("test_pdf")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

###############################################################################
#
# STAGE 1: Load existing database
#
###############################################################################

existing_venues = set()
if EXCEL_FILE.exists():
    try:
        df = pd.read_excel(EXCEL_FILE, index_col="wedding venue")
        existing_venues = set(df.index.tolist())
        logger.info(f"Found {len(existing_venues)} existing venues in database")
    except Exception as e:
        logger.error(f"Error reading existing Excel file: {e}")
        logger.info("Will create a new database file")

###############################################################################
#
# STAGE 2: Identify new venues to process
#
###############################################################################

pdf_files = list(PDF_DIR.glob("*.pdf"))
pdf_venues = {pdf.stem for pdf in pdf_files}

new_venues = pdf_venues - existing_venues
logger.info(f"Found {len(new_venues)} new venues to process")

if not new_venues:
    logger.info("No new venues to process. Exiting.")
    exit(0)

###############################################################################
#
# STAGE 3: Process new PDFs to markdown
#
###############################################################################

progress_bar = tqdm(new_venues, desc="Processing venues", unit="venue")
for venue_name in progress_bar:
    pdf_file_path = PDF_DIR / f"{venue_name}.pdf"
    progress_bar.set_postfix(file=str(pdf_file_path))
    output_dir_venue = OUTPUT_DIR / venue_name

    extract_text_from_file_docling(pdf_file_path, output_dir_venue, force_extract=False)
    figures = filter(
        lambda fig: fig.suffix in [".png", ".jpg", ".jpeg"],
        output_dir_venue.glob("**/*"),
    )
    for figure in tqdm(sorted(figures)):
        figure_to_md(figure, force_extract=False, delete_if_false_image=True)

    try:
        markdown_path = next(output_dir_venue.glob("*.md"))
    except StopIteration:
        logger.warning(f"No markdown file found for {venue_name}")
        continue
    new_md = replace_images_with_markdown(
        markdown_path,
        inplace=True,
    )

###############################################################################
#
# STAGE 4: Convert markdown to structured data
#
###############################################################################

venue_data = None
try:
    for venue_dir in OUTPUT_DIR.iterdir():
        if not venue_dir.is_dir():
            continue

        markdown_files = list(venue_dir.glob("*.md"))
        venue_name = venue_dir.name

        if not markdown_files:
            continue

        markdown_path = markdown_files[0]
        row = markdown_to_structured_output(markdown_path)
        if venue_data is None:
            venue_data = row
        else:
            venue_data += row
finally:
    ###########################################################################
    #
    # STAGE 5: Update database
    #
    ###########################################################################

    if EXCEL_FILE.exists():
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a") as writer:
            venue_data.df.to_excel(writer, sheet_name="Venue Options")
            logger.info(f"Appended {len(venue_data.df)} venues to {EXCEL_FILE}")
    else:
        venue_data.to_excel(EXCEL_FILE)
        logger.info(
            f"Created new database file {EXCEL_FILE} with {len(venue_data.df)} venues"
        )
