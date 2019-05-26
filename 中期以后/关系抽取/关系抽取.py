#!/usr/bin/env python
# -*- coding: utf-8 -*-
import jiagu
import json

with open("百度百科.json","r",encoding="UTF-8") as fr:
    individuals=json.load(fr)
json_data=[]
for individual in individuals:
    temp={}
    tuples=[]
    temp["name"]=individual["name"]
    temp["infobox"]=individual["infobox"]
    for sentence in individual["sentences"]:
        knowledge = jiagu.knowledge(sentence)
        dic = {sentence: knowledge}
        tuples.append(dic)
    temp["tuples"]=tuples
    json_data.append(temp)
with open("关系抽取.json","w", encoding="UTF-8") as fw:
        json.dump(json_data, fw , indent=4, ensure_ascii=False)
