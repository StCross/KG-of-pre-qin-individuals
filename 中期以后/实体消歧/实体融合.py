#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def main():
    with open("百度百科.json", "r" ,encoding="UTF-8") as fr:
        individuals=json.load(fr)
        jsondata={}
        for individual in individuals:
            infobox=individual["infobox"]
            synos=[]
            try:
                synos.extend(infobox["别称"].split("、"))
            except KeyError:
                pass
            try:
                synos.extend(infobox["别名"].split("、"))
            except KeyError:
                pass
            for syno in synos:
                if syno==individual["name"]:
                    synos.remove(syno)
            jsondata[individual["name"]]=synos
    with open( "实体融合.json", "w", encoding="UTF-8" ) as fw:
        json.dump(jsondata, fw, indent=4, ensure_ascii=False )



if __name__ == "__main__":
    main()