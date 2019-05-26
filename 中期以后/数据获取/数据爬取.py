#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import xlrd
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import time

def get_tuple_CN(name):
    base=r"http://shuyantech.com/api/cndbpedia/avpair?q="
    url=base+name
    try:
        html = urlopen(url)
    except HTTPError:
        return 0 #无人物
    soup = BeautifulSoup( html, "html.parser")
    tuple_list =json.loads(soup.get_text())
    if tuple_list=={"status":"fail", "reason": "too many requests"}:
        return 1 #请求达到上限
    tuple_list=tuple_list["ret"]
    print(name)
    tuples = {}
    infobox=[]
    for member in tuple_list:
        if member[0] not in["本名","中文名","CATEGORY_ZH","DESC"]:
            infobox.append([member[0],member[1]])
    if len(infobox)==0:
        return False
    else:
        tuples["name"]=name
        tuples["infobox"]=infobox
    time.sleep(1)
    return tuples

def get_tuple_wiki(name):
    base = r"http://zhishi.me/zhwiki/resource/"
    tuples={}
    url = base + name
    try:
        html = urlopen(url)
    except HTTPError:
        return 0 #无人物
    soup = BeautifulSoup( html, "html.parser" )
    keys=soup.findAll("strong")
    values=soup.findAll("span",{"class":"val"})
    infobox=[]
    for key,value in zip(keys,values):
        infobox.append([key.get_text(),value.get_text()])
    if len(infobox)==0:
        return 1 #无信息盒
    else:
        tuples["name"]=name
        tuples["infobox"]=infobox
    return tuples


def main():
    file = xlrd.open_workbook( r"先秦人物.xlsx" )
    sheet = file.sheets()[0]
    names = sheet.col_values(0)
    json_data=[]
    none=[]
    for name in names:
        temp=get_tuple_CN(name)
        if temp not in[0,1]:
            json_data.append(temp)
        else:
            temp=get_tuple_wiki(name)
            if temp not in[0,1]:
                json_data.append(temp)
            else:
                none.append(name)
    print(len(json_data))
    with open( "数据爬取.json", "w", encoding="UTF-8" ) as fw:
        json.dump(json_data, fw, indent=4, ensure_ascii=False )
        print(none)

if __name__ == "__main__":
    main()