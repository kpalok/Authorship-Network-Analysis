import pickle
import time
import sys
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.etree.ElementTree import parse

PERSON_URL = "https://dblp.uni-trier.de/pers/xx/{}.xml"
COAUTHORS_URL = "https://dblp.uni-trier.de/pers/xc/{}.xml"

def loadPickleDict(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)

def getAverageCoauthorCountPerCoAuthor(author_name, dict_pickle):

    authors = loadPickleDict(dict_pickle)
    c3_sum = 0

    for coauthor in authors[author_name]:
        couauthors2 = authors[coauthor[0]]
        c3_sum += len(couauthors2)
    
    return c3_sum / len(authors[author_name])

def getAffiliation(author_urlpt):
    for i in range(0, 10):
        try:
            dblp_url = urlopen(PERSON_URL.format(author_urlpt))
            if i > 0:
                print("Connection reopened iteration: ", i)
            break
        except HTTPError as ex:
            if ex.code == 429:
                if i == 9:
                    raise Exception("Failed to open xml document after 10 retries: {}".format(ex))
                else:
                    time.sleep(10*(i+1))
            else:
                print(ex, " Returned None for affiliation")
                return None

    person_xml = parse(dblp_url)
    affiliation = None
    for note in person_xml.getroot().iter('note'):
        if note.get('type') == "affiliation":
            affiliation = note.text
            break

    return affiliation

def getCoauthors(author_name, author_urlpt, max_depth):
    authors = {}
    affiliations = {}
    coauthors = []

    for i in range(0, 10):
        try:
            dblp_url = urlopen(COAUTHORS_URL.format(author_urlpt))
            if i > 0:
                print("Connection reopened iteration: ", i)
            break
        except HTTPError as ex:
            if i == 9:
                raise Exception("Failed to open xml document after 10 retries: {}".format(ex))
            else:
                time.sleep(10*(i+1))

    coauthors_xml = parse(dblp_url)

    for author in coauthors_xml.getroot().iter('author'):
        name = author.text
        urlpt = author.get('urlpt')
        count = int(author.get('count'))
        affiliations[name] = getAffiliation(urlpt)
        coauthors.append((name, urlpt, count))

    authors[author_name] = coauthors
    affiliations[author_name] = getAffiliation(author_urlpt)

    if max_depth > 1:
        i = 0
        for coauthor in coauthors:
            if not coauthor[0] in authors:
                auth, aff = getCoauthors(coauthor[0], coauthor[1], max_depth-1)
                authors.update(auth)
                affiliations.update(aff)
            else:
                print("Skipped author that was already processed")
            i += 1
            print(i, "/", len(coauthors))

    return authors, affiliations

# if __name__ == "__main__":
    # auth_yu, aff_yu = getCoauthors("Philip S. Yu", "y/Yu:Philip_S=", 2)

    # with open('dictionaries/auth_yu.pickle', 'wb') as yu:
    #     pickle.dump(auth_yu, yu, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('dictionaries/aff_yu.pickle', 'wb') as yu:
    #     pickle.dump(aff_yu, yu, protocol=pickle.HIGHEST_PROTOCOL)

    # auth_leung, aff_leung = getCoauthors("Victor C. M. Leung", "l/Leung:Victor_C=_M=", 2)

    # with open('dictionaries/auth_leung.pickle', 'wb') as leung:
    #     pickle.dump(auth_leung, leung, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('dictionaries/aff_leung.pickle', 'wb') as leung:
    #     pickle.dump(aff_leung, leung, protocol=pickle.HIGHEST_PROTOCOL)

    # print("Philip S. Yu average co-authors of each co-author: ", getAverageCoauthorCountPerCoAuthor("Philip S. Yu", 'dictionaries/dict_yu.pickle'))
    # print("Victor C. M. Leung average co-authors of each co-author: ", getAverageCoauthorCountPerCoAuthor("Victor C. M. Leung", 'dictionaries/dict_leung.pickle'))