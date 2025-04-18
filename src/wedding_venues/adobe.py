"""
Copyright 2024 Adobe
All Rights Reserved.

NOTICE: Adobe permits you to use, modify, and distribute this file in
accordance with the terms of the Adobe license agreement accompanying it.
"""

import logging
import os
from datetime import datetime
import dotenv
from adobe.pdfservices.operation.auth.service_principal_credentials import (
    ServicePrincipalCredentials,
)
from adobe.pdfservices.operation.exception.exceptions import (
    SdkException,
    ServiceApiException,
    ServiceUsageException,
)
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import (
    ExtractElementType,
)
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import (
    ExtractPDFParams,
)
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import (
    ExtractRenditionsElementType,
)
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import (
    ExtractPDFResult,
)


dotenv.load_dotenv()


# Initialize the logger
logging.basicConfig(level=logging.INFO)

#
# This sample illustrates how to extract Text, Table Elements Information from PDF along with renditions of Figure,
# Table elements.
#
# Refer to README.md for instructions on how to run the samples & understand output zip file.
#


def create_output_file_path(zip_path: str) -> str:
    if os.path.isfile(zip_path):
        zip_name = os.path.basename(zip_path)
        zip_path = os.path.dirname(zip_path)
    else:
        time_stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        zip_name = f"extract_{time_stamp}.zip"
    os.makedirs(zip_path, exist_ok=True)
    return f"{zip_path}/{zip_name}"


def pdf2zip(pdf_path: str, zip_path: str):
    try:
        file = open(pdf_path, "rb")
        input_stream = file.read()
        file.close()

        # Initial setup, create credentials instance
        credentials = ServicePrincipalCredentials(
            client_id=os.getenv("PDF_SERVICES_CLIENT_ID"),
            client_secret=os.getenv("PDF_SERVICES_CLIENT_SECRET"),
        )

        # Creates a PDF Services instance
        pdf_services = PDFServices(credentials=credentials)

        # Creates an asset(s) from source file(s) and upload
        input_asset = pdf_services.upload(
            input_stream=input_stream, mime_type=PDFServicesMediaType.PDF
        )

        # Create parameters for the job
        extract_pdf_params = ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
            elements_to_extract_renditions=[
                ExtractRenditionsElementType.TABLES,
                ExtractRenditionsElementType.FIGURES,
            ],
        )

        # Creates a new job instance
        extract_pdf_job = ExtractPDFJob(
            input_asset=input_asset, extract_pdf_params=extract_pdf_params
        )

        # Submit the job and gets the job result
        location = pdf_services.submit(extract_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

        # Get content from the resulting asset(s)
        result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
        stream_asset: StreamAsset = pdf_services.get_content(result_asset)

        # Creates an output stream and copy stream asset's content to it
        output_file_path = create_output_file_path(zip_path)
        with open(output_file_path, "wb") as file:
            file.write(stream_asset.get_input_stream())

    except (ServiceApiException, ServiceUsageException, SdkException) as e:
        logging.exception(f"Exception encountered while executing operation: {e}")
