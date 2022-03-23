# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import argparse
import os
from pathlib import Path

import pandas as pd

import utils
from commentAnalysis import CommentAnalyzer

FILE_NAME_SUFFIX = "annotated"


class Featurizer:
    def __init__(self, retain_features, analysis_features):
        """
        Constructor sets instance variables
        Inputs: Retained Features (list) -> pull data features, Analysis Features (list) - > comment analysis features
        Docs test
        """
        self.analysis_features = analysis_features
        self.retain_pull_features = retain_features
        self.raw_filename = ""
        self.raw_data = None
        self.featurized_data = None
        self.commentAnalyzer = None

    def readRawData(self, filename):
        """
        Function to read raw data stored as csv
        Inputs: File location (string) -> input raw data file location
        """
        self.raw_filename = filename
        self.raw_data = pd.read_csv(filename)

        # Convert Comments and Review Comments to dictionary
        self.raw_data['Comments'] = self.raw_data['Comments'].apply(lambda comment: utils.string_to_dict(comment))
        self.raw_data['Review_Comments'] = self.raw_data['Review_Comments'].apply(
            lambda comment: utils.string_to_dict(comment))

    def setupCommentAnalyzer(self, filename):
        """
        Function to obtain Comment Analyzer with parameters
        Inputs: File location (string) -> .txt containing keywords to count
        """
        word_list = []

        # Open file to obtain list of words in Comment Analzyer
        if filename:
            with open(filename, 'r') as wordFile:
                word_list = wordFile.read().replace(" ", "").strip().split(',')
        self.commentAnalyzer = CommentAnalyzer(word_list)
        self.analysis_features = self.analysis_features + word_list
        print("Comment Analyzer Setup")

    def formFeatures(self):
        """
        Function to create/export dataset with desired features
        Inputs: Name of file to export (string), export flag (boolean)
        """
        features = []  # List of rows to convert to dataframe

        # Iterate over each pull
        for index, row in self.raw_data.iterrows():
            row_features = {}  # Dictionary to store row features

            # Pull Request Features
            for feature in self.retain_pull_features:
                row_features[feature] = row[feature]
            pull_analyzed = self.commentAnalyzer.analyzeComment(row["Body"])

            for analysis in pull_analyzed:
                row_features["Pull_" + analysis] = pull_analyzed[analysis]

            # Comment Features
            if len(row['Comments']) > 0:
                temp_df_comments = pd.DataFrame(row['Comments'])
                all_comment_analysis = []

                for comment_index, comment_row in temp_df_comments.iterrows():
                    all_comment_analysis.append(self.commentAnalyzer.analyzeComment(comment_row["Body"]))

                all_comment_analysis = pd.DataFrame(
                    data=all_comment_analysis)  # Form dataset of all individual comment features

                # Aggregate comment features
                for column in self.analysis_features:
                    row_features["Comment_Mean_" + column] = all_comment_analysis[column].mean()
                    row_features["Comment_Median_" + column] = all_comment_analysis[column].median()
                    row_features["Comment_Mode_" + column] = all_comment_analysis[column].mode()
                    row_features["Comment_Max_" + column] = all_comment_analysis[column].max()
                    row_features["Comment_Presence_Count_" + column] = len(
                        all_comment_analysis[all_comment_analysis[column] > 0.5])

                row_features["Comment_Unique_Users"] = len(temp_df_comments["User"].unique())
                row_features["First_Comment"] = min(temp_df_comments["Created_At"])
            else:  # If there are no comment set to none
                for column in self.analysis_features:
                    row_features["Comment_Mean_" + column] = None
                    row_features["Comment_Median_" + column] = None
                    row_features["Comment_Mode_" + column] = None
                    row_features["Comment_Max_" + column] = None
                    row_features["Comment_Presence_Count_" + column] = None

                row_features["Comment_Unique_Users"] = None
                row_features["First_Comment"] = None

            # Review Features
            if len(row['Review_Comments']) > 0:
                temp_df_review_comments = pd.DataFrame(row['Review_Comments'])
                all_review_comment_analysis = []

                for review_comment_index, review_comment_row in temp_df_review_comments.iterrows():
                    all_review_comment_analysis.append(self.commentAnalyzer.analyzeComment(review_comment_row["Body"]))
                all_review_comment_analysis = pd.DataFrame(data=all_review_comment_analysis)

                # Aggregate review features
                for column in all_review_comment_analysis:
                    row_features["Review_Comment_Mean_" + column] = all_review_comment_analysis[column].mean()
                    row_features["Review_Comment_Median_" + column] = all_review_comment_analysis[column].median()
                    row_features["Review_Comment_Mode_" + column] = all_review_comment_analysis[column].mode()
                    row_features["Review_Comment_Max_" + column] = all_review_comment_analysis[column].max()
                    row_features["Review_Comment_Presence_Count_" + column] = len(
                        all_review_comment_analysis[all_review_comment_analysis[column] > 0.5])

                row_features["Review_Comment_Unique_Users"] = len(temp_df_review_comments["User"].unique())
                row_features["First_Review_Comment"] = min(temp_df_review_comments["Created_At"])
            else:  # If there are no reviews set to none
                for column in self.analysis_features:
                    row_features["Review_Comment_Mean_" + column] = None
                    row_features["Review_Comment_Median_" + column] = None
                    row_features["Review_Comment_Mode_" + column] = None
                    row_features["Review_Comment_Max_" + column] = None
                    row_features["Review_Comment_Presence_Count_" + column] = None

                row_features["Review_Comment_Unique_Users"] = None
                row_features["First_Review_Comment"] = None

            # Add pull features to list of row features
            features.append(row_features)
        export_df = pd.DataFrame(data=features)
        return export_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Form features from raw data.')
    parser.add_argument('rawdatafile', help='Raw Data Filename')
    parser.add_argument('-w', '--words', required=False, help='File containing words to count')
    parser.add_argument('-n', '--name', required=False, help='Output file name. If not specified, the name is '
                                                             'constructed like this: <rawdatafile>{'
                                                             'suffix}.csv'.format(suffix=FILE_NAME_SUFFIX))

    args = parser.parse_args()

    RETAINED_FEATURES = ["Number", "URL", "Title", "State", "Body", "Deletions", "Additions", "User", "Comments_Num",
                         "Commits_Num", "Created_At", "Closed_At", "Merged", "Merged_At", "Review_Comments_Num"]
    COMMENT_ANALYSIS_FEATURES = ["Sentiment", "Code Blocks"]

    featurizer = Featurizer(RETAINED_FEATURES, COMMENT_ANALYSIS_FEATURES)
    featurizer.readRawData(args.rawdatafile)
    featurizer.setupCommentAnalyzer(args.words)
    df = featurizer.formFeatures()
    file_name = utils.construct_file_name(args.name, args.rawdatafile, FILE_NAME_SUFFIX)
    utils.export_to_cvs(df, file_name)
