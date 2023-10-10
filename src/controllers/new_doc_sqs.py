import json
import os
from src.utils.web_scrape import WebScraper
from src.dependencies.openapi import DataExtractor
from src.utils import csv_generation
from src.dependencies.users_api import UserApi
from src.utils.aws_s3 import AWSService
from src.utils.pdf_reader import PDFReader
from src import config


class NewDocSqs(object):
    def __init__(self, body):
        if body['type'] == 'urls':
            scraped_websites = WebScraper().site_scrape(body['url_list'])
            new_dict = {
                "scraped_websites": scraped_websites,
                "phrases_list": body.get('phrases_list')
            }
            extracted_data = DataExtractor().extract_data_from_webscraped_urls(new_dict)
            if body.get('output_typeurl'):
                if body['output_typeurl'] == 'CSV':
                    file_path = csv_generation.create_csv(extracted_data, 'urls')
                    UserApi(body).post_document(file_path, body['id'])

                    data = {
                        'extracted_data': extracted_data,
                        'output_document_name': os.path.basename(file_path)
                    }

                    UserApi(body).update_extraction(body['id'], data)

                    os.remove(file_path)
                    
        elif body['type'] == 'file':
            
            AWSService().download_file(body['id'], body['filename'])
            _, file_extension = os.path.splitext(body['filename'])

            if file_extension.lower() == '.pdf':
                pdf_read = PDFReader().read_pdf(body['filename'])

                new_data = {
                    "phrases_list": body.get('phrases_list'),
                    "pdf_data": {body['filename']: pdf_read}
                }
                extracted_data = DataExtractor().extract_data_from_pdf(new_data)

            if body.get('output_typeurl'):
                if body['output_typeurl'] == 'CSV':
                    file_path = csv_generation.create_csv(extracted_data, 'urls')
                    UserApi(body).post_document(file_path, body['id'])

                    data = {
                        'extracted_data': extracted_data,
                        'output_document_name': os.path.basename(file_path)
                    }

                    UserApi(body).update_extraction(body['id'], data)

                    os.remove(file_path)

            os.remove(f"{config.doc_location}{body['filename']}")
