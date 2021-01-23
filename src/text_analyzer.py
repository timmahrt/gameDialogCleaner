
import os
import io
import csv

import MeCab
from sudachipy import tokenizer, dictionary

import utils

def getChunks(words, size):
    retList = []
    for i in range(len(words) - (size - 1)):
        retList.append(tuple(words[i: i + size]))
    return retList

def getFrequency(grams):
    retList = []
    for orderId, gram in enumerate(set(grams)):
        freq = grams.count(gram)
        retList.append([freq, orderId, gram])
    return retList


def pruneRareSequences(grams, minOccurance):
    retGrams = []
    for freq, orderId, gram in grams:
        if freq < minOccurance:
            continue
        retGrams.append([freq, orderId, gram])

    return retGrams


def _output(outputDir, unigrams, bigrams, trigrams, fourgrams):
    print(outputDir)
    for fn, grams in [
            ['unigrams.csv', unigrams],
            ['bigrams.csv', bigrams],
            ['trigrams.csv', trigrams],
            ['fourgrams.csv', fourgrams]
    ]:
        gramOutList = getFrequency(grams)
        if fn != 'unigrams.csv':
            gramOutList = pruneRareSequences(gramOutList, 2)
        gramOutList.sort()
        with io.open(os.path.join(outputDir, fn), "w", encoding="utf-8") as fd:
            csvwriter = csv.writer(fd)
            for row in gramOutList:
                csvwriter.writerow(row)


def extractDialogWithMecab(rootDir):

    outputDir = utils.getOutputPath(rootDir, 'stats')
    parser = MeCab.Tagger("-Owakati")
    unigrams = []
    bigrams = []
    trigrams = []
    fourgrams = []
    for fn, fd in utils.loadFiles(rootDir):
        for line in fd:
            wordList = parser.parse(line).split()
            unigrams.extend(getChunks(wordList, 1))
            bigrams.extend(getChunks(wordList, 2))
            trigrams.extend(getChunks(wordList, 3))
            fourgrams.extend(getChunks(wordList, 4))

    _output(outputDir, unigrams, bigrams, trigrams, fourgrams)


def extractDialogWithSudachi(rootDir):
    outputDir = utils.getOutputPath(rootDir, 'stats')
    tokenizer_obj = dictionary.Dictionary().create()
    mode = tokenizer.Tokenizer.SplitMode.C

    unigrams = []
    bigrams = []
    trigrams = []
    fourgrams = []
    POS_LIST = [
        '名詞',
        '動詞',
        '副詞',
        '形容詞',
        '連体詞',
        '形状詞'
    ]
    for fn, fd in utils.loadFiles(rootDir):
        for line in fd:
            line = line.strip()
            wordList = []
            for word in tokenizer_obj.tokenize(line, mode):
                if word.part_of_speech()[0] not in POS_LIST:
                    continue
                wordList.append((word.dictionary_form(), word.part_of_speech()[0]))
                print([word.surface(), word.dictionary_form(), word.part_of_speech()[0]])

            unigrams.extend(getChunks(wordList, 1))
            bigrams.extend(getChunks(wordList, 2))
            trigrams.extend(getChunks(wordList, 3))
            fourgrams.extend(getChunks(wordList, 4))

    _output(outputDir, unigrams, bigrams, trigrams, fourgrams)


if __name__ == "__main__":
    rootDir = 'ff8/cleaned/dialog/'
    # extractDialogWithMecab(rootDir)
    extractDialogWithSudachi(rootDir)
