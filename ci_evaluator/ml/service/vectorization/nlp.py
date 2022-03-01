import math
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.porter import PorterStemmer
import pandas as pd
import re
import service.constants as cs


class NLP:

    def __init__(self):
        # nltk.download('stopwords')
        # nltk.download('vader_lexicon')
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.corpus = self.setStandardCorpus()

    def getCleanedTokenList(self, text, filtr=False, corpus=None):
        text = re.sub('[^0-9a-zA-Z]+', ' ', text)
        tokenlist = text.split()

        new_tokenlist = []
        for token in tokenlist:
            if len(token) > 15 : continue
            temp = token.lower()
            if (not self.containsDig(temp)) and (temp not in self.stop_words):
                if not filtr or (temp in corpus):
                    new_tokenlist.append(self.stemmer.stem(temp))

        return new_tokenlist

    def getCorpus(self, df):
        corpus = ''
        for i in range(len(df)):
            corpus += (' ' + df[i])

        return corpus

    def setStandardCorpus(self):
        data_fr = pd.read_csv(cs.WORD_SET, delimiter=',')
        list_df = list(data_fr['Words'])
        self.corpus = self.getCorpus(list_df)
    
    def containsDig(self, text):
        for c in text :
            if c.isdigit() : return True
        return False

    def removeDuplicates(self, token_list):
        return list(set(token_list))

    def getTermFrequencies(self, df, token_list):
        term_frequencies = {}
        for txt_id in range(len(df)):
            txt_tklist = self.getCleanedTokenList(df[txt_id], filtr=True, corpus=self.corpus)
            term_frequencies[str(txt_id)] = {}
            for word in token_list:
                term_frequencies[str(txt_id)][word] = txt_tklist.count(word)

        return term_frequencies

    def getDocumentFrequencies(self, df, token_list):
        tfs = self.getTermFrequencies(df, token_list)
        document_frequencies = {}
        for word in token_list:
            document_frequencies[word] = 0
            for txt_id in range(len(df)):
                comment_term_frequencies = tfs[str(txt_id)]
                if comment_term_frequencies[word] != 0:
                    document_frequencies[word] += 1
            document_frequencies[word] /= len(df)

        return document_frequencies

    def getTFIDFs(self, df):
        # corpus = self.getCorpus(df)
        if not self.corpus:
            self.setStandardCorpus()
        token_list = self.getCleanedTokenList(self.corpus)
        token_list = sorted(self.removeDuplicates(token_list))

        tfs = self.getTermFrequencies(df, token_list)
        dfs = self.getDocumentFrequencies(df, token_list)

        tfidf_scores = {}
        for txt_id in range(len(df)):
            tfidf_scores[str(txt_id)] = {}
            for word in token_list :
                if dfs[word] == 0 :
                    tfidf_scores[str(txt_id)][word] = 0
                else :
                    tfidf = tfs[str(txt_id)][word] * math.log(1 / dfs[word])
                    tfidf_scores[str(txt_id)][word] = tfidf

        tfidfs_df = pd.DataFrame(columns=token_list)
        for txt_id in range(len(df)):
            tfidfs_df.loc[txt_id] = list(tfidf_scores[str(txt_id)].values())

        return tfidfs_df

    def getSentimentalAnalisys(self, df):
        sentiments = ['sa_negative', 'sa_neutral', 'sa_positive', 'sa_compound']
        sentiment_df = pd.DataFrame(columns=sentiments)
        for txt_id in range(len(df)):
            sentiment_df.loc[txt_id] = list(self.sia.polarity_scores(df[txt_id]).values())

        return sentiment_df
