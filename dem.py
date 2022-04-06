import re
import csv
import git
import github
from openpecha import github_utils


def get_err_links():
    new_link = []
    datas = ""
    with open("err.log","r") as f:
        datas = f.readlines()
    for data in datas:
        m = re.match("err: (.*)",data)
        new_link.append(m.group(1))
    return new_link

def get_pecha_names():
    csv_row = []
    with open('pechas_catalog.log','r')as file:
        csv_rows = csv.reader(file)
        for row in csv_rows:
            csv_row.append(row[0])
    return csv_row

def delete_repo(id):
    github_utils.delete_repo(id)

if __name__ == "__main__":
    err_links =get_err_links()
    for err_link  in err_links:
        print(err_link)