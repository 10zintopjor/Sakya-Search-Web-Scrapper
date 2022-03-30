from bs4 import BeautifulSoup
import requests

sample_url = "https://sakyaresearch.org/etexts/1183"
main_url = "https://sakyaresearch.org"

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
    next_link = page.select_one("div.etext-page-border-right.with-page-link a")['href']
    base_text = extract_base_text(main_url+next_link)
    print(base_text)

def extract_base_text(url):
    page = get_page(url)
    base_text=[]
    base_text.append(page.select_one("div.etext-body").text)
    #pagination = page.select_one("ul.pagination").text
    next_link = page.select_one("div.etext-page-border-right.with-page-link a")
    if next_link != None:
        base_text.extend(extract_base_text(main_url+next_link['href']))
    return base_text


def main():
    page = get_page(sample_url)
    langs_url = get_languages_url(page)
    for lang_url in langs_url:
        get_text(main_url+lang_url['href'])
        break


if __name__ == "__main__":
    main()