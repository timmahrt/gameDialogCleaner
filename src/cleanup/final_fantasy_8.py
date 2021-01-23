
import io
import os
import re

import utils

def clean(root, outputPath):
    '''

    Post-clean up thoughts
        Seems similar to FF7 but with more whitespace.
        Lots of inner monologue from Squall?
    '''
    locationRe = re.compile("\n\n[^\n(（『「①②③＋]+\n\n")

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    for fn, fd in utils.loadFiles(root):
        data = fd.read()

        data = data.strip()

        # For unmarked locations, mark them
        start = 0
        while True:
            match = locationRe.search(data, start)
            if match is None:
                break
            start = match.start() + 2 # pass the 2 leading newlines
            # text = data[match.start():match.end()]
            # if text.strip() == '':
            #     continue

            data = data[:start] + '＋＋' + data[start:]
            start += 2 # pass the 2 inserted characters

        data = data.replace('\n（', ':（')

        # Place quoted sections onto a single line
        start = 0
        while True:
            start = data.find('「', start)
            if start == -1:
                break
            end = data.find('」', start)

            speech = data[start:end].replace('\n', '')
            data = data[:start] + speech + data[end:]

            start = start + 1

        data = data.replace("\n「", ":「")
        data = data.replace("」:「", "」\n:「")
        data = data.replace("\n\n", "\n")

        data = markChoices(data)
        data = correctNumberOfQuotes(data)
        data = utils.removeQuoteMarksFromSpeech(data)
        data = utils.simplifyLongNewlineSequences(data)
        data = utils.addSpaceAfterChoiceMarker(data)
        data = utils.addLeadingWhitespaceWhenSameSpeaker(data, False)

        data = data.split('＊＊＊＊＊')[0]
        data = data.split('＋＋私的好き台詞＋＋')[0]
        data = data.strip() + '\n'

        data = '＋＋' + data
        data = data.replace("\n", "＋＋\n", 1)

        with io.open(os.path.join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write(data)

def markChoices(data):
    returnList = []
    for line in data.split("\n"):
        if '⇒' in line or line.endswith('を選択'):
            line = '○' + line.lstrip('＋＋　')
        returnList.append(line)

    return "\n".join(returnList)

def correctNumberOfQuotes(data):
    returnList = []
    for line in data.split("\n"):
        numOpen = line.count('「')
        numClose = line.count('」')

        if numOpen > numClose and line[-1] == '」':
            line += '」'

        returnList.append(line)

    return "\n".join(returnList)
