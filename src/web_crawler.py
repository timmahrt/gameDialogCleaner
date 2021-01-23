
import os
import io
import urllib
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup

import pdb

def loadPage(url):
    f = urlopen(url)
    webpage = f.read()

    return BeautifulSoup(webpage, 'lxml') # 'html.parser'

def downloadRawHtml(url, outputFn):
    '''
    Pass as extractTextFunc to downlaod the raw html of a page
    '''
    r = requests.get(url)
    r.encoding = 'shift_jis'
    html = r.text
    for fromVal in ['Shift_JIS', 'shift_jis', 'x-sjis']:
        html = html.replace(f'charset={fromVal}', 'charset=utf-8')

    with io.open(outputFn, "w", encoding="utf-8") as writeFd:
        writeFd.write(html)

def downloadScriptOnPage(url, outputFn):
    '''
    Pass as extractTextFunc to extract the text of an html page

    This will pick up lots of garbage text that will need
    to be cleaned up later
    '''
    soup = loadPage(url)
    text = soup.get_text()

    with io.open(outputFn, "w", encoding="utf-8") as fd:
        fd.write(text)

def downloadScriptOnPageFromTable(url, outputFn):
    '''
    Pass as extractTextFunc to extract the text of the first table in an html page

    Scraping the table gets weird results with BeautifulSoup's
    'html parser' but 'lxml' works fine /shrug
    '''
    soup = loadPage(url)
    table = soup.find('table')
    rows = table.find_all('tr')

    outputRows = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) != 3:
            continue

        speaker, script, enScript = [ele.text.strip() for ele in cols]
        line = "%s:「%s」「%s」" % (speaker, script.replace('\n', ''), enScript.replace('\n', ' '))
        outputRows.append(line)

    with io.open(outputFn, "w", encoding="utf-8") as fd:
        fd.write("\n".join(outputRows) + "\n")

def saveUrl(i, urlTail, fullUrl, outputPath, extractTextFunc):
    pageTextOutputFn = "%03d_%s.html" % (i, os.path.splitext(urlTail)[0].replace('/', '_'))
    try:
        extractTextFunc(fullUrl, os.path.join(outputPath, pageTextOutputFn))
    except urllib.error.HTTPError:
        print("Failed to access page: '%s'" % fullUrl)

def getUrlsFromPage(url, href=None):
    soup = loadPage(url)
    if href is None:
        urls = [url.get('href') for url in soup.find_all('a')]
    else:
        urls = [url.get('href') for url in soup.find_all('a', href=True)]

    return urls

def crawlPageForUrls(url, outputPath, extractTextFunc=downloadScriptOnPage):
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    urlPrefix = url.rsplit('/', 1)[0]
    urls = getUrlsFromPage(url)
    for i, scriptUrl in enumerate(urls):
        try:
            urlTail = scriptUrl.rsplit('/', 1)[-1]
        except AttributeError:
            print('Bad url?: %s' % scriptUrl)
            continue
        fullUrl = "%s/%s" % (urlPrefix, urlTail)
        saveUrl(i, urlTail, fullUrl, outputPath, extractTextFunc)

def crawlPageForUrlsDontMangleUrls(url, outputPath, prefix, extractTextFunc=downloadScriptOnPage):
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    urls = getUrlsFromPage(url, True)
    for i, urlTail in enumerate(urls):
        fullUrl = prefix + urlTail
        saveUrl(i, urlTail, fullUrl, outputPath, extractTextFunc)

if __name__ == "__main__":

    dqRoot = 'http://nayukaaaaa.nomaki.jp/wp/dq.html'

    ff4Root = 'http://notserious.info/ff4/script/'
    ff5Root = 'http://yupotan.sppd.ne.jp/game/ff5/ff5serif.html'
    ff6Root = 'http://www2u.biglobe.ne.jp/~Figaro/menu/scenario/scenario-j-1.htm'
    ff7Root = 'http://ajatt.com/finalfantasy/ff7p-index.htm'
    ff8Root = 'http://aizenn.web.fc2.com/talk/ff-serifu.html'
    ff9Root = 'http://akanekono.web.fc2.com/ff9/ff9top.html'

    sf3s1Root = 'https://web.archive.org/web/20050120181126/http://homepage1.nifty.com/CHRIS/SF3/S-1/SF3Conversation.HTML'
    sf3s2Root = 'https://web.archive.org/web/20050120181229/http://homepage1.nifty.com/CHRIS/SF3/S-2/SF3Conversation2.HTML'
    sf3s3Root = 'https://web.archive.org/web/20041212175045/http://homepage1.nifty.com/CHRIS/SF3/S-3/SF3Conversation3.HTML'

    #crawlPageForUrlsDontMangleUrls(sf3s1Root, 'sf3s1_html', "https://web.archive.org/web/20050120181126/http://homepage1.nifty.com/CHRIS/SF3/S-1/", downloadRawHtml)
    #crawlPageForUrlsDontMangleUrls(sf3s2Root, 'sf3s2_html', "https://web.archive.org/web/20050120181126/http://homepage1.nifty.com/CHRIS/SF3/S-2/", downloadRawHtml)
    #crawlPageForUrlsDontMangleUrls(sf3s3Root, 'sf3s3_html', "https://web.archive.org/web/20050120181126/http://homepage1.nifty.com/CHRIS/SF3/S-3/", downloadRawHtml)

    #crawlPageForUrlsDontMangleUrls(dqRoot, 'dq', 'http://nayukaaaaa.nomaki.jp/wp/')

    # crawlPageForUrls(ff4Root, 'ff4', downloadScriptOnPageFromTable)
    # crawlPageForUrls(ff5Root, 'ff5')
    # crawlPageForUrls(ff6Root, 'ff6_html', downloadRawHtml)
    # crawlPageForUrls(ff7Root, 'ff7_html', downloadRawHtml)
    crawlPageForUrls(ff8Root, 'ff8_html', downloadRawHtml)
    # crawlPageForUrls(ff9Root, 'ff9_html', downloadRawHtml)
    #crawlPageForUrls(chronotriggerRoot, 'chronotriggerUrls.txt')
