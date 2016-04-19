import sys
import langid
import os
import nltk
from nltk.tag.api import TaggerI
from nltk.internals import find_file, find_jar, config_java, java, _java_options, find_jars_within_path
import itertools
from operator import itemgetter
from nltk.stem import WordNetLemmatizer
import networkx as nx
from nltk.collocations import * 
from nltk.stem.porter import *

tagger = nltk.tag.perceptron.PerceptronTagger()
wnl = WordNetLemmatizer()
colloc_list = []
entity_names = []

def filter_for_tags(tagged, tags=['NN', 'NNPS', 'NNP', 'NNS']):
    return [item for item in tagged if item[1] in tags]

def filter_numbers(tagged):
    return [item for item in tagged if len(item[0])>2 and not item[0].isdigit()]

def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]
 
def normalize_tags(tagged):
    return [(item[0], item[1][0:1]) for item in tagged]

def lowercase(tagged):
    return [(w.lower(),t) for (w,t) in tagged]

def rstopwords(tagged):
    return [(w,t) for (w,t) in tagged if not w in nltk.corpus.stopwords.words('english')]

def lemmatize(tagged):
    return [(wnl.lemmatize(item[0]),item[1]) if not ' ' in item[0] else (item[0],item[1]) for item in tagged]

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names

def joincolloc(tagged):
    tagged1 = []
    sw = 0
    for i in range(len(tagged)-1):
      if sw == 1:
        sw = 0
        continue
      if (tagged[i],tagged[i+1]) in colloc_list:
        sw = 1 
	if tagged[i][1].startswith('NN') or tagged[i+1][1].startswith('NN'):
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'NN'))
        elif tagged[i][1]=='RB' or tagged[i+1][1]=='RB':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'RB'))
        else:
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],tagged[i][1]))
      else:
        tagged1.append(tagged[i])
    if len(tagged)>0:
      tagged1.append(tagged[len(tagged)-1])
    return tagged1

def groupne2(tagged):
    tagged1 = []
    sw = 0
    for i in range(len(tagged)-1):
      if sw == 1:
        sw = 0
        continue
      if (tagged[i][0]+' '+tagged[i+1][0]) in entity_names:
        sw = 1
        if tagged[i][1]=='NNP' or tagged[i+1][1]=='NNP':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'NNP'))
        elif tagged[i][1]=='NN' or tagged[i+1][1]=='NN':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'NN'))
        elif tagged[i][1]=='RB' or tagged[i+1][1]=='RB':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'RB'))
        else:
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],tagged[i][1]))
      else:
       tagged1.append(tagged[i])
    if len(tagged)>0:
      tagged1.append(tagged[len(tagged)-1])
    return tagged1

def groupne3(tagged):
    tagged1 = []
    sw = 0
    for i in range(len(tagged)-2):
      if sw == 1:
        sw = 0
        continue
      if (tagged[i][0]+' '+tagged[i+1][0]+' '+tagged[i+2][0]) in entity_names:
        sw = 1
        if tagged[i][1]=='NNP' or tagged[i+1][1]=='NNP' or tagged[i+2][1]=='NNP':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0]+' '+tagged[i+2][0],'NNP'))
        elif tagged[i][1]=='NN' or tagged[i+1][1]=='NN' or tagged[i+2][1]=='NNP':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0]+' '+tagged[i+2][0],'NN'))
        elif tagged[i][1]=='RB' or tagged[i+1][1]=='RB' or tagged[i+2][1]=='NNP':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0]+' '+tagged[i+2][0],'RB'))
        else:
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0]+' '+tagged[i+2][0],tagged[i][1]))
      else:
       tagged1.append(tagged[i])
    if len(tagged)>1:
      tagged1.append(tagged[len(tagged)-2])
      tagged1.append(tagged[len(tagged)-1])
    elif len(tagged)==1:
      tagged1.append(tagged[len(tagged)-1])
    return tagged1


def joincollocbi(tagged):
    tagged1 = []
    sw = 0
    for i in range(len(tagged)-1):
      if sw == 1:
        sw = 0 
        continue
      if ' ' in tagged[i][0]:
        t1 = (tagged[i][0][tagged[i][0].find(' '):].strip(), tagged[i][1])
      else:
        t1 = (tagged[i][0], tagged[i][1])
      if ' ' in tagged[i+1][0]:
        t2 = (tagged[i+1][0][:tagged[i+1][0].find(' ')].strip(), tagged[i][1])
      else:
        t2 = (tagged[i+1][0], tagged[i+1][1])
      if (t1,t2) in colloc_list:
        sw = 1
        if tagged[i][1]=='NNP' or tagged[i+1][1]=='NNP':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'NNP'))
        elif tagged[i][1]=='NN' or tagged[i+1][1]=='NN':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'NN'))
        elif tagged[i][1]=='RB' or tagged[i+1][1]=='RB':
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],'RB'))
        else:
          tagged1.append((tagged[i][0]+' '+tagged[i+1][0],tagged[i][1]))
      else:
       tagged1.append(tagged[i])
    if len(tagged)>0:
      tagged1.append(tagged[len(tagged)-1])
    return tagged1

