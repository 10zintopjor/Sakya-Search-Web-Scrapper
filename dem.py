import re
from typing_extensions import dataclass_transform

def get_err_links():
    new_link = []
    datas = ""
    with open("err.log","r") as f:
        datas = f.readlines()
    for data in datas:
        m = re.match("err: (.*)",data)
        new_link.append(m.group(1))
    return new_link