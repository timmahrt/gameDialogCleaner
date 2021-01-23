
import os
import io

import utils

from bs4 import BeautifulSoup

NON_FINAL_PUNCTUATION = '、〜'
SENTENCE_FINAL_PUNCTUATION = '…。！？・'

def extractDialog(rootDir):

    outputDir = utils.getOutputPath(rootDir, 'dialog')

    for fn, fd in utils.loadFiles(rootDir):
        sentenceList = []
        for line in fd:
            if ':「' not in line:
                continue
            line = line.split(':「')[1].rstrip().rstrip('」')

            for punctuation in NON_FINAL_PUNCTUATION:
                line = line.replace(punctuation, '')

            tmpSentenceList = [line]
            for punctuation in SENTENCE_FINAL_PUNCTUATION:
                subTmpSentenceList = []
                for sentence in tmpSentenceList:
                    subTmpSentenceList.extend(sentence.split(punctuation))
                tmpSentenceList = [line.strip() for line in subTmpSentenceList if line != '']
            sentenceList.extend(tmpSentenceList)

        with io.open(os.path.join(outputDir, fn), "w", encoding="utf-8") as fd:
            for line in sentenceList:
                fd.write(line + '\n')

class PageBuilder:

    SPEAKER_A = 'speaker_a'
    SPEAKER_B = 'speaker_b'
    CONTEXT = 'context'
    CHOICE = 'choice'

    def buildSection(self, textList, sectionId):
        rowList = []
        speakerClass = PageBuilder.CONTEXT
        for speechId, line in enumerate(textList):
            if ':' in line:
                speaker, line = line.split(':', 1)
                speaker = speaker.strip()
                # line = line.lstrip('「').rstrip('」')
            else:
                speaker = ''

            if self.isContext(line):
                speakerClass = PageBuilder.CONTEXT
            elif self.isChoice(line):
                speakerClass = PageBuilder.CHOICE
            elif speakerClass in [PageBuilder.CONTEXT, PageBuilder.CHOICE]:
                speakerClass = PageBuilder.SPEAKER_A
            elif speaker != '':
                if speakerClass == PageBuilder.SPEAKER_A:
                    speakerClass = PageBuilder.SPEAKER_B
                else:
                    speakerClass = PageBuilder.SPEAKER_A

            rowId = 'row_%03d_%02d' % (sectionId, speechId)
            rowList.append(self._makeRow(speakerClass, speaker, line, rowId))

        rowsText = "".join(rowList)

        return self._makeSection(rowsText)

    def isContext(self, line):
        return '＋＋' in line

    def isChoice(self, line):
        return line.startswith('○')

    def makeDocument(self, body):
        return f"""
<!doctype HTML>
<html lang='ja-jp' />
    <head>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="../game_scripts.css">
    </head>
    <body>
        <div class='main_content'>
            {body}
        <div>
    </body>
</html>
"""

    def _makeSection(self, sectionContent):
        return f"""
        <table class='script_section'>
            {sectionContent}
        </table>"""

    def _makeRow(self, rowClass, speaker, sourceText, rowId):
        return f"""
            <tr class='script_section_row {rowClass}'>
                <td class='script_section_row_speaker dialog_cell' id='{rowId}_speaker'>
                    {speaker}
                </td>
                <td class='script_section_row_source dialog_cell notranslate' id='{rowId}_source'>
                    {sourceText}
                </td>
                <td class='script_section_row_translation dialog_cell' id='{rowId}_translation'>
                    {sourceText}
                </td>
            </tr>"""

def isWrapped(line, left, right):
    return line[0] == left and line[-1] == right

def extractDialogAsHtml(rootDir, outputDir, builder, tocTitle, getTitleFromFile=None):
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    sectionNum = 0
    for fn, fd in utils.loadFiles(rootDir):
        sections = []
        currentSection = []
        for line in fd:
            line = line.strip()
            if line == '':
                sections.append(builder.buildSection(currentSection, sectionNum))
                sectionNum += 1
                currentSection = []
            else:
                currentSection.append(line)

        sections.append(builder.buildSection(currentSection, sectionNum))

        sectionsText = "\n\n".join(sections)
        html = builder.makeDocument(sectionsText)

        outputFn = os.path.splitext(fn)[0] + ".html"
        with io.open(os.path.join(outputDir, outputFn), "w", encoding="utf-8") as fd:
            fd.write(html)

    generateDirectoryListing(outputDir, tocTitle, getTitleFromFile)

