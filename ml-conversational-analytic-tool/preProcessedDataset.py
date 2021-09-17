# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import ast

import numpy as np
import pandas as pd
import tensorflow as tf


class PreProcessedDataset:
    def __init__(self, vocab_size=1000, no_tokens=512, max_pull_length=100):
        """
        Set flags and instance variables in constructor
        """
        self.annotated_data = None
        self.dataset = None
        self.full_dataset = None

        self.vocab_size = vocab_size
        self.no_tokens = no_tokens
        self.max_pull_length = max_pull_length
        self.curr_max_length = 0
        self.codes = {}
        self.decodes = {}
        self.all_encoded_utterances = []
        self.results = {'Constructive': [], 'Inclusive': []}
        self.all_users = []

        self.annotated_data_open = False
        self.dataset_open = False
        self.full_dataset_ready = False
        self.encode_ready = False

    def setupPreProcess(self, annotated_filename, dataset_filename):
        """
        Setup the preprocessed dataset
        """

        # Load datasets
        self.loadAnnotatedData(annotated_filename)
        self.loadDataset(dataset_filename)
        self.full_dataset = pd.merge(self.annotated_data, self.dataset, how='left', on='Number', copy=True)
        self.full_dataset = self.full_dataset[
            ['Number', 'Thread', 'Constructive', 'Inclusive', 'Title', 'User', 'Body', 'Comments', 'Review_Comments']]

        def stringToDict(string):
            string = ast.literal_eval(string)
            for i in range(len(string)):
                string[i] = ast.literal_eval(string[i])
            return string

        # Convert all json strings to dictionaries
        self.full_dataset['Comments'] = self.full_dataset['Comments'].apply(lambda comment: stringToDict(comment))
        self.full_dataset['Review_Comments'] = self.full_dataset['Review_Comments'].apply(
            lambda comment: stringToDict(comment))

    def encodeData(self):
        """
        Encode all utterances
        """

        all_utterances = self._getObsResUsers()
        # Encode each utterance
        for utterances in all_utterances:
            self.all_encoded_utterances.append(self.encode(utterances))
        # Cap pull length to max
        drop_indexes = []
        for i in range(len(self.all_encoded_utterances)):
            if len(self.all_encoded_utterances[i]) > 100:
                drop_indexes.append(i)
        drop_indexes.reverse()
        for idx in drop_indexes:
            self.all_encoded_utterances = self.all_encoded_utterances[:idx] + self.all_encoded_utterances[idx + 1:]
            self.all_users = self.all_users[:idx] + self.all_users[idx + 1:]
            self.results['Constructive'] = self.results['Constructive'][:idx] + self.results['Constructive'][idx + 1:]
            self.results['Inclusive'] = self.results['Inclusive'][:idx] + self.results['Inclusive'][idx + 1:]
        self.curr_max_length = max([len(x) for x in self.all_encoded_utterances])

    def getRoleAgnosticMatrix(self, outcome=None, padPull=True):
        """
        Get matrix observation and results for ML task outcome = Inclusive, Constructive, or None -> both
        """

        obs = []
        for i in range(len(self.all_encoded_utterances)):
            def pad(inp):
                padding = [0] * self.no_tokens
                while len(inp) < self.curr_max_length:
                    inp = np.vstack([inp, padding.copy()])
                return inp

            # Pad to maximum pull length
            if padPull:
                obs.append(np.array(pad(self.all_encoded_utterances[i])))
            else:
                obs.append(tf.convert_to_tensor(np.array(self.all_encoded_utterances[i])))
        res = self.getRes(outcome)
        return obs, res

    def getRoleMatrix(self, outcome=None, padPull=True):
        """
        Get stacked matrix observation and results for ML task
        """
        # Check if results must be padded to same length for each pull
        if padPull:
            # Author and reviwer layers
            layer_writer = []
            layer_reviewer = []

            for i in range(len(self.all_encoded_utterances)):
                writer_comments = []
                reviewer_comments = []
                writer = self.all_users[i][0]

                for j in range(len(self.all_encoded_utterances[i])):
                    # Check if author or reviewer
                    if self.all_users[i][j] == writer:
                        writer_comments.append(self.all_encoded_utterances[i][j])
                        reviewer_comments.append(np.zeros(self.no_tokens))
                    else:
                        reviewer_comments.append(self.all_encoded_utterances[i][j])
                        writer_comments.append(np.zeros(self.no_tokens))
                    padding = [0] * self.no_tokens

                    # Pad both reviewer and writer layers
                    while len(writer_comments) < self.curr_max_length:
                        writer_comments.append(padding.copy())
                        reviewer_comments.append(padding.copy())
                    layer_writer.append(np.array(writer_comments))
                    layer_reviewer.append(np.array(reviewer_comments))

            # Stack reviwer and author matrices
            obs = np.stack((layer_writer, layer_reviewer), axis=3)
            res = self.getRes(outcome)
            return obs, res
        else:
            obs = []
            for i in range(len(self.all_encoded_utterances)):
                writer_comments = []
                reviewer_comments = []
                writer = self.all_users[i][0]

                for j in range(len(self.all_encoded_utterances[i])):
                    if self.all_users[i][j] == writer:
                        writer_comments.append(self.all_encoded_utterances[i][j])
                        reviewer_comments.append(np.zeros(self.no_tokens))
                    else:
                        reviewer_comments.append(self.all_encoded_utterances[i][j])
                        writer_comments.append(np.zeros(self.no_tokens))
                # Stack individual layers since their lenghts are not equal
                obs.append(tf.convert_to_tensor(np.stack((writer_comments, reviewer_comments), axis=2)))
            res = self.getRes(outcome)
            return obs, res

    def getRes(self, outcome=None):
        """
        Get list of results
        """
        if outcome:
            return self.results[outcome]
        return pd.DataFrame(data=self.results)

    def loadAnnotatedData(self, filename):
        """
        Load annotated dataset from file
        """
        self.annotated_data = pd.read_csv(filename)
        self.annotated_data_open = True

    def loadDataset(self, filename):
        """
        Load raw data from file
        """
        self.dataset = pd.read_csv(filename)
        self.dataset_open = True

    def encode(self, utterances):
        """
        Encode an utterance through the lookup dictionary
        """
        encoded_utterances = []
        for utterance in utterances:
            obs = []
            words = utterance.split(" ")
            for word in words:
                obs.append(self.codes.get(word, 2))
                # Truncate to 512 tokens
                if len(obs) > self.no_tokens - 1:
                    break
            # Indicate message end
            if len(obs) < self.no_tokens:
                obs.append(1)
            # Pad to 512 tokens
            while len(obs) < self.no_tokens:
                obs.append(0)
            encoded_utterances.append(np.array(obs))
        return np.array(encoded_utterances)

    def _setupEncode(self):
        """
        Setup the lookup dictionary through frequency encoding
        """
        word_counts = {}
        for index, row in self.annotated_data.iterrows():
            words = row['Thread'].split(" ")
            for word in words:
                if word in word_counts:
                    word_counts[word] = word_counts[word] + 1
                else:
                    word_counts[word] = 1

        # Sort the words to generate code
        # Lower number : higher count
        # 0 - Padding, 1 - End, 2 - Missing
        # Only top 100 words
        sorted_tuple_count = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        self.codes = {}
        curr_id = 3
        for tup in sorted_tuple_count:
            self.codes[tup[0]] = curr_id
            curr_id = curr_id + 1
            if curr_id == self.vocab_size:
                break
        self.encode_ready = True

    def _getObsResUsers(self):
        """
        Get all utterances by parsing dictionary for each pull
        """
        all_utterances = []
        for index, row in self.full_dataset.iterrows():
            utterances = []
            users = []
            utterances.append(str(row['Title']) + "\n" + str(row['Body']))
            users.append(row['User'])
            temp_df_comments = pd.DataFrame(row['Comments'])
            temp_df_review_comments = pd.DataFrame(row["Review_Comments"])

            if len(temp_df_comments) > 0 or len(temp_df_review_comments) > 0:
                all_comments = temp_df_comments.append(temp_df_review_comments)
                all_comments['Created_At'] = pd.to_datetime(all_comments['Created_At'])
                all_comments = all_comments.sort_values(by=['Created_At'])

                for comment_index, comment_row in all_comments.iterrows():
                    utterances.append(comment_row['Body'])
                    users.append(comment_row['User'])

            all_utterances.append(utterances)
            self.all_users.append(users)
            self.results['Constructive'].append(row['Constructive'])
            self.results['Inclusive'].append(row['Inclusive'])

        return all_utterances
