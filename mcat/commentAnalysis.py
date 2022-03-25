# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import argparse

import nltk
from nltk.sentiment import vader

nltk.download('vader_lexicon')  # Model download


class CommentAnalyzer:
    def __init__(self, words):
        """
        Constructors form a dictionary to be used for counting.
        Parameters: words - list of words to count
        Test docs
        """
        self.word_count = {word.lower(): 0 for word in words}  # Create dictionary with list items as key
        self.vader_sentiment = vader.SentimentIntensityAnalyzer()  # Initialize sentiment analysis model

    def analyzeComment(self, comment):
        """
        Method to get desired features from an input comment.
        Parameters: comment - string.
        Returns: dictionary with features
        """
        result = {}  # Create return dictionary
        cleaned_comment = self.preProcess(comment)  # Clean comment text
        # result['Word Counts'] = self.countWords(cleaned_comment)  # Determine word counts
        result.update(self.countWords(cleaned_comment))
        result['Sentiment'] = self.getSentiment(comment)  # Determine sentiment
        result['Code Blocks'] = self.getCodeBlockCount(cleaned_comment)  # Determine code block count
        return result

    def preProcess(self, text):
        """
        Method to clean and return text.
        Parameters: text - string.
        Returns: string after cleaning
        """
        if not isinstance(text, str):
            return ""
        cleaned_text = text.strip()  # Remove trailing and starting spaces
        cleaned_text = cleaned_text.lower()  # Convert to lowercase
        return cleaned_text

    def countWords(self, comment):
        """
        Method to determine word count.
        Parameters: comment - string
        Returns: dictionary with word counts
        """
        words = comment.split(" ")  # Split text into words
        current_word_count = self.word_count.copy()  # Copy default dict for new count
        for word in words:  # Iterate over all words
            if word in self.word_count:
                current_word_count[word] = current_word_count[word] + 1
        return current_word_count

    def getCodeBlockCount(self, comment):
        """
        Method to determine the code blocks.
        Parameters: comment - string
        Returns: integer count
        """
        count = comment.count("```")  # Find occurences of code block
        if count % 2 != 0:  # Should be in pairs
            print("Warning: Mismatched code blocks")
            return int(count / 2 - 1)  # Subtract 1 since unmatched pair
        return int(count / 2)  # Divide by 2 since pairs

    def getSentiment(self, comment):
        """
        Method to determine sentiment. Parameters: comment - string
        Returns: dictionary with positive, negative and neutral scores
        """
        return self.vader_sentiment.polarity_scores(comment)["compound"]

    def changeWords(self, words):
        """
        Method to change words to count. Parameters: Set new word count with new keys/
        """
        self.word_count = {word: 0 for word in words}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze input text segment.')
    parser.add_argument('text', help='Text to analyze')
    parser.add_argument('-w', '--words', required=False, help='File containing words to count')

    args = parser.parse_args()
    # Form word list through the file
    word_list = []
    if args.words:
        with open(args.words, 'r') as word_file:
            word_list = word_file.read().replace(" ", "").strip().split(",")
    analyzer = CommentAnalyzer(word_list)
    print(analyzer.analyzeComment(args.text))
