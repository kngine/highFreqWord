import requests
import lxml
import re
import nltk
import os
from bs4 import BeautifulSoup
from nltk.corpus import PlaintextCorpusReader

# import stopwords

# config
rootUrl = "https://www.nytimes.com/"
nWords = 5000
limitRuns = 500


# temp vaiables
allUrls = []
iRun = 0


def getTranslation(word):
    url = 'http://dict.youdao.com/w/{}/'.format(word)
    # response = urllib.request.urlopen(url)
    # html = response.read()
    data = requests.get(url).content
    soup = BeautifulSoup(data, 'html.parser')
    container = soup.find(class_='trans-container')

    if not container:
        return 0

    li = container.find_all('li')
    data = [li.text.strip() for li in li]
    return data



def getWords(url, file):
    minLen = 4
    if url[-5:] != ".html":
        return
    if url[:4] != "http":
        url = rootUrl + url

    print("processing link " + url + " ...")

    data = requests.get(url).content
    soup = BeautifulSoup(data,'lxml')
    text = str(soup).replace('\n','').replace('\r','')
    # replace <script> tag
    text = re.sub(r'\<script.*?\>.*?\</script\>',' ',text)
    # replace HTML tag
    text = re.sub(r'\<.*?\>'," ",text)
    text = re.sub(r'[^a-zA-Z]',' ',text)
    text = text.lower().split()
    text = [i for i in text if len(i) > minLen]
    text = ' '.join(text)

    file.write(text+' ')
    print("process one link done\n")


def getLinks(url):
    global iRun
    iRun += 1
    if iRun > limitRuns:
        return

    try:
        host = url.split('/')
        data = requests.get(url).text
        soup = BeautifulSoup(data,'lxml')
        for link in soup.find_all('a'):
            if link.get('href') not in allUrls and link.get('href') is not None:
                if link.get('href').startswith('http'):
                    if link.get('href').split('/')[2] == host[2]:
                        newpage = link.get('href')
                        allUrls.append(newpage)
                        getLinks(newpage)
                elif link.get('href').startswith('/'):
                    newpage = link.get('href')
                    newpage = 'http://'+host[2]+newpage
                    allUrls.append(newpage)
                    getLinks(newpage)
    except Exception as e:
        print(e)


def getHighFreqWords():
    maxlen = 15
    maxlen1 = 5

    corpath = ''
    wordlist = PlaintextCorpusReader(corpath,'.*')
    allwords = nltk.Text(wordlist.words('temp.txt'))
    stop = []
    swords = [i for i in allwords if  i not in stop]
    fdist = nltk.FreqDist(swords)

    with open('highFreqWords.txt','w',encoding='utf-8') as file:
        for item in fdist.most_common(nWords):
            # print(item,item[0])
            word0 = item[0]
            try:
                q = getTranslation(item[0])
            except Exception as e:
                print(e)

            if not q:
                continue
            while len(word0) < maxlen:
                word0 += ' '
            num = str(item[1])
            while len(num) < maxlen1:
                num = ' ' + num
            file.write(word0 + ' ' + num + '  ')
            for translate in q:
                file.write(translate + ' ')
            file.write("\n")


if __name__ == '__main__':
    if os.path.isfile("temp.txt"):
        os.remove("temp.txt")
    print("root url is "+rootUrl + "\n")

    # step 1
    print("getting links...")
    getLinks(rootUrl)

    # step 2
    print("start processing " + str(len(allUrls)) + " urls ...\n")
    with open("temp.txt",'a+',encoding='utf-8') as file:
        for url in allUrls:
            try:
                getWords(url, file)
            except Exception as e:
                print(e)

    # step 3
    print("getting high frequency words...")
    getHighFreqWords()