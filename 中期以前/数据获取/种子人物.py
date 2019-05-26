#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import xlwt

base = r"https://tieba.baidu.com/p/4460566858?pn="


def getlist(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    infos = soup.findAll("div", {"class": "post_bubble_middle_inner"})
    names = []
    for info in infos:
        text = info.get_text()
        print(text)
        temp1 = text.split("。")
        temp2 = temp1[0].split("，")
        try:
            names.append(temp2[1])
        except IndexError:
            pass
    return names


def main():
    file = xlwt.Workbook()
    sheet = file.add_sheet("种子人物")
    i = 0
    for j in range(1, 11):
        url = base+str(j)
        namelist = getlist(url)
        for name in namelist:
            sheet.write(i, 1, name)
            i += 1
    file.save("人物列表.xls")


if __name__ == "__main__":
    main()
