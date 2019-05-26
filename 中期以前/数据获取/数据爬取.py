#!/usr/bin/python
# coding=<utf-8>
import json
import xlrd
import xlwt
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


def getinfo(url, name):
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    items = soup.findAll("dt", {"class":"basicInfo-item name"})
    values = soup.findAll("dd", {"class":"basicInfo-item value"})
    texts = soup.findAll("div", {"class":"para", "label-module":"para"})
    info = {}
    temp_infobox = {}
    temp_text = []
    info["name"] = name.strip()
    for item, value in zip(items, values):
        temp_infobox["".join(item.get_text().split())] = value.get_text().strip()
    info["infobox"] = temp_infobox
    for text in texts:
        temp_text.append(text.get_text().strip())
    sentences = []
    for text in temp_text:
        for sentence in text.split( "。" ):
            if len( sentence ) >= 5:
                sentences.append(sentence)
    info["sentences"] = sentences
    return info


def main():
    jsonfile = []
    base = r"https://baike.baidu.com/item/"
    file = xlrd.open_workbook(r"融合后人物.xls")
    sheet = file.sheets()[0]
    names = sheet.col_values(0)
    nonelist=[]
    num=0
    for name in names:
        url = base+name
        info = getinfo(url, name)
        if len(info["sentences"]) >0:
            num+=1
            jsonfile.append(info)
     #   else:
     #       nonelist.append(name)
        print("已经爬取",num,"\r")
    with open("百度百科.json","w", encoding="UTF-8") as fw:
        json.dump(jsonfile, fw , indent=4, ensure_ascii=False)
    #with open("无百科词条人物.txt","w",encoding="UTF-8") as fx:
        #for name in nonelist:
            #fx.write(name+"\n")
    '''
    for name in nonelist:
        names.remove(name)
    wb = xlwt.Workbook()
    ws = wb.add_sheet("可获取词条人物")
    i=0
    for name in names:
        ws.write(i,0,name)
        i+=1
    wb.save( "可获取词条人物.xls")
'''

if __name__ == "__main__":
    main()

      


