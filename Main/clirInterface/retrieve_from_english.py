# -*- coding: utf-8 -*-
import urllib2, sys, json, os, io, re, string
from urllib import quote
from api import api_key
### IR #####
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../irInterface'))
from indriHandler import singleIndriQuery
import queryBuilder,indriDocFetch

############
DEBUG = False
#api_key = "AIzaSyCDWvrBXpTFAfbcJqkyaVZrL_AwL2EM2pc"
translation_dir = "../Data/wikipedia_translations"
DOCS = {}
def translate(text,source="tr",target="en",domain="google"):
    escaped_text = quote(text.encode('utf8'), '')
    google_url = "https://www.googleapis.com/language/translate/v2"
    full_url="%s?q=%s&target=%s&format=text&source=%s&key=%s" %(google_url,escaped_text,target,source,api_key)
    req = urllib2.Request(url=full_url)
    try:
        response = urllib2.urlopen(req)
    except:
        sys.stderr.write("%s %s\n[%s...] couldn't translated\n" % (sys.exc_info()[0],sys.exc_info()[1],text[0:20]))
        return text
    res = json.loads(response.read().decode('utf-8'))
    translations = res['data']['translations']
    if translations:
        return translations[0]['translatedText']
    else:
        sys.stderr.write("No translation received for [%s...]\n" % text[0:20])
        return text

def translate_en(text,domain="google"):
    return translate(text,source="en",target="tr")

def fetch_and_translate(doc_id,doc_filename):
    doc_title,doc = indriDocFetch.getDoc(doc_id,lang="en")
    if not doc_title:
        sys.stderr.write("ERROR [Doc id:%s] [indriDocFetch.getDoc]../src/CompressedCollection.cpp(705): Unable to find document %s in the collection.\n" %(doc_id,doc_id))
        return "ERROR [Doc id:%s] [indriDocFetch.getDoc]../src/CompressedCollection.cpp(705): Unable to find document %s in the collection.\n" %(doc_id,doc_id) 
    doc_title_translated = translate_en(doc_title)
    translated_doc = [doc_title_translated,]
    DOCS[doc_id] =  "%s (%s)" % (doc_title,doc_title_translated)
    for part in doc.split("\n"):
        if len(part) < 5000:
            part_translated = translate_en(part)
            translated_doc.append(part_translated)
        else:
            sys.stderr.write("Doc id %s [HTTP Error 413: Request Entity Too Large]\n" %doc_id)
    translated_doc_str = "\n".join(translated_doc)
    with io.open(doc_filename,"w") as doc_file:
        doc_file.write(translated_doc_str)
    return translated_doc_str

def query(question_en, qID=6666):
    param_file = "singleFromWeb_en" + str(qID)
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    question_en_cleaned = regex.sub(' ', question_en)
    queryBuilder.buildIndriQuerySingle_en(param_file, question_en_cleaned)
    doc_ids = singleIndriQuery(param_file, count=3)
    translated_docs = []
    for doc_id in doc_ids:
        try:
            int(doc_id)            
            doc_filename = os.path.join(translation_dir, doc_id)
            if os.path.exists(doc_filename):
                with open(doc_filename) as doc_file:
                    translated_docs.append("".join(doc_file.readlines()))
            else:
                translated_docs.append(fetch_and_translate(doc_id,doc_filename))
        except ValueError:
            sys.stderr.write("Query error at %s\n" %question_en_cleaned)
            break
        except AttributeError:
            sys.stderr.write("%s %s \n %s %s" %(sys.exc_info()[0],sys.exc_info()[1],doc_id,doc_filename))
        if DEBUG:
            sys.stdout.write("[%s] %s\n" %(doc_id,DOCS.get(doc_id) or ""))
    return translated_docs

def get_last_query():
    param_file = "singleFromWeb_en"
    doc_ids = singleIndriQuery(param_file, count=3)
    with open('../IR/queries/singleFromWeb_en') as q_file:
        print(q_file.readlines())
    return doc_ids



def main(question_tr, qID=6666):
    question_en = translate(question_tr)
    if DEBUG:
        sys.stdout.write("%s\n" % question_en)
    docs_list = query(question_en, qID)
    #docs_tr = translate_en(docs)
    #queryBuilder.queryDir = '../IR/queries/'

    #queryBuilder.indexDir = '../IR/indri-5.0/vikiEBAindex/'

    return docs_list

#https://developers.google.com/apis-explorer/?hl=en_US#p/translate/v2/language.translations.list?q=T%25C3%25BCrkiyenin+en+b%25C3%25BCy%25C3%25BCk+ovas%25C4%25B1+hangisidir%253F&target=en&format=text&source=tr&_h=3&

#https://www.googleapis.com/language/translate/v2?q=T%C3%BCrkiye'nin+en+b%C3%BCy%C3%BCk+ovas%C4%B1+hangisidir%3F&target=en&format=text&source=tr&key=

if __name__ == "__main__":
    print sys.argv

    filename = sys.argv[1] if len(sys.argv) > 1 else "/home/hazircevap/hazircevap/Data/q.q"
    with open(filename) as q_file:
        lines = q_file.readlines()

    all_questions = []

    for line in lines:
        all_questions.append(line.split("|")[0].strip())

    docs_dict = {}
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../Data/wikipedia_translations/")
    for filename in next(os.walk(path))[2]:
        with open(os.path.join(path,filename)) as w_file:
            docs_dict[filename] = w_file.readline().strip()

    docs_dict['1217700'] = "??rlanda Cumhuriyeti"
    docs_dict['44265'] = "Waterford Waterford"
    docs_dict['29151'] = "Brno"
    docs_dict['960585'] = "??ukurova"
    docs_dict['1379071'] = "Do??u Anadolu B??lgesi"

    DOCS = docs_dict
    DEBUG = True
    i = 1 #int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for ind,qu in enumerate(all_questions[i:]):
        sys.stdout.write("[%d] %s\n" %(ind+i,qu))
        docs_l = main(qu)
        sys.stdout.write("---------\n")
