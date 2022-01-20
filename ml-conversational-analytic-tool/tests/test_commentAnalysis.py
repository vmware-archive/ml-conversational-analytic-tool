import unittest
import unittest.mock

import commentAnalysis

class TestCommentAnalysis(unittest.TestCase):

    def setUp(self) -> None:
        self.sentiment_analyzer = commentAnalysis.vader.SentimentIntensityAnalyzer()
        self.sentiment_analyzer.polarity_scores = unittest.mock.MagicMock(return_value={"compound": 1.0})

    def test_CommentAnalyzer_init(self):
        analyzer = commentAnalysis.CommentAnalyzer(['test'])
        self.assertEqual({'test': 0}, analyzer.word_count)

    def test_analyzeComment(self):
        analyzer = commentAnalysis.CommentAnalyzer(['test'])
        analyzer.vader_sentiment = self.sentiment_analyzer
        result = analyzer.analyzeComment("This is a test PR")
        self.assertEqual({'test': 1, 'Sentiment': 1.0, 'Code Blocks': 0}, result)

    def test_analyzeComment_with_empty_comment(self):
        analyzer = commentAnalysis.CommentAnalyzer(['empty comment'])
        analyzer.vader_sentiment = self.sentiment_analyzer
        result = analyzer.analyzeComment("")
        self.assertEqual({'empty comment': 0, 'Sentiment': 1.0, 'Code Blocks': 0}, result)

    def test_analyzeComment_with_codeBlocks(self):
        analyzer = commentAnalysis.CommentAnalyzer(['code block test'])
        analyzer.vader_sentiment = self.sentiment_analyzer
        result = analyzer.analyzeComment("```This patch has blocks```, ```This is second block```")
        self.assertEqual({'code block test': 0, 'Sentiment': 1.0, 'Code Blocks': 2}, result)

    def test_preProcess(self):
        analyzer = commentAnalysis.CommentAnalyzer(['preProcess test'])
        result = analyzer.preProcess("THIS is a TEST COMMENT")
        self.assertEqual("this is a test comment", result)

    def test_countWords(self):
        analyzer = commentAnalysis.CommentAnalyzer(['count words test'])
        result = analyzer.countWords("This is a test comment")
        self.assertEqual({'count words test': 0}, result)

    def test_getSentiment(self):
        analyzer = commentAnalysis.CommentAnalyzer(['sentiment test'])
        result = analyzer.getSentiment("This is a very good PR")
        self.assertEqual(float, type(result))

    def test_getCodeBlockCount(self):
        analyzer = commentAnalysis.CommentAnalyzer(['test'])
        result = analyzer.getCodeBlockCount("```This comment has code block``` ``` this is the 2nd code block```")
        self.assertEqual(2, result)
