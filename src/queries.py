import pickle
import time
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.etree.ElementTree import parse

COAUTHORS_URL = "https://dblp.uni-trier.de/pers/xc/{}.xml"

def loadPickleDict(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)

def getCoauthors(author_name, author_urlpt, depth):
    authors = {}
    coauthors = []

    for i in range(0, 10):
        try:
            dblp_url = urlopen(COAUTHORS_URL.format(author_urlpt))
            break
        except HTTPError as ex:
            if i == 9:
                raise Exception("Failed to open xml document after 10 retries: {}".format(ex))
            else:
                time.sleep(1)

    coauthors_xml = parse(dblp_url)

    for author in coauthors_xml.getroot().iter('author'):
        name = author.text
        urlpt = author.get('urlpt')
        count = int(author.get('count'))

        coauthors.append((name, urlpt, count))

    authors[author_name] = coauthors

    if depth > 1:
        for coauthor in coauthors:
            authors.update(getCoauthors(coauthor[0], coauthor[1], depth-1))

    return authors

if __name__ == "__main__":
    dict_yu = getCoauthors("Philip S. Yu", "y/Yu:Philip_S=", 2)

    with open('dictionaries/dict_yu.pickle', 'wb') as yu:
        pickle.dump(dict_yu, yu, protocol=pickle.HIGHEST_PROTOCOL)

    dict_leung = getCoauthors("Victor C. M. Leung", "l/Leung:Victor_C=_M=", 2)

    with open('dictionaries/dict_leung.pickle', 'wb') as leung:
        pickle.dump(dict_leung, leung, protocol=pickle.HIGHEST_PROTOCOL)