blacklist = []
fname=sys.argv[1]
articles = os.listdir(fname)
FOLDER = 'keywords-'+fname+'-textrank'
if not os.path.exists(FOLDER): os.makedirs(FOLDER)

tagged = []
for article in articles:
    articleFile = open(fname+'/' + article, 'r')
    for linee in articleFile:
      line=linee.decode('latin-1')
      lang = langid.classify(line.strip())
      if not lang[0]=='en':
        continue
      sentences = nltk.sent_tokenize(line.strip())
      tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
      tagged_sentences = [tagger.tag(sentence) for sentence in tokenized_sentences]
      for sentence in tagged_sentences:
        tagged.extend(sentence)
      chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
      for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))
    articleFile.close()

entity_names = set(entity_names)

bigram_measures = nltk.collocations.BigramAssocMeasures()
finder = nltk.collocations.BigramCollocationFinder.from_words(tagged)
finder.apply_freq_filter(3)
colloc_list = finder.nbest(bigram_measures.pmi, 20) # this needs to be tweaked

for article in articles:
    print 'Reading articles/' + article
    articleFile = open(fname + '/' + article, 'r')
    tagged=[]
    sentences=[]
    k=0
    for linee in articleFile:
      line = linee.decode('latin-1')
      lang = langid.classify(line.strip())
      if not lang[0]=='en':
        continue
      sents = nltk.sent_tokenize(line.strip())
      tok_sents = [nltk.word_tokenize(sent) for sent in sents]
      tagged_sents = [tagger.tag(sent) for sent in tok_sents]
      tagged_sents = [joincolloc(sent) for sent in tagged_sents]
      tagged_sents = [joincollocbi(sent) for sent in tagged_sents]
      tagged_sents = [groupne2(sent) for sent in tagged_sents]
      tagged_sents = [groupne3(sent) for sent in tagged_sents]
      tagged_sents = [filter_for_tags(sent) for sent in tagged_sents]
      tagged_sents = [normalize_tags(sent) for sent in tagged_sents]
      tagged_sents = [normalize(sent) for sent in tagged_sents]
      tagged_sents = [filter_numbers(sent) for sent in tagged_sents]
      tagged_sents = [lowercase(sent) for sent in tagged_sents]
      tagged_sents = [lemmatize(sent) for sent in tagged_sents]
      tagged_sents = [rstopwords(sent) for sent in tagged_sents]
      for sent in tagged_sents:
        tagged.extend(sent)
      sentences.extend(tagged_sents)
    
    gr = nx.MultiGraph()
 
    for sentence in sentences:
      if len(sentence)>1:
        for i in range(len(sentence)-1):
          for j in range(i+1,len(sentence)):
            try:
              s1 = sentence[i][0] + '/' + sentence[i][1]
              s2 = sentence[j][0] + '/' + sentence[j][1]
#              wt = float(1.0)/float(len(sentence)) # if weighting by sentence length is desired
              wt = 1
              gr.add_edge(s1,s2,weight=wt)
            except AdditionError, e:
              pass

    H=nx.Graph() 
    for u,v,d in gr.edges(data=True):
      w = d['weight']
      if H.has_edge(u,v):
        H[u][v]['weight'] += w
      else:
        H.add_edge(u,v,weight=w)

    calculated_page_rank = nx.pagerank(H)

    keyphraseFile = open(FOLDER + '/'+article, 'w')
    di = sorted(calculated_page_rank.iteritems(), key=itemgetter(1), reverse=True)
    dic = []
    for k, g in itertools.groupby(di, key=itemgetter(1)):
      try:
        w = str(map(itemgetter(0), g)[0])
	w = w[:w.find('/')]
        if len(w)>2 and w not in blacklist:
          if w not in dic:
            keyphraseFile.write(w.replace(' ','_') + ':' + str(k)[0:6] + '\n')
            dic.append(w)
      except:
        pass
    keyphraseFile.close()