def getNameFromFirstLine(fn):
    line = None
    print(fn)
    with io.open(fn, 'r', encoding='utf-8') as fd:
        soup = BeautifulSoup(fd.read(), 'lxml')
        table = soup.find('table')
        line = table.find_all('td')[1].text
        line = line.strip()
        line = line.strip('＋')
        line = line.strip('○')
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.strip()

    return line


def getNumSpeechEvents(fn):
    with io.open(fn, "r", encoding="utf-8") as fd:
        html = fd.read()
        return html.count('speaker_a') + html.count('speaker_b')


def generateDirectoryListing(rootDir, tocTitle, getTitleFromFile=None):
    dirList = [fn for fn in os.listdir(rootDir) if '.html' in fn and fn != 'index.html']
    dirList.sort()

    makeRow = lambda url, urlText, length: f"<div class='link_row'><div class='script_length_info'>{length}</div><div class='script_link'><a href='{url}'>{urlText}</a></div></div>"
    pageTitle = f"<div class='title'> {tocTitle}</div>"
    homeLink = "<div class='section'><div class= 'link_row link_home'><a href='..'>Return home</></div></div>"

    linklessRowTemplate = "<div class='link_row'><div class='script_length_info'>%s</div><div class='script_link'>%s</div></div>"
    tableHeader = linklessRowTemplate % ('# lines', '')
    rowList = [pageTitle, tableHeader]
    totalNumSpeechEvents = 0
    for i, fn in enumerate(dirList):
        if getTitleFromFile:
            suffix = getTitleFromFile(os.path.join(rootDir, fn))
            pageText = f"{i + 1} - {suffix}"
        else:
            pageText = f"Page {i + 1}"
        numSpeechEvents = getNumSpeechEvents(os.path.join(rootDir, fn))
        totalNumSpeechEvents += numSpeechEvents

        rowList.append(makeRow(fn, pageText, numSpeechEvents))
    totalRow = linklessRowTemplate % (str(totalNumSpeechEvents), "Total")
    rowList.insert(2, totalRow)
    rowList.append(homeLink)

    allUrlText = "\n".join(rowList)

    builder = PageBuilder()
    html = builder.makeDocument(allUrlText)
    with io.open(os.path.join(rootDir, "index.html"), "w", encoding="utf-8") as fd:
        fd.write(html)


if __name__ == "__main__":

    # extractDialogAsHtml('data/super_mario_rpg/cleaned', 'data/super_mario_rpg/html', PageBuilder(), 'Super Mario RPG', getNameFromFirstLine)

    # extractDialogAsHtml('data/chrono_trigger/cleaned', 'data/chrono_trigger/html', PageBuilder(), 'Chrono Trigger', getNameFromFirstLine)

    # extractDialogAsHtml('data/ff6/cleaned', 'data/ff6/html', PageBuilder(), 'Final Fantasy 6', getNameFromFirstLine)
    # extractDialogAsHtml('data/ff7/cleaned', 'data/ff7/html', PageBuilder(), 'Final Fantasy 7', getNameFromFirstLine)
    # extractDialogAsHtml('data/ff8/cleaned', 'data/ff8/html', PageBuilder(), 'Final Fantasy 8', getNameFromFirstLine)
    extractDialogAsHtml('data/ff9/cleaned', 'data/ff9/html', PageBuilder(), 'Final Fantasy 9', getNameFromFirstLine)

    # extractDialogAsHtml('data/sf3s1/cleaned', 'data/sf3s1/html', PageBuilder(), 'Shining Force 3 (Scenario 1)', getNameFromFirstLine)
    # extractDialogAsHtml('data/sf3s2/cleaned', 'data/sf3s2/html', PageBuilder(), 'Shining Force 3 (Scenario 2)', getNameFromFirstLine)
    # extractDialogAsHtml('data/sf3s3/cleaned', 'data/sf3s3/html', PageBuilder(), 'Shining Force 3 (Scenario 3)', getNameFromFirstLine)
