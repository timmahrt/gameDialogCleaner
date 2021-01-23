
import io
import os
import re

import utils

def clean(root, outputPath):
    '''
    A little bit involved but with a bit of planning, it wasn't too difficult.
    Fortunately, three games all used the same formatting, so this function
    yielded a lot of text.
    '''
    END_OF_HEADER = 'TIMESTAMPS'
    nameRe = re.compile("\n{2,}.*?\n[（「１]")

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    for fn, fd in utils.loadFiles(root):
        data = fd.read()

        start = data.find(END_OF_HEADER) + len(END_OF_HEADER) + 1
        data = data[start:].lstrip()

        # Remove lines containing an arrow in them
        data = removeLinesContaining(data, '→')

        start = nameRe.search(data).start()
        preamble = getPreamble(data[:start])
        data = data[start:]

        data = removeFooter(data)

        # Protect events by making them look like speech
        data = data.replace('\n・', 'イベント\n「・')
        data = data.replace('\n\n１．', '\n\n選択\n「１．')

        epilogue = getEpilogue(data)
        outputList = [preamble, ] + splitDataBySpeechEvent(data)
        outputList.append(epilogue)
        outputData = "\n".join(outputList) + '\n'
        outputData = outputData.replace('　', '') # Remove ideographic space

        outputData = setSpeakerBeforeDecisions(outputData)

        # Clean up the earlier protected 'events'
        outputData = removePlaceholderSpeech(outputData, 'イベント:「・', '\n:・')
        outputData = removePlaceholderSpeech(outputData, '選択:「１．', '\n:１．')

        outputData = reduceWhitespaceBeforeNumbers(outputData)
        outputData = addColonBeforeDecisions(outputData)
        outputData = replaceSpecialCharacters(outputData)

        outputData = utils.removeQuoteMarksFromSpeech(outputData)
        outputData = utils.simplifyLongNewlineSequences(outputData)
        outputData = utils.addLeadingWhitespaceWhenSameSpeaker(outputData, True)
        outputData = utils.addSpaceAfterChoiceMarker(outputData)

        with io.open(os.path.join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write(outputData)


def replaceSpecialCharacters(outputData):
    numberRe = re.compile(":[１２３４５６７８９]．")
    outputData = numberRe.sub(':○', outputData)

    locationRe = re.compile("^・", flags=re.MULTILINE)
    outputData = locationRe.sub("＋＋", outputData)

    locationRe2 = re.compile("^:・", flags=re.MULTILINE)
    outputData = locationRe2.sub(":＋＋", outputData)

    return outputData

def removeFooter(data):
    # Remove page footer
    for text in ['?ﾔ戻る', '?ﾕシナリオ一覧']:
        i = data.rfind(text)
        if i != -1:
            data = data[:i]

    return data

def getPreamble(data):
    # Extract the chapter name and the subchapter location
    newlineRe = re.compile("\n{3,}")
    preamble = data
    preamble = newlineRe.sub('\n\n', preamble)
    preambleEnd = preamble.find('\n') + 1
    preambleEnd = preamble.find('\n', preambleEnd) + 1
    if preamble[preambleEnd + 1] != '・':
        preamble = preamble[:preambleEnd] + '・' + preamble[preambleEnd:]
    preambleEnd = preamble.find('\n', preambleEnd) + 1
    preamble = preamble[:preambleEnd]

    return preamble

def getEpilogue(data):
    # Isolate the epilogue (if there is one)
    epilogueStart = data.rfind('「')
    epilogueStart = data.find('\n\n\n', epilogueStart)
    epilogue = ''
    if epilogueStart != -1:
        epilogue = '\n\n' + data[epilogueStart:].strip()
        data = data[:epilogueStart]

    return epilogue

def splitDataBySpeechEvent(data):
    numberRe = re.compile("\n{1,}[１２３４５６７８９]")
    nameRe = re.compile("\n{2,}.*?\n[（「１]")
    outputList = []
    while True:
        nameStop = data.find('「')
        nameStopAlt = data.find('（')
        if nameStop == -1 and nameStopAlt == -1:
            break
        elif nameStop != -1 and nameStopAlt != -1:
            nameStop = min([nameStop, nameStopAlt])
        elif nameStop == -1:
            nameStop = nameStopAlt

        # all names contain a leading sequence of at least two new lines
        # trim those, and consider the rest to be meaningful
        # (ie a pause between speech events)
        name = data[:nameStop]
        name = name.replace('\n\n', '', 1)
        data = data[nameStop:]

        # Look for the next name.
        # All the text that appears before it is the current
        # speaker's speech
        # There is a special case when the current speaker is
        # the last in the script
        match = nameRe.search(data)
        if match:
            speechStop = match.start()
        else:
            speechStop = -1

        speech = data[:speechStop]

        # Numbers look like text but show choice-based events
        numbersText = ''
        match = numberRe.search(speech)
        if match:
            numbersIndex = match.start()
            numbersText = speech[numbersIndex:]
            speech = speech[:numbersIndex]

        # Format the speech which may contain several speech
        # events in one sequence by the same speaker
        speech = speech.replace('\n（', '\n:（')
        speech = speech.replace('\n「', '」\n:「')
        speech += '」'
        speech = speech.replace('\n', '')
        speech = speech.replace(':「', '\n:「')
        speech = speech.replace('）」', '）') # Kindof gross, probably wrong

        outputList.append("%s:%s" % (name.rstrip(), speech.strip()))

        if numbersText:
            i = numbersText.find('\n「')
            if i != -1:
                speechStop -= len(numbersText) - i
                numbersText = numbersText[:i]

            outputList.append(numbersText)


        data = data[speechStop:]

    return outputList


def setSpeakerBeforeDecisions(outputData):
    # If a name appears on the line before a number, the speaker is
    # giving a selection of options for the user to choose and should
    # be set as the speaker
    oneRe = re.compile("\n{1,}１")
    start = 0
    while True:
        match = oneRe.search(outputData, start)
        if match == None:
            break
        start = match.start()
        if outputData[start - 1] != '\n':
            prevLineStart = outputData.rfind('\n', 0, start)
            segment = outputData[prevLineStart:start]
            if ':' not in segment and '・' not in segment: # The previous line contains no speech?
                outputData = outputData[:start] + ':' + outputData[start + 1:]
        start += 2
    return outputData

def reduceWhitespaceBeforeNumbers(outputData):
    # Some numbered choices have too much whitespace
    newlinesAndNumbersRe = re.compile("\n\n[１２３４５６７８９]．")
    start = 0
    while True:
        match = newlinesAndNumbersRe.search(outputData, start)
        if match == None:
            break
        start = match.start()

        outputData = outputData[:start] + outputData[start + 1:]
        start = start - 1

    return outputData

def addColonBeforeDecisions(outputData):
    newlineAndNumbersRe = re.compile("\n[１２３４５６７８９]")
    start = 0
    while True:
        match = newlineAndNumbersRe.search(outputData, start)
        if match == None:
            break
        start = match.start()

        if outputData[start + 1] != ':':
            outputData = outputData[:start + 1] + ":" + outputData[start + 1:]

    return outputData

def removeLinesContaining(data, matchChar):
    start = 0
    while True:
        stop = data.find(matchChar, start)
        if stop == -1:
            break
        start = data.rfind('\n', start, stop)
        stop = data.find('\n', start + 1)
        data = data[:start] + data[stop:]

    return data

def removePlaceholderSpeech(outputData, eventPlaceholder, replacement):
    start = 0

    while True:
        start = outputData.find(eventPlaceholder, start)
        if start == -1:
            break
        end = outputData.find('」', start)
        outputData = outputData[:end] + '\n' + outputData[end + 1:]
        start = end
    outputData = outputData.replace(eventPlaceholder, replacement)

    return outputData
