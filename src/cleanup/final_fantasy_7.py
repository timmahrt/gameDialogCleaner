
import io
import os
import re

import utils

def clean(root, outputPath):
    '''

    Post-clean up thoughts
        This has a lot going on.  Changes in the scene are demarcated with < >.
        Keywords, sometimes the current speaker, and maybe narrations are decorated
        with 【 】
        A blank line represents a break in continuity or passage of time maybe?

        All dialog can be extracted by picking lines with ":" in them.
    '''

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    for fn, fd in utils.loadFiles(root):
        data = fd.read()

        data = data.lstrip()
        data = data[data.find('\n'):].strip()

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
        data = data.split('TO BE')[0]
        data = data.strip() + '\n'

        data = changeEventMarking(data)
        data = removeCharactersSurroundingSpeaker(data)

        data = utils.removeQuoteMarksFromSpeech(data)
        data = utils.simplifyLongNewlineSequences(data)
        data = utils.addSpaceAfterChoiceMarker(data)
        data = utils.addLeadingWhitespaceWhenSameSpeaker(data, True)

        with io.open(os.path.join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write(data)

def removeCharactersSurroundingSpeaker(data):
    openingBracketRe = re.compile("^【", flags=re.MULTILINE)
    data = openingBracketRe.sub('', data)

    closingBracketRe = re.compile("】:")
    data = closingBracketRe.sub(':', data)

    return data

def changeEventMarking(data):
    eventMarker = re.compile("^＜(?!選択肢)", flags=re.MULTILINE)
    data = eventMarker.sub("＋＋＜", data)

    eventMarker = re.compile("^＜(?=選択肢)", flags=re.MULTILINE)
    data = eventMarker.sub("○＜", data)
    data = data.replace("＜", "").replace("＞", "")
    data = splitEvents(data)

    data = '＋＋' + data # The first line is always the context for the current location

    return data

def splitEvents(data):
    outputData = ""
    for line in data.split('\n'):
        if not line.startswith("○"):
            outputData += line + '\n'
            continue

        if '→' not in line or '：' not in line:
            outputData += line.replace('選択肢：', '') + '\n'
            continue

        choices, correctChoice = line.split('：', 1)[1].split('→', 1)
        correctChoice = correctChoice.replace('を選択', '').strip()
        choices = choices.split('or')
        for choice in choices:
            choice = choice.strip()
            if choice == correctChoice:
                choice += '（OK）'
            outputData += f"○　{choice}\n"

    return outputData
