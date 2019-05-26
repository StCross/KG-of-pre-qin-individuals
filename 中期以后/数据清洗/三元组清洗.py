#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def main():
    with open("CNdbpedia_tuples.json","r",encoding="UTF-8") as fr:
        individuals=json.load(fr)
    json_data=[]
    names = []
    new = []
    for individual in individuals:
        names.append(individual["name"])
    for individual in individuals:
        temp={}
        relations=[]
        properties=[]
        tuples=individual["tuples"]
        for tuple in tuples:
            if tuple[0] in["父亲","母亲","妻子","子女","儿子","女儿","辅佐","丈夫","下属","上司","同僚","叔父","侄子","前任","继任","兄长","姐姐","哥哥","弟弟"]:
                relations.append(tuple)
                if(tuple[1] not in names and tuple[1] not in new):
                    new.append(tuple[1])
            elif tuple[0] not in["本名","中文名","外文名"] and tuple[1] not in ["不详","?","？"]:
                properties.append(tuple)
            else:
                continue
        temp["name"]=individual["name"]
        temp["properties"]=properties
        temp["relations"]=relations
        json_data.append(temp)
    print(len(json_data))
    with open("三元组清洗.json","w", encoding="UTF-8") as fw:
        json.dump(json_data, fw , indent=4, ensure_ascii=False)
    print(new)


if __name__ == "__main__":
    main()