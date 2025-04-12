import json
import os
import os.path
import re
import tempfile
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Union

import pandas as pd


def get_dict_xlsx(
    extracted_folder_path: str, excel_filename: str
) -> List[Dict[str, Any]]:
    """Read excel output from adobe API and convert to dictionary format.

    Parameters
    ----------
    extracted_folder_path : str
        Path to the directory containing the excel file
    excel_filename : str
        Name of the excel file to read

    Returns
    -------
    List[Dict[str, Any]]
        List of dictionaries containing the excel data
    """
    df = pd.read_excel(
        os.path.join(extracted_folder_path, excel_filename),
        sheet_name="Sheet1",
        engine="openpyxl",
    )

    df.columns = [re.sub(r"_x([0-9a-fA-F]{4})_", "", col) for col in df.columns]
    df = df.replace({r"_x([0-9a-fA-F]{4})_": ""}, regex=True)

    data_dict = df.to_dict(orient="records")

    return data_dict


def zip2md(zip_path: str, md_path: str) -> str:
    """Convert a PDF zip file to markdown format.

    This function extracts content from a PDF that has been processed by Adobe's PDF Services API.
    It converts the extracted content into markdown format, preserving:
    - Text content with proper heading levels (H1-H6)
    - Tables (as JSON)
    - Images (as HTML img tags with dimensions)

    Parameters
    ----------
    zip_path : str
        Path to the zip file containing the Adobe PDF Services output
    md_path : str
        Path to the markdown file to save the output

    Returns
    -------
    str
        Markdown formatted text containing all extracted content
    """
    if not zip_path.endswith(".zip"):
        output_zip_path = f"adobe_result/{zip_path}/sdk.zip"
    else:
        output_zip_path = zip_path
    print(f"output zip path: {output_zip_path}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        json_file_path = os.path.join(tmp_dir, "structuredData.json")

        try:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} unzip file")
            with zipfile.ZipFile(output_zip_path, "r") as zip_ref:
                zip_ref.extractall(path=tmp_dir)
        except Exception as e:
            print("----Error: cannot unzip file")
            print(e)
            return ""

        try:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} open json file")
            with open(json_file_path) as json_file:
                data = json.load(json_file)
        except Exception as e:
            print("----Error: cannot open json file")
            print(e)
            return ""

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} extract content")
        dfs = pd.DataFrame()
        page = ""
        try:
            for ele in data["elements"]:
                df = pd.DataFrame()

                if "Page" in ele:
                    page = ele["Page"]

                if any(x in ele["Path"] for x in ["Table"]):
                    if "filePaths" in ele:
                        if [s for s in ele["filePaths"] if "xlsx" in s]:
                            data_dict = get_dict_xlsx(tmp_dir, ele["filePaths"][0])
                            json_string = json.dumps(data_dict)
                            df = pd.DataFrame({"text": json_string}, index=[0])

                elif "Text" in ele:
                    path = ele["Path"]
                    if "H1" in path:
                        df = pd.DataFrame({"text": f"# {ele['Text']}"}, index=[0])
                    elif "H2" in path:
                        df = pd.DataFrame({"text": f"## {ele['Text']}"}, index=[0])
                    elif "H3" in path:
                        df = pd.DataFrame({"text": f"### {ele['Text']}"}, index=[0])
                    elif "H4" in path:
                        df = pd.DataFrame({"text": f"#### {ele['Text']}"}, index=[0])
                    elif "H5" in path:
                        df = pd.DataFrame({"text": f"##### {ele['Text']}"}, index=[0])
                    elif "H6" in path:
                        df = pd.DataFrame({"text": f"###### {ele['Text']}"}, index=[0])
                    elif "Figure" not in path:
                        df = pd.DataFrame({"text": ele["Text"]}, index=[0])

                elif "Figure" in ele["Path"] and "filePaths" in ele:
                    for img_path in ele["filePaths"]:
                        if any(
                            ext in img_path.lower()
                            for ext in [".jpg", ".jpeg", ".png", ".gif"]
                        ):
                            full_img_path = os.path.join(tmp_dir, img_path)
                            bounds = ele.get("Bounds", [])
                            if len(bounds) == 4:
                                width = bounds[2] - bounds[0]
                                height = bounds[3] - bounds[1]
                                markdown_img = f'<img src="{full_img_path}" width="{width:.0f}" height="{height:.0f}" alt="Figure from page {page}"/>'
                            else:
                                markdown_img = f'<img src="{full_img_path}" alt="Figure from page {page}"/>'
                            df = pd.DataFrame({"text": markdown_img}, index=[0])

                df["page_number"] = page
                dfs = pd.concat([dfs, df], axis=0)

        except Exception as e:
            print("----Error: processing elements in JSON")
            print(e)
            return ""

        dfs = dfs.reset_index(drop=True)
        dfs = dfs.dropna()
        if "text" not in dfs.columns:
            print(f"no content found in document {zip_path}.pdf")
            return ""

        dfs = (
            dfs.groupby("page_number")["text"]
            .apply(lambda x: "\n".join(x))
            .reset_index()
        )
        text_content = "\n".join(dfs["text"].values)
        with open(md_path, "w") as f:
            f.write(text_content)
        return text_content
