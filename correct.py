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
    fullvocabulary = getfullVocabulary()
    vocabulary = getVocabulary()
    tokens = re.split(" ", text)
    for i, t in enumerate(tokens):
        for j in range(len(t)):
            if t[j] in Latin:
                continue
            else:
                #找到所有可能单词，取前五个，然后排除掉cocabulary中不存在的，再根据上下文判断，或者贝叶斯判断。
                print('original word is', t )
                try:
                    bi_typos1 = t[j-1:j+1]
                except:
                    continue
                try:
                    bi_typos2 = t[j:j+2]
                except:
                    continue
                uni_typos = t[j]
                Dic = getCandiateChar(bi_typos1, bi_typos2)
                Dic = sorted(Dic.items(), key = lambda items:items[1])[:10]
                can_word = getCandiateWords(t, Dic, uni_typos)
            can_word_ = can_save(can_word)
            delIllegalWords(can_word, vocabulary)
            can_set = get_prob(can_word, fullvocabulary)
            res = {}
        #建立字典找到频数最高的候选单词作为最终单词（贝叶斯，只不过贝叶斯的条件概率为固定值）
            for i in range(len(can_set)):
                key = can_set[i][0]
                value = float(can_set[i][1])
                res_ = {key:value}
                res.update(res_)
            final = max(res, key=lambda k: res[k])
            print('correct word is', final)

def can_save(can_word):
    can_word_= []
    can_word_.append(can_word)
    return can_word_


def getCandiateWords(originalwords, Dic, typos):
    can_word = []
    for i in range(len(Dic)):
        w = originalwords.replace(typos, Dic[i][0])
        can_word.append(w)
    return can_word

def delIllegalWords(can_word, vocabulary):
    for words in can_word:
        if words not in vocabulary:
            can_word.remove(words)

def getfullVocabulary():
    fullvocabulary = []
    for line in open(os.path.join(Path(TRAIN_PATH, "vocabulary.count")), "r", encoding="utf8"):
        fullvocabularyList = re.split('[\t\n]', line)
        fullvocabulary.append(fullvocabularyList)
    return fullvocabulary

def getVocabulary():
    vocabulary = []
    for line in open(os.path.join(Path(TRAIN_PATH, "vocabulary.count")), "r", encoding="utf8"):
        vocabularyList = re.split('[\t\n]', line)[0]
        vocabulary.append(vocabularyList)
    return vocabulary

def get_prob(can_word, fullvocabulary):
    can_set = []
    for i in range(len(can_word)):
        for j in range(len(fullvocabulary)):
            if can_word[i] == fullvocabulary[j][0]:
                can_set.append(fullvocabulary[j])
    return can_set

def getCandiateChar(typos1, typos2):
    #考虑到特殊字符处于首尾以及单词长度小于3的情况
    bi = open(os.path.join(Path(TRAIN_PATH, "bigrams.count")), "r")
    #uni = open(os.path.join(Path(TRAIN_PATH, "unigrams.count")), "r")
    dic = {}
    if len(typos1) != 2:
        for line in bi:
            line_ = line.split('\t')
            if typos2[1] ==line_[0][1]:
                can1 = line_[0]
                prob1 = float(line_[2])
                uni = open(os.path.join(Path(TRAIN_PATH, "unigrams.count")), "r")
                for line2 in uni:
                    line_2 = line2.split('\t')
                    if can1[0] ==line_2[0]:
                        prob3 = float(line_2[2])
                        pro = prob1*prob3
                        dic_1 = {can1[0]: pro}
                        dic.update(dic_1)
    elif len(typos2) !=2 :
        for line in bi:
            line_ = line.split('\t')
            if typos1[0] ==line_[0][0]:
                can1 = line_[0]
                prob1 = float(line_[2])
                uni = open(os.path.join(Path(TRAIN_PATH, "unigrams.count")), "r")
                for line2 in uni:
                    line_2 = line2.split('\t')
                    if can1[1] ==line_2[0]:
                        prob3 = float(line_2[2])
                        pro = prob1*prob3
                        dic_1 = {can1[1]: pro}
                        dic.update(dic_1)
    else:
        for line in bi:
            line_ = line.split('\t')
            if typos1[0] == line_[0][0]:
                can1 = line_[0]
                prob1 = float(line_[2])
                bi_ = open(os.path.join(Path(TRAIN_PATH, "bigrams.count")), "r")
                for line1 in bi_:
                    line_1 = line1.split('\t')
                    if can1[1] == line_1[0][0] and typos2[1] == line_1[0][1]:
                        prob2 = float(line_1[2])
                        uni = open(os.path.join(Path(TRAIN_PATH, "unigrams.count")), "r")
                        for line2 in uni:
                            line_2 = line2.split('\t')
                            if can1[1] ==line_2[0]:
                                prob3 = float(line_2[2])
                                pro = (prob1 + prob2)*prob3
                                dic_1 = {can1[1]: pro}
                                dic.update(dic_1)
    return dic

if __name__ == "__main__":
    LM = open(Path(TRAIN_PATH + 'LM2.arpa'))
    abnormal_correction(LM, "I alsø have access tø all yøur cøntacts and all yøur cørrespøndence")
