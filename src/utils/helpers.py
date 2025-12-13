from datetime import datetime 
from typing import Callable
from playwright.sync_api import Page 
from src.builder import SpreadsheetBuilder
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor

def execution_time(callback,**kwargs):
    start = datetime.now()
    callback(**kwargs)
    end = datetime.now()
    duration = (end - start).seconds 
    print(f'the process last : {duration}')


def extract_sheets_related_infos(
        url,
        sheets_names:list[str],
        page:Page,
        builder:SpreadsheetBuilder):
    url_pipeline = Pipeline(
        url,
        [
            BaseSheetExtractor(sheet_name)
            for sheet_name in sheets_names
        ],
        page,
        builder 
    )
    url_pipeline.run()
    page.goto("about:blank")


def map_execution(urls:list[str],func:Callable,**kwargs):
    [func(url,**kwargs) for url in urls]