#Raam Nachiappan, rnachiap, 45618246
#Preston So, prestons, 33974506

from bs4 import BeautifulSoup
from math import log10
import numpy as np
import json
import os
import re

TOTAL_FILES = 1001
pattern = re.compile('[a-zA-Z0-9]+')
folders =["0", "1", "2"]
tags = ['strong', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'header','em', 'head', 'body', 'p', 'table', 'tr', 'td', 'th', 'span']
boldtags = ['strong', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'header']
normtags = ['em', 'body', 'p', 'table', 'tr', 'td', 'th', 'span']
bigDict = dict() #File and tfidf values
fileFrequency = dict() #File and number of query words in them
dictLists = [] #List of dictionaries for each query term


#Loads dictionaries from npy files made from tokenize function
inverseIndexHeaders = np.load('inverseIndexHeaders.npy').item()
bold_words = np.load('boldwords.npy').item()
norm_words = np.load('norm_words.npy').item()

#Returns IDF value num of documents/num of documents word is in
def idf(term, wordIndex):
    return (1 + log10(1001/len(wordIndex[term])))

#returns a tfidf dict which is file:tfidf value
def tfidf(term, wordIndex):
    tfidfDict = dict()
    files = wordIndex[term]
    for i in files:
        absPath = os.path.abspath(i[0] + "/" + i[1])
        infile = open(absPath)
        f = infile.read()
        soup = BeautifulSoup(f, "lxml")
        a = soup.text.encode('utf-8').strip()
        total_terms = pattern.findall(a)
        num_of_terms = len(total_terms)
        wordCount = 0
        for j in total_terms:
            if j.lower() == term:
                wordCount += 1
        if num_of_terms < 30:
            tf = 0
        elif i in bold_words[term] and i in norm_words[term]:
            tf = float(wordCount * 1)/num_of_terms
        elif i in norm_words[term]:
            tf = float(wordCount * 1)/num_of_terms
        else:
            tf = float(wordCount)/num_of_terms
        tfidf_value = tf * idf(term, wordIndex)
        tfidfDict[(i[0], i[1])] = tfidf_value
    return tfidfDict

#returns big dictionary of file:tfidf value by adding term tfidf values together
#  also increases value if more query words are in the file
def calcTopPages(dictLists):
    for dict in dictLists:
        for i in dict:
            if i in bigDict:
                fileFrequency[i] += 1
                bigDict[i] += dict[i]
                if fileFrequency[i] == len(dictLists):
                    bigDict[i] *= 100
            else:
                fileFrequency[i] = 1
                bigDict[i] = dict[i]
    return bigDict

#Takes user input for a query and creates dict lists for each term to their tfidf value
def queryInput():
    global dictLists
    query = ""
    while (query == ""):
        query = raw_input("Enter your search query: ").lower()
    query = pattern.findall(query)
    for i in range(len(query)):
        dictLists.append(dict())
    for i in range(len(query)):
        try:
            dictLists[i] = tfidf(query[i], inverseIndexHeaders)
        except:
            continue
    calcTopPages(dictLists)

#Reads json file and sorts the bigDict into an ordered dictionary by tfidf value and prints the top 10 URLs
def returnURL(bigDict):
    with open('bookkeeping.json') as data_file:
        jsonObj = json.load(data_file)
    rankedDict = sorted(bigDict, key = bigDict.get, reverse=True)
    URLcount = 0
    for i in range(len(rankedDict)):
        if URLcount == 20:
            break
        folder, file = str(rankedDict[i][0]), str(rankedDict[i][1])
        print(jsonObj[folder + "/" + file])
        URLcount += 1

#Runs the program
if __name__ == "__main__":
    queryInput()
    returnURL(bigDict)

#Tokenize function we used to create initial dictionaries
    # def tokenize(tags):
    #     d = {}
    #     for folder in folders:
    #         for file in os.listdir(folder):
    #             absPath = os.path.abspath(folder + "/" + file)
    #             infile = open(absPath)
    #             f = infile.read()
    #             soup = BeautifulSoup(f, "lxml")
    #             for i in soup.find_all(tags):
    #                 for j in i.contents:
    #                     s = (j).encode('utf-8').strip()
    #                     for k in pattern.findall(s):
    #                         k = k.lower()
    #                         if k in d:
    #                             if (folder,file) in d[k]:
    #                                 continue
    #                             d[k].append((folder,file))
    #                         else:
    #                             d[k] = [(folder,file)]
    #     return d
    #
    # inverseIndexHeaders = tokenize(tags)
    # bold_words = tokenize(boldtags)
    # norm_words = tokenize(normtags)
    #
    # np.save('inverseIndexHeaders.npy', inverseIndexHeaders)
    # np.save('boldwords.npy', bold_words)
    # np.save('norm_words.npy', norm_words)