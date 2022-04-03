from curses.textpad import Textbox
from urllib.parse import ParseResultBytes
from bs4 import BeautifulSoup
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.annotation import Page, Span
from pathlib import Path
import requests
from uuid import uuid4
from datetime import datetime
import re
import logging
from openpecha import github_utils,config


pechas_catalog = ''
alignment_catalog = ''
err_log = ''
sample_url = "https://sakyaresearch.org/etexts/1183"
main_url = "https://sakyaresearch.org"
e_text_url = "https://sakyaresearch.org/etexts?filter%5Blanguage_id%5D=2"


def get_page(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content,"html.parser")
    return soup


def get_languages_url(page):
    langs = page.select("div.btn-group.btn-group-justified.etext-language-switch a")
    return langs


def get_text(url):
    page = get_page(url)  
    next_page = page.select_one("div.etext-page-border-right.with-page-link a")['href']
    base_text = extract_base_text(main_url+next_page)
    src_meta = parse_text_meta(page)
    return base_text,src_meta


def parse_text_meta(page):
    src_meta = {}
    title_page_div = page.select_one("div.etext-page-border-center.etext-titlepage")
    src_meta['title'] =  re.match("(.*)\{.*\}",title_page_div.select_one("div>div:nth-of-type(1) h1").text).group(1).replace("'","")
    src_meta['description']= change_text_format(title_page_div.select_one("div>div:nth-of-type(2)").text)
    src_meta['source'] = main_url
    src_meta['file_info'] = [change_text_format(i.text) for i in title_page_div.select("div>div:nth-of-type(5) li")]
    src_meta['responibilities'] = [change_text_format(i.text) for i in title_page_div.select("div>div:nth-of-type(3)>div:nth-of-type(2) li")]
    src_meta['text_witnesses'] = main_url+title_page_div.select_one("div>div:nth-of-type(4) a")['href']

    return src_meta


def extract_base_text(url):
    page = get_page(url)
    base_text={}
    text = re.sub("\[\D:\d+\D?\]","",page.find("div",{"class": ["etext-body", "etext-front"]}).text)
    pagination = convert_pagination(page.select_one("div.col-sm-8 div.row div:nth-child(2)").text.strip().replace("\n",""))
    base_text.update({change_text_format(text):pagination})
    next_page = page.select_one("div.etext-page-border-right.with-page-link a")
    if next_page != None:
        base_text.update(extract_base_text(main_url+next_page['href']))
    return base_text


def convert_pagination(pagination):
    new_pagination =""
    m = re.match(".*:(\d+)(\D+)",pagination)
    if re.match(".*:\[-\]",pagination):
        return None
    if m.group(2) == "a":
        new_pagination = int(m.group(1))*2 -1
    elif m.group(2) == "b":
        new_pagination = int(m.group(1))*2  
    return new_pagination


def get_pecha_links(url):
    page = get_page(url)
    e_texts = []
    links = [i.attrs.get('href') for i in page.select("div.listing a")]
    e_texts.extend(links)
    next_page = page.select_one("ul.pagination li.next a")
    if next_page != None:
        e_texts.extend(get_pecha_links(main_url+next_page['href']))
    return e_texts    


def get_base_layer(text_with_pagination,src_meta):
    bases = {}
    text_clean = ""
    for text in text_with_pagination:
        text_clean +=text+"\n\n"
    bases.update({src_meta['title']:text_clean})
    return bases


def get_layers(text_with_pagination,src_meta):
    layers = {}
    layers[src_meta['title']] = {
        LayerEnum.pagination : get_pagination_layers(text_with_pagination)
    }
    return layers


def get_pagination_layers(text_with_pagination):
    page_annotations = {}
    char_walker = 0
    for text in text_with_pagination:
        pagination = text_with_pagination[text]
        page_annotation,char_walker = get_page_annotation(text,char_walker,pagination)
        page_annotations.update(page_annotation)

    pagination_layer = Layer(
        annotation_type=LayerEnum.pagination,annotations=page_annotations
    ) 
    return pagination_layer


def get_page_annotation(text,char_walker,pagination):
    page_start = char_walker
    page_end = char_walker + len(text)
    page_annotation = {
        uuid4().hex:Page(span=Span(start = page_start,end =page_end),imgnum=pagination)
    }    
    return page_annotation,page_end+2


def get_metadata(src_meta):
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata= src_meta)
    return instance_meta


def create_opf(opf_path,text_with_pagination,src_meta):
    opf = OpenPechaFS(
        meta= get_metadata(src_meta),
        base=get_base_layer(text_with_pagination,src_meta),
        layers= get_layers(text_with_pagination,src_meta)
        )
    opf_path = opf.save(output_path=opf_path)
    write_readme(src_meta,opf_path)
    return opf_path


def remove_double_linebreak(text):
    prev = ""
    new_text = ""

    for i in range(len(text)):
        if text[i] == "\n" and prev == "\n":
            continue
        new_text += text[i]
        prev = text[i]

    return new_text.strip("\n").strip()


def change_text_format(text):
    text = remove_double_linebreak(text)
    base_text=""
    prev= ""
    text = text.replace("\n","") 
    ranges = iter(range(len(text)))
    for i in ranges:
        if i<len(text)-1:
            if i%170 == 0 and i != 0 and re.search("\s",text[i+1]):
                base_text+=text[i]+"\n"
            elif i%170 == 0 and i != 0 and re.search("\S",text[i+1]):
                while i < len(text)-1 and re.search("\S",text[i+1]):
                    base_text+=text[i]
                    i = next(ranges) 
                base_text+=text[i]+"\n" 
            elif prev == "\n" and re.search("\s",text[i]):
                continue
            else:
                base_text+=text[i]
        else:
            base_text+=text[i]
        prev = base_text[-1]    
    return base_text[:-1] if base_text[-1] == "\n" else base_text


def set_up_logger(logger_name):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(message)s")
    fileHandler = logging.FileHandler(f"{logger_name}.log")
    fileHandler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(fileHandler)
    return logger

def write_readme(source_metadata,opf_path):
    Table = "| --- | --- "
    Title = f"|Title | {source_metadata['title'].strip()} "
    pecha_id = f"|pecha_id | {opf_path.stem}"
    source = f"|Source | {main_url}"
    readme = f"{Title}\n{Table}\n{pecha_id}\n{source}"
    Path(opf_path.parent / "readme.md").write_text(readme)


def publish_pecha(opf_path):
    github_utils.github_publish(
    opf_path.parent,
    not_includes=[],
    message="initial commit"
    )
    print("Published ",opf_path.stem)


def main():
    global pechas_catalog,err_log
    pechas_catalog = set_up_logger("pechas_catalog")
    err_log = set_up_logger('err')
    opf_path = Path('./opfs')
    e_text_links = get_pecha_links(e_text_url)
    for e_text_link in e_text_links:
        page = get_page(main_url+e_text_link)
        lang_urls = get_languages_url(page)
        for lang_url in lang_urls:
            try:
                opf_path = Path('./opfs')
                texts,src_meta = get_text(main_url+lang_url['href'])
                opf_path = create_opf(opf_path,texts,src_meta)
                publish_pecha(opf_path)
                pechas_catalog.info(f"{opf_path.stem},{src_meta['title']}")
            except:
                err_log.info(f"err: {e_text_link}")

if __name__ == "__main__":
    main()