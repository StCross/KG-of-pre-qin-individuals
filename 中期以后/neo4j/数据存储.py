#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding:utf-8
from py2neo import Node,Graph,Relationship, NodeMatcher
import json

graph = Graph( "bolt://localhost:7687",username="neo4j", password="wsgmss" )
names=[]

def create_person(individual):
    global graph
    person_name=individual["name"]
    name=Node("Person",name = person_name)
    if len(individual["properties"])>0:
        for pro in individual["properties"]:
            name[pro[0]]=pro[1]
    graph.create(name)


def create_relation(individuals):
    global graph
    matcher = NodeMatcher(graph)
    for individual in individuals:
        name=individual["name"]
        if len( individual["relations"] ) > 0:
            for rel in individual["relations"]:
                try:
                    e2e= Relationship(matcher.match("Person", name=name).first(),rel[0],matcher.match("Person", name=rel[1]).first())
                    graph.create(e2e)
                except AttributeError:
                    print(matcher.match("Person", name=name).first(),rel[0],matcher.match("Person", name=rel[1]).first())


def main():
    with open("三元组清洗.json","r",encoding="UTF-8") as fr:
        individuals=json.load(fr)
    for individual in individuals:
        create_person(individual)
    create_relation(individuals)

        

if __name__ == "__main__":
    main()



