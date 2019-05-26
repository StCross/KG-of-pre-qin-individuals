#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
LTP_DATA_DIR = r"D:/LTP/ltp_data_v3.4.0"  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, "cws.model")  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, "pos.model")  # 词性标注模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR, "parser.model")  # 依存句法分析模型路径，模型名称为`parser.model
NE_model_path = os.path.join(LTP_DATA_DIR , "ner.model")
from pyltp import Segmentor
segmentor = Segmentor()
segmentor.load_with_lexicon(cws_model_path, "C:/Users/asus/Desktop/人物列表.txt")  # 分词模型
from pyltp import Postagger
postagger = Postagger()
postagger.load(pos_model_path)  # 词性标注模型
from pyltp import Parser
parser = Parser()
parser.load(par_model_path)  # 依存句法分析模型
from pyltp import NamedEntityRecognizer
recognizer = NamedEntityRecognizer()
recognizer.load(NE_model_path)  #命名实体识别模型


def build_child_dict_list(words,arcs):   #构建句法依存树，以每个词子节点及依存关系形式展现
    child_dict_list=list()
    for index in range(len(words)):
        child_dict=dict()
        for arc_index in range(len(arcs)):
            if arcs[arc_index].head == index + 1:
                if arcs[arc_index].relation in child_dict:
                    child_dict[arcs[arc_index].relation].append(arc_index)
                else:
                    child_dict[arcs[arc_index].relation] = []
                    child_dict[arcs[arc_index].relation].append(arc_index)
        child_dict_list.append( child_dict )
    return child_dict_list


def complete_e(words, postags, child_dict_list, word_index):   #遍历依存树直至叶子结点,提取特定关系以完善抽取
    child_dict = child_dict_list[word_index]
    prefix = ""
    if "ATT" in child_dict:
        for i in range(len(child_dict["ATT"])):
            prefix += complete_e(words, postags, child_dict_list, child_dict["ATT"][i])
    postfix = ""
    if postags[word_index] == "v":
        if "VOB" in child_dict:
            postfix += complete_e(words, postags, child_dict_list, child_dict["VOB"][0])
        if "SBV" in child_dict:
            prefix = complete_e(words, postags, child_dict_list, child_dict["SBV"][0]) + prefix
    return prefix + words[word_index] + postfix


def tuple_extract(sentence,docker,name):
    words = list(segmentor.segment(sentence)) # 分词
    postags = list(postagger.postag(words))  #词性标注
    netags = recognizer.recognize(words, postags) #命名实体识别
    arcs = parser.parse(words, postags)  # 句法分析
    child_dict_list = build_child_dict_list( words,arcs )
    for index in range( len( postags ) ):
        if postags[index] == "v":
            child_dict = child_dict_list[index]
            if "SBV" in child_dict  and "VOB" in child_dict :   #主谓宾
                e1 = complete_e(words, postags, child_dict_list, child_dict["SBV"][0])
                r = words[index]
                e2 = complete_e( words, postags, child_dict_list, child_dict["VOB"][0])
                if name in e1 or "他" in e1 or "其" in e1:
                    docker.append( "主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2) )
            # 抽取以谓词为中心的事实三元组

            if "SVB" in child_dict and "COO" in child_dict:
                e1 = complete_e(words,postags,child_dict_list, child_dict["SBV"][0])
                list_e2=list()
                list_r=list()
                for i in range(len(child_dict["COO"])):
                    child_dict_i=child_dict_list(child_dict["COO"][i])
                    list_e2.append(complete_e( words, postags, child_dict_list, child_dict_i["VOB"][0]))
                    list_r.append(words[child_dict["COO"][i]])
                if name in e1 or "他" in e1 or "其" in e1:
                    for e2,r in zip(list_e2,list_r):
                        docker.append( "主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2) )
            #抽取并列关系且以谓词为中心的三元组

            if arcs[index].relation == "ATT":
                if "VOB" in child_dict:
                    e1 = complete_e( words, postags, child_dict_list, arcs[index].head - 1 )
                    r = words[index]
                    e2 = complete_e( words, postags, child_dict_list, child_dict["VOB"][0] )
                    temp_string = r + e2
                    if temp_string == e1[:len( temp_string )]:
                        e1 = e1[len( temp_string ):]
                    if temp_string not in e1:
                        if name in e1 or "他" in e1 or "其" in e1:
                            docker.append( "主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2) )
            # 定语后置，动宾关系

            if "SBV" in child_dict and "CMP"in child_dict:
                # e1 = words[child_dict["SBV"][0]]
                e1 = complete_e( words, postags, child_dict_list, child_dict["SBV"][0] )
                cmp_index = child_dict["CMP"][0]
                r = words[index] + words[cmp_index]
                if "POB" in child_dict_list[cmp_index]:
                    e2 = complete_e( words, postags, child_dict_list, child_dict_list[cmp_index]["POB"][0] )
                    if name in e1 or "他" in e1 or "其" in e1:
                        docker.append( "主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2) )
            # 含有介宾关系的主谓动补关系

            if netags[index][0] == "S" or netags[index][0] == "B":
                ni = index
                if netags[ni][0] == "B":
                    while netags[ni][0] != "E":
                        ni += 1
                    e1 = "".join( words[index:ni + 1] )
                else:
                    e1 = words[ni]
                if arcs[ni].relation == "ATT" and postags[arcs[ni].head - 1] == "n" and netags[
                    arcs[ni].head - 1] == "O":
                    r = complete_e( words, postags, child_dict_list, arcs[ni].head - 1 )
                    if e1 in r:
                        r = r[(r.index( e1 ) + len( e1 )):]
                    if arcs[arcs[ni].head - 1].relation == "ATT" and netags[arcs[arcs[ni].head - 1].head - 1] != "O":
                        e2 = complete_e( words, postags, child_dict_list, arcs[arcs[ni].head - 1].head - 1 )
                        mi = arcs[arcs[ni].head - 1].head - 1
                        li = mi
                        if netags[mi][0] == "B":
                            while netags[mi][0] != "E":
                                mi += 1
                            e = "".join( words[li + 1:mi + 1] )
                            e2 += e
                        if r in e2:
                            e2 = e2[(e2.index( r ) + len( r )):]
                        if r + e2 in sentence:
                            if name in e1 or "他" in e1 or "其" in e1:
                                docker.append( "主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2) )
            # 尝试抽取命名实体有关的三元组


def main():
    file = open("数据爬取.json", "r" , encoding="UTF-8" )
    jsonfile_r = json.load(file)
    jsonfile_w =dict()
    for member in jsonfile_r:
        texts = member["texts"]
        name = member["name"]
        docker = list()
        for text in texts:
            for sentence in text.split("。"):
                tuple_extract(sentence,docker,name)
        jsonfile_w[name]=docker
    with open("关系抽取.json","w", encoding="UTF-8") as fw:
        json.dump(jsonfile_w, fw , indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()











