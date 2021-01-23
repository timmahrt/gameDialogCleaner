
import io
import os
import re

import utils

def clean(root, outputPath):
    '''

    Seems similar to FF7 but with each line indented and two kinds of spaces ^^"
    '''
    indentationRe = re.compile("\n *")
    indentationRe2 = re.compile("\n *　?\n")
    ideographicSpaceRe = re.compile("　?")
    ideographicSpaceRe2 = re.compile("　?「")

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    for fn, fd in utils.loadFiles(root):
        data = fd.read()
        data = replaceEventMarker(data)

        data = removeDuplicatedHeader(data)
        data = formatChoices(data)

        data = ideographicSpaceRe2.sub('「', data)
        data = indentationRe2.sub('\n\n', data)
        data = indentationRe.sub('\n', data)
        data = data.replace('\n　', '') # U+3000, ideographic space
        data = ideographicSpaceRe.sub('', data)
        #data = data.replace(CHOICE_CHAR, '\n\n' + CHOICE_CHAR)

        data = replaceNonSpeechQuotes(data)
        data = addOpeningQuoteMark(data)
        data = handleInternalDialog(data)
        data = addClosingQuoteMark(data)
        data = insertColonBeforeQuotes(data)

        data = data.replace("\n「", ":「")
        data = data.replace("」:「", "」\n:「")

        data = data.replace("□", "＋＋")
        data = data.replace("ATE", "＋＋ATE")

        # data = data.replace("\n\n", "\n")
        data = utils.removeQuoteMarksFromSpeech(data)
        data = utils.simplifyLongNewlineSequences(data)
        data = utils.addSpaceAfterChoiceMarker(data)
        data = utils.addLeadingWhitespaceWhenSameSpeaker(data, False)
        data = data.strip() + '\n'

        with io.open(os.path.join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write(data)

def replaceEventMarker(data):
    return data.replace('○○', 'XX').replace('○', '＋＋').replace('■', '＋＋')

def removeDuplicatedHeader(data):
    # The title is always at least partially duplicated
    # Sometimes the subtitle contains a prefixed semicolon.
    # Remove the title and use the subtitle without a semicolon
    data = data.lstrip()
    data = data[data.find('\n'):]
    data = data.lstrip()
    data = data.lstrip(';')

    # The second title may or may not be prefixed with a circle
    if not data.startswith('＋＋'):
        data = '＋＋' + data

    return data

def handleInternalDialog(data):
    # If '(' starts a new section, don't touch it
    # but if it follows text, assume its a soft dialog
    # (person's unspoken thoughts?)
    data = data.replace('\n\n（', '@')
    data = data.replace("\n（", ":（")
    data = data.replace('@', '\n\n（')

    return data

def formatChoices(data):
    # Properly format choices
    # Only the best choice to select is selected
    # We have to manually find the other choice
    # which will have the same level of indentation
    # but can appear on the line before or after
    CHOICE_CHAR = '○'
    start = 0
    while True:
        start = data.find('＞', start)
        if start == -1:
            break

        lineStart = data.rfind('\n', 0, start)
        prefix = data[lineStart:start] + '　' # ideographic space

        prevLineStart = data.rfind('\n', 0, lineStart)
        nextLineStart = data.find('\n', start + 1)
        if prefix in data[prevLineStart:lineStart]:
            choiceA = data[prevLineStart:lineStart]
            choiceB = data[lineStart:nextLineStart]
            newStart = prevLineStart
            newEnd = nextLineStart
        else:
            nextLineEnd = data.find('\n', nextLineStart + 1)
            choiceA = data[lineStart:nextLineStart]
            newStart = lineStart
            if prefix in data[nextLineStart:nextLineEnd]:
                choiceB = data[nextLineStart:nextLineEnd]
                newEnd = nextLineEnd
            else:
                choiceB = None
                newEnd = nextLineStart

        firstHalf = f"{CHOICE_CHAR}{choiceA.strip()}"
        secondHalf = ""
        if choiceB:
            secondHalf = f"\n{CHOICE_CHAR}{choiceB.strip()}"
        newSegment = f"\n\n{firstHalf}{secondHalf}\n\n"
        data = data[:newStart] + newSegment + data[newEnd:]

        start = newEnd + len(newSegment)
    return data

def replaceNonSpeechQuotes(data):
    # Replace the quotes in locations with an alternative annotation
    # Quotes will only be used for speech
    for searchStr in ['ATE', '○']:
        start = 0
        while True:
            start = data.find(searchStr, start)
            if start == -1:
                break
            end = data.find('\n', start)

            subdata = data[start:end]
            subdata = subdata.replace('「', '{').replace('」', '}')
            data = data[:start] + subdata + data[end:]

            start = start + 1

    return data

def addOpeningQuoteMark(data):
    # Put a '「' on the preceding line if there isn't a '「' there already
    start = 0
    while True:
        start = data.find('「', start)
        if start == -1:
            break
        prevStart = data.rfind('\n', 0, start - 1) + 1

        isPerson = data[prevStart:start - 1].find('「') == -1

        if isPerson:
            insertData = ':「'
        else:
            insertData = '\n:「'
        data = data[:start - 1] + insertData + data[start + 1:]
        start += len(insertData) + 2

    return data

def addClosingQuoteMark(data):
    # Find each line that contains '「' and add a final '」' if there is not already one
    for startToken, endToken in [['「', '」'], ['（','）']]:
        start = 0
        while True:
            start = data.find(':' + startToken, start)
            if start == -1:
                break
            end = data.find('\n', start)

            if data[end - 1] != endToken:
                data = data[:end] + endToken + data[end:]
            start = start + 1

    return data

def insertColonBeforeQuotes(data):
    # Find '「' that don't have a preceding ':' and give them one
    start = 0
    while True:
        start = data.find('「', start)
        if start == -1:
            break

        if data[start - 1] != ':':
            data = data[:start] + ':' + data[start:]

        start = start + 1

    return data
