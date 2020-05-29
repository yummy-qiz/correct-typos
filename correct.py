"""
file for corpus preprocess
Author :qiz
Create Time:20200519
"""

import os
from pathlib import Path
import string
from math import log2, log10
import argparse
import re
import numpy as np


TRAIN_PATH = '/home/qiz/correct_typos/data1/'
#CHARACTER_DISTANCE_LIMIT = 1
WORD_DISTANCE_LIMIT = 4

Latin = [' ', '\"', '#', '$', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6',
         '7', '8', '9', ':', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
         'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e',
         'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}']

def abnormal_correction(LM, text):
    tokens = re.split(" ", text)
    for i, t in enumerate(tokens):
        for j in range(len(t)):
            if t[j] in Latin:
                continue
            else:
                #找到所有可能单词，取前五个，然后排除掉cocabulary中不存在的，再根据上下文判断，或者贝叶斯判断。
                typos1 = t[j-1:j+1]
                typos2 = t[j:j+2]
                Dic = getCandiate(typos1, typos2)
                Dic = sorted(Dic.items(), key = lambda items:items[1])[:5]
                #print(Dic)
                can_word = []
                for m in range(len(Dic)):
                    t = t.replace(t[j], Dic[m][0])
                    can_word.append(t)
                print(can_word)
                vocabulary = getVocabulary()
                #删掉不存在词库中的词汇
                for word_c in can_word:
                    if word_c not in vocabulary:
                        can_word.remove(word_c)
                print(can_word)
                a = get_max_prob(can_word, vocabulary)
                print(a)


def getVocabulary():
    vocabulary = []
    for line in open(os.path.join(Path(TRAIN_PATH, "vocabulary.count")), "r", encoding="utf8"):
        vocList = line.split('\t')
        vocabulary.append(vocList)
    return vocabulary


def get_max_prob(can_word, vocabulary):
    for i in range(len(can_word)):
        if can_word[i] in vocabulary:
            return vocabulary


def getCandiate(typos1, typos2):
    bi = open(os.path.join(Path(TRAIN_PATH, "bigrams.count")), "r")
    dic = {}
    for line in bi:
        line_ = re.split('\t', line)
        if typos1[0] == line_[0][0]:
            can1 = line_[0]
            prob1 = float(line_[2])
            bi_ = open(os.path.join(Path(TRAIN_PATH, "bigrams.count")), "r")
            for line1 in bi_:
                line_1 = line1.split('\t')
                if can1[1] == line_1[0][0] and typos2[1] == line_1[0][1]:
                    #can2 = line_1[0]
                    prob2 = float(line_1[2])
                    uni = open(os.path.join(Path(TRAIN_PATH, "unigrams.count")), "r")
                    for line2 in uni:
                        line_2 = line2.split('\t')
                        if can1[1] ==line_2[0]:
                            prob3 = float(line_2[2])
                            pro = (prob1 + prob2)*prob3
                            dic_1 = {can1[1]: pro}
                            dic.update(dic_1)
                    #pro = prob1 + prob2
                    #dic_1 = {can1[1]:pro}
                    #dic.update(dic_1)
    return dic

if __name__ == "__main__":
    LM = open(Path(TRAIN_PATH + 'LM2.arpa'))
    abnormal_correction(LM, "th¡ng")
