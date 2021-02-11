
import os
import shutil
import io
import re

def getOutputPath(root, outputDirName):
    outputPath = os.path.join(root, outputDirName)
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)
    return outputPath


def loadFiles(root):
    fnList = os.listdir(root)
    fnList.sort()
    for fn in fnList:
        if ".txt" not in fn:
            continue
        with io.open(os.path.join(root, fn), "r", encoding="utf-8") as fd:
            yield fn, fd


def addLeadingWhitespaceWhenSameSpeaker(outputData, useIdeographicSpace):
    """
    useIdeographicSpace: false if names are in latin script; true otherwise
    """
    space = "　" if useIdeographicSpace else " "
    # Pad line with whitespace when speaker doesn't change
    start = 0
    while True:
        stop = outputData.find("\n:", start)
        if stop == -1:
            break
        lineStart = outputData.rfind("\n", start, stop)
        if lineStart == -1:
            break
        newlineI = outputData.find(":", lineStart, stop)
        if newlineI == -1:
            break
        if outputData[newlineI - 1] != "\n":
            newlineIStart = outputData.rfind("\n", start, newlineI)
            spaceBufferLength = newlineI - newlineIStart - 1
            spaceBuffer = space * spaceBufferLength  # Reinserting ideographic spaces XD
            outputData = outputData[: stop + 1] + spaceBuffer + outputData[stop + 1 :]

        start = stop

    return outputData


def addSpaceAfterChoiceMarker(section):
    eventMarker = re.compile("○(?!　| )")

    return eventMarker.sub("○　", section)


def is_cjk(character):
    """
    Borrowed from the nltk

    https://github.com/alvations/nltk/blob/79eed6ddea0d0a2c212c1060b477fc268fec4d4b/nltk/tokenize/util.py
    """
    return any(
        [
            start <= ord(character) <= end
            for start, end in [
                (4352, 4607),
                (11904, 42191),
                (43072, 43135),
                (44032, 55215),
                (63744, 64255),
                (65072, 65103),
                (65381, 65500),
                (131072, 196607),
            ]
        ]
    )


def lineIsPercentCjk(line, percent):
    numCjk = sum([1 for char in line if is_cjk(char)])
    return (numCjk / float(len(line))) > percent


def simplifyLongNewlineSequences(section):
    """Long sequences of new lines get homogenized to \n\n"""
    newlineRe = re.compile("\n{3,}")
    return newlineRe.sub("\n\n", section)


def removeReundantSpeakers(section):
    retLines = []
    prevSpeaker = None
    for line in section.split("\n"):
        if ":" not in line:
            prevSpeaker = None
            retLines.append(line)
            continue

        currentSpeaker = line.split(":", 1)[0]
        if prevSpeaker in (currentSpeaker, f"[{currentSpeaker}]"):
            line = line.replace(currentSpeaker + ":", ":")

        retLines.append(line)
        prevSpeaker = currentSpeaker

    return "\n".join(retLines)


def renameFilesWithLeadingNumbers(inputPath, outputPath):
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    fileList = [fn for fn in os.listdir(inputPath) if ".txt" in fn]
    fileList.sort()

    for i, fn in enumerate(fileList):
        partialFn = fn.split("_", 1)[1]
        newFn = "%03d_%s" % (i + 1, partialFn)
        shutil.copy(os.path.join(inputPath, fn), os.path.join(outputPath, newFn))


def removeQuoteMarksFromSpeech(section):
    openQuoteRe = re.compile(":「")
    section = openQuoteRe.sub(":", section)

    closeQuoteRe = re.compile("」$", flags=re.MULTILINE)
    section = closeQuoteRe.sub("", section)

    return section
