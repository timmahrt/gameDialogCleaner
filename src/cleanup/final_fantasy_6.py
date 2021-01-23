
import io
import os

import utils

def clean(root, outputPath):
    '''

    Post-clean up thoughts
    -- had I parsed the page as a table, rather than do a text dump,
       the process would have been simpler. I had to manually
       pre-process the last page (credits). Otherwise, some pages have
       a table with 2 columns and others have 3 columns.
    '''

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    for fn, fd in utils.loadFiles(root):
        data = fd.read()

        data = data.lstrip()
        pageTitle, data = data.split('\n', 1)
        dataList = data.split('セリフ＆ナレーション')
        if len(dataList) != 2:
            continue
        data = dataList[1]
        data = data.split('Back  Next')[0].strip()
        data = data.replace('\n  ', '  ')

        step = 2
        if data.count('\n　\n') > 5:
            step = 3

        outputRows = [f': ＋＋{pageTitle}']
        dataList = data.split("\n")
        for i in range(0, len(dataList) - step + 1, step):
            speaker = dataList[i]
            text = dataList[i+step-1]
            outputRows.append("%s:「%s」" % (speaker, text))

        data = "\n".join(outputRows) + "\n"

        data = utils.removeQuoteMarksFromSpeech(data)
        data = utils.simplifyLongNewlineSequences(data)
        data = utils.addSpaceAfterChoiceMarker(data)
        data = utils.removeReundantSpeakers(data)
        data = utils.addLeadingWhitespaceWhenSameSpeaker(data, True)

        with io.open(os.path.join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write(data)
