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
    csv_rows = []
    with open('pechas_catalogv1.txt','r')as file:
        csv_rows = file.readlines()
    return csv_rows

def delete_repo(id):
    github_utils.delete_repo(id)

if __name__ == "__main__":
    pecha_ids = get_pecha_names()
    for pecha_id in pecha_ids:
        id = pecha_id.replace("\n","")
        try:
            delete_repo(id)
            print(f"deleted {id}")
        except:
            print("already deleted")