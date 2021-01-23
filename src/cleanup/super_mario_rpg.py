import io
import os
from os.path import join
import re

import utils

def clean(sourceFolder, outputFolder):

    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)

    for fn, fd in utils.loadFiles(sourceFolder):
        section = fd.read()

        section = condenseWhitespace(section)
        section = removeNewlinesInContinuousSpeech(section)
        section = markEvents(section)
        section = separateSpeakersAndSpeech(section)

        section = section.replace('　', '')
        section = section.strip()

        section = utils.simplifyLongNewlineSequences(section)
        section = utils.addSpaceAfterChoiceMarker(section)
        section = utils.addLeadingWhitespaceWhenSameSpeaker(section, False)

        with io.open(join(outputFolder, fn), 'w', encoding='utf-8') as writeFd:
            writeFd.write(section)

def removeAsciiFromText(inputFn, outputFn):

    with io.open(outputFn, "w", encoding="utf-8") as outputFd:
        with io.open(inputFn, "r", encoding="utf-8") as inputFd:
            for line in inputFd:
                if not utils.lineIsPercentCjk(line, 0.2):
                    line = "\n"
                outputFd.write(line)

def condenseWhitespace(section):
    contentfullLinesRe = re.compile(r'\S\n\S')

    start = 0
    while True:
        match = contentfullLinesRe.search(section, start)
        if not match:
            break
        start = match.start()
        section = section[:start + 1] + section[start + 2:]

    return section

def removeNewlinesInContinuousSpeech(section):
    contentfullLinesRe = re.compile(r'\S\n\n\S')
    start = 0
    while True:
        match = contentfullLinesRe.search(section, start)
        if not match:
            break
        start = match.start()
        section = section[:start + 1] + section[start + 2:]

    return section



def separateSpeakersAndSpeech(section):
    lines = section.split("\n")
    retSection = [lines.pop(0)]
    notWhitespaceRe = re.compile(r"^\D")
    for line in lines:
        if len(line) > 0:
            if line.startswith('《'):
                line = line.strip('《')
                line = line.replace('》', ':', 1)
            elif notWhitespaceRe.search(line) is not None:
                line = f":{line}"
        retSection.append(line)

    return "\n".join(retSection)


def markEvents(section):
    # Mark when receiving items
    start = 0
    while True:
        start = section.find('もらった\n', start)
        if start == -1:
            break

        replI = section.rfind('\n', 0, start) + 1
        section = section[:replI] + '□' + section[replI:]
        start += 2

    # Mark decisions
    parenthesesRe = re.compile("\n　+（")
    section = parenthesesRe.sub('\n　○（', section)

    # Remove parentheses around decisions
    start = 0
    while True:
        start = section.find('○（', start)
        if start == -1:
            break
        end = section.find('）', start)
        section = section[:start + 1] + section[start + 2:end] + section[end + 1:]

    return section


def splitFile(sourceFile, outputFolder):
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)

    with io.open(sourceFile, "r", encoding="utf-8") as fd:
        data = fd.read()

    splits = [
        ['koopas_castle', 'こうじゃい！'],
        ['marios_house', 'ボクは、先に行ってますね。'],
        ['mushroom_castle', 'しっかり、みはります。'],
        ['thiefs_road', 'だよ。'],
        ['mushroom_castle_with_mallow', 'これで　おじいちゃんもよろこんでくれます！'],
        ['kinokero_waterway', 'ばいばい！'],
        ['kerokero_lake', 'さぁ、すぐそこが　ローズタウンですよ。'],
        ['rosetown', 'フラフラしながら　森の方へいったわよ。'],
        ['flower_girl_forest', '《トイドー》　ジーノ、ガンバレ～'],
        ['yostar_island', '《ワッシー》　（また　かけっこしような！）'],
        ['dukati', '気がするんだヨ‥‥‥。'],
        ['dukati_after_mines', 'では、どれにいたしましょう？'],
        ['bookie_tower', '‥‥‥ような気がした‥‥‥'],
        ['merry_marry', 'いいカゲンに　しろ！'],
        ['mushroom_castle', 'いつになったら　ふってくるのだ‥？'],
        ['falling_stars_hill', 'いいなぁ、キャンブルざんまい‥‥‥'],
        ['ripple_town', 'だれも帰ってこなかったなぁ‥‥‥'],
        ['sunkenship', 'がんばってください。\n\n\n\nまたどうぞ。'],
        ['countryroad', 'じゃあ　おさきに　しっけいするよ。'],
        ['monstown', 'マシュマロ国　道路課'],
        ['marshmallow_country', '《プランター》　まんぞく、まんぞく。'],
        ['barrel_volcano', 'カリバーの　メノ・バリアーが　消えた！！'],
        ['factory', 'スターロードの　復活だ！']
    ]
    for i, row in enumerate(splits):
        outputName, line = row
        splitI = data.index(line) + len(line)
        head = data[:splitI]
        data = data[splitI:]

        outputFn = "%02d_%s.txt" % (i + 1, outputName)
        with io.open(join(outputFolder, outputFn), "w", encoding="utf-8") as fd:
            fd.write(head)
