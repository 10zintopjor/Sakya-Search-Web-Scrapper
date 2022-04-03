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
    with open('sa.csv','r')as file:
        csv_rows = csv.reader(file)
        for row in csv_rows:
            csv_row.append(row[0])
    return csv_row

def delete_repo(id):
    github_utils.delete_repo(id)

if __name__ == "__main__":
    pecha_ids = get_pecha_names()
    for pecha_id in pecha_ids:
        try:
            delete_repo(f"{pecha_id}.opf")
            print(f"deleted {pecha_id}")
        except:
            print("already deleted")