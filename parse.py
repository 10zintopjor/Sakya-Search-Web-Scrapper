from bs4 import BeautifulSoup
import requests

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
    text_meta = page.select_one("div.etext-page-border-center.etext-titlepage").text
    next_page = page.select_one("div.etext-page-border-right.with-page-link a")['href']
    base_text = extract_base_text(main_url+next_page)
    return base_text


def extract_base_text(url):
    page = get_page(url)
    base_text=[]
    base_text.append(page.select_one("div.etext-body").text)
    #pagination = page.select_one("ul.pagination").text
    next_page = page.select_one("div.etext-page-border-right.with-page-link a")
    if next_page != None:
        base_text.extend(extract_base_text(main_url+next_page['href']))
    return base_text

def get_pecha_links(url):
    page = get_page(url)
    e_texts = []
    links = [i.attrs.get('href') for i in page.select("div.listing a")]
    e_texts.extend(links)
    next_page = page.select_one("ul.pagination li.next a")
    if next_page != None:
        e_texts.extend(get_pecha_links(main_url+next_page['href']))
    return e_texts    


def main():
    page = get_page(sample_url)
    langs_url = get_languages_url(page)
    for lang_url in langs_url:
        texts = get_text(main_url+lang_url['href'])
        print(len(texts))
        break


if __name__ == "__main__":
    """ urls = get_pecha_links(e_text_url)
    print(urls) """
    main()