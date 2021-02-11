import io
import os
from os.path import join
import re

import utils

yearRe = re.compile("[0-9]{3,}")


def clean(rootFileName, outputPath):
    """


    Chrono triggers data is split by each location so
    it is processed a little different.  Each section
    is processed.  To avoid too much file fragmentation,
    if two physical locations occur in the same time
    period, they are merged into the same file.
    """
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    sections = getSegmentsForRootFile(rootFileName)
    sections = cleanSectionScript(sections)
    sections = mergeSectionsByYear(sections)

    for i, section in enumerate(sections):
        outputFn = getFileNameFromSection(i + 1, section)
        with io.open(join(outputPath, outputFn), "w", encoding="utf-8") as fd:
            fd.write(section)


def cleanSectionScript(sections):
    cleanedSections = []
    for section in sections:
        section = simpleCondenseLines(section)
        section = markChoices(section)
        section = condenseLines(section)
        section = isolateChoices(section)
        section = separateSpeakersAndSpeech(section)
        section = section.replace("　", "")  # Scrub whitespace
        section = section.replace("[END]", "")
        section = section.replace(":\n:", ":")  # Happens sometimes
        section = section.replace("「", "")  # No longer needed
        section = section.replace("\n [", "\n[")
        section = fixDialogueSpacing(section)
        section = utils.simplifyLongNewlineSequences(section)
        section = utils.removeReundantSpeakers(section)
        section = utils.addSpaceAfterChoiceMarker(section)
        section = utils.addLeadingWhitespaceWhenSameSpeaker(section, False)
        cleanedSections.append(section)

    return cleanedSections


def simplifyWhitespace(section):
    newlineRe = re.compile("\n{3,}")
    return newlineRe.sub("\n\n", section)


def getYear(section):
    firstLine = section.split("\n", 1)[0]
    match = yearRe.search(firstLine)
    if match is None:
        return firstLine
    else:
        return match.group(0)


def simpleCondenseLines(section):
    choiceStartRe = re.compile(r"\n[^「 　\n\[]\S[^\n「]+\n[^ 　\n]")

    start = 0
    while True:
        match = choiceStartRe.search(section, start)
        if not match:
            break

        start = match.start()
        newlineToDeleteI = section.find("\n", start + 1)
        section = section[:newlineToDeleteI] + section[newlineToDeleteI + 1 :]

    return section


def condenseLines(section):
    END_MARKER = "END"
    start = 0
    while True:
        i = section.find(END_MARKER, start)
        if i == -1:
            break

        # Move backwards, eating as many newlines as possible
        while True:
            prevEnd = section.rfind("\n", 0, i)
            if prevEnd == -1:
                break

            # The 'END' marker applies to a speech quote in the existing context
            if "「" in section[prevEnd:i]:
                break
            prevStart = section.rfind("\n", 0, prevEnd)
            if prevStart == -1:
                break

            prevLine = section[prevStart:prevEnd]

            if END_MARKER not in prevLine:
                section = section[:prevEnd] + section[prevEnd + 1 :]
                i -= 1

            if "[" in prevLine or "「" in prevLine:
                break

        start = i + 1

    return section


def separateSpeakersAndSpeech(section):
    lines = section.split("\n")
    retSection = [lines.pop(0)]
    notWhitespaceRe = re.compile(r"^\D")
    for line in lines:
        if len(line) > 0:
            if line.startswith(" ["):
                line = line.lstrip(" [")
                line = line.replace("]", ":", 1)
            elif "「" in line:
                line = line.replace("「", ":「")
            elif notWhitespaceRe.search(line) is not None:
                line = f":{line}"
        retSection.append(line)

    return "\n".join(retSection)


def markChoices(section):
    choiceMarker = "○"
    choiceStartRe = re.compile(r"\n[^「 　\n][^「]+\n　{2,3}\S")
    start = 0
    while True:
        match = choiceStartRe.search(section, start)
        if match is None:
            break
        start = match.start()
        end = section.find("\n\n", start)

        i = 0
        while True:
            i = section.find("　　　", start, end)
            if i == -1:
                i = section.find("　　", start, end)
                if i == -1:
                    break
                else:
                    i = i + 2
            else:
                i = i + 3
            section = section[:i] + choiceMarker + section[i:]
            start = i

        start = end
        if start == -1:
            break

    # Kindof a hack
    section = section.replace("　　はい[END]", "　　○はい[END]")
    section = section.replace("　　はい\n", "　　○はい\n")
    section = section.replace("　　いいえ[END]", "　　○いいえ[END]")
    section = section.replace("　　いいえ\n", "　　○いいえ\n")

    return section


def isolateChoices(section):
    choiceMarker = "○"
    section = section.replace(choiceMarker, "\n" + choiceMarker)
    return section


def mergeSectionsByYear(sections):
    # Merge sections by year
    sectionMarker = "＋＋"
    prevSection = sectionMarker + sections.pop(0)
    prevYear = getYear(prevSection)
    newSections = [prevSection]
    for section in sections:
        section = sectionMarker + section

        currentYear = getYear(section)

        if prevYear == currentYear:
            newSections[-1] += "\n\n" + section
        else:
            newSections.append(section)
            prevYear = currentYear

    return newSections


def getFileNameFromSection(i, section):
    firstLine = section.split("\n", 1)[0].strip()
    firstLine = firstLine.replace(" ", "_")
    for char in [".", ",", "'", "＋", "[", "]", "(", ")", "?", "/", ":"]:
        firstLine = firstLine.replace(char, "")
    firstLine = firstLine.strip()

    outputFn = "%03d_%s.txt" % (i, firstLine)

    return outputFn


def getSegmentsForRootFile(rootFileName):
    sectionRe = re.compile(
        r" \[[a-zA-Z0-9 ,.()/']+([0-9]{3,}|\?)[a-zA-Z ,.()]+\]|\[End of Time\]|\[Ending.*\]"
    )

    sections = []
    with io.open(rootFileName, "r", encoding="utf-8") as fd:
        data = fd.read()
        start = 0

        while True:
            match = sectionRe.search(data, start)
            if match is None:
                sections.append(data[start:-1])
                break

            end = match.start()
            if start != 0:
                sections.append(data[start:end].strip())

            start = end + 1

    return sections


def fixDialogueSpacing(section):
    whitespaceRe = re.compile("\n\n(?!\n)")
    section = whitespaceRe.sub("\n", section)
    section = section.replace("\n[", "\n\n[")
    return section
