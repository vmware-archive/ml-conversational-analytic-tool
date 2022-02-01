# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import unittest
import unittest.mock

import pandas as pd
import requests

import githubDataExtraction


class TestGitHubDataExtraction(unittest.TestCase):

    def setUp(self):
        self.test_access_token = "test-token"
        self.test_organization = "test-org"
        self.test_repo = "test-repo"
        self.extractor = githubDataExtraction.GithubDataExtractor(self.test_access_token, self.test_organization)
        self.directory_path = os.path.dirname(os.path.realpath(__file__))

    def test_get_all_repos_returns_list_of_repos(self):
        repo_one = {"name": "repo_one"}
        repo_two = {"name": "repo_two"}
        repo_list = [repo_one, repo_two]

        self.extractor.run_queries = unittest.mock.MagicMock(return_value=repo_list)

        expected = [repo_one.get("name"), repo_two.get("name")]
        actual = self.extractor.get_all_repos()
        self.assertEqual(expected, actual)

    def test_get_all_repos_calls_run_queries_with_correct_values(self):
        repo_one = {"name": "repo_one"}
        repo_list = [repo_one]

        test_query = """ { test query } """
        test_queries_and_variables = {
            "query": test_query,
            "variables": {"owner": self.test_organization}
        }

        self.extractor.query_repos = test_query
        self.extractor.run_queries = unittest.mock.MagicMock(return_value=repo_list)

        self.extractor.get_all_repos()

        self.assertEqual(1, self.extractor.run_queries.call_count)
        self.extractor.run_queries.assert_called_with(query=test_queries_and_variables)

    def test_get_all_repos_returns_empty_list_when_repos_does_not_exist(self):
        repo_list = []

        self.extractor.run_queries = unittest.mock.MagicMock(return_value=repo_list)

        actual = self.extractor.get_all_repos()
        self.assertEqual([], actual)

    def test_get_all_pull_requests_returns_dataframe(self):
        with open("{}/resources/pr_raw_data_example_one.json".format(self.directory_path)) as raw_data_file:
            pr_one = json.load(raw_data_file)
        pr_list = [pr_one]

        self.extractor.run_queries = unittest.mock.MagicMock(return_value=pr_list)
        actual = self.extractor.get_all_pull_requests(self.test_repo)
        self.assertEqual(pd.DataFrame, type(actual))

    def test_get_all_pull_requests_without_reactions_calls_run_queries_with_correct_arguments(self):
        with open("{}/resources/pr_raw_data_example_one.json".format(self.directory_path)) as raw_data_file:
            pr_one = json.load(raw_data_file)
        pr_list = [pr_one]

        test_query = """ { test query } """
        test_queries_and_variables = {
            "query": test_query,
            "variables": {"owner": self.test_organization, "repo": self.test_repo}
        }

        self.extractor.query_pull_requests_without_reactions = test_query
        self.extractor.run_queries = unittest.mock.MagicMock(return_value=pr_list)

        self.extractor.get_all_pull_requests(self.test_repo, reaction_flag=False)

        self.assertEqual(1, self.extractor.run_queries.call_count)
        self.extractor.run_queries.assert_called_with(query=test_queries_and_variables)

    def test_get_all_pull_requests_with_reactions_calls_run_queries_with_correct_arguments(self):
        with open("{}/resources/pr_raw_data_example_one.json".format(self.directory_path)) as raw_data_file:
            pr_one = json.load(raw_data_file)
        pr_list = [pr_one]

        test_query = """ { test query } """
        test_queries_and_variables = {
            "query": test_query,
            "variables": {"owner": self.test_organization, "repo": self.test_repo}
        }

        self.extractor.query_pull_requests_with_reactions = test_query
        self.extractor.run_queries = unittest.mock.MagicMock(return_value=pr_list)

        self.extractor.get_all_pull_requests(self.test_repo, reaction_flag=True)

        self.assertEqual(1, self.extractor.run_queries.call_count)
        self.extractor.run_queries.assert_called_with(query=test_queries_and_variables)

    def test_get_all_pull_requests_returns_empty_dataframe_when_pull_requests_does_not_exist(self):
        pr_list = []
        self.extractor.run_queries = unittest.mock.MagicMock(return_value=pr_list)

        actual = self.extractor.get_all_pull_requests(self.test_repo)
        self.assertTrue(actual.empty)

    def test_get_all_pull_requests_returns_sorted_data_frame(self):
        with open("{}/resources/pr_raw_data_example_one.json".format(self.directory_path)) as raw_data_file_one:
            pr_one = json.load(raw_data_file_one)
        with open("{}/resources/pr_raw_data_example_two.json".format(self.directory_path)) as raw_data_file_two:
            pr_two = json.load(raw_data_file_two)
        pr_list = [pr_two, pr_one]

        self.extractor.run_queries = unittest.mock.MagicMock(return_value=pr_list)
        actual = self.extractor.get_all_pull_requests(self.test_repo)
        self.assertEqual(1, actual["Number"].iloc[0])
        self.assertEqual(10, actual["Number"].iloc[1])

    def test_get_pull_features_without_reactions(self):
        self.extractor.reaction_flag = False

        with open("{}/resources/pr_raw_data_example_one.json".format(self.directory_path)) as raw_data_file:
            pr = json.load(raw_data_file)

        with open("{}/resources/pr_post_processing_without_reactions_example.json".format(
                self.directory_path)) as post_processed_data_file:
            expected = json.load(post_processed_data_file)

        actual = self.extractor.get_pull_features(pr)
        self.assertEqual(expected, actual)

    def test_get_pull_features_with_reactions(self):
        self.extractor.reaction_flag = True

        with open("{}/resources/pr_raw_data_example_one.json".format(self.directory_path)) as raw_data_file:
            pr = json.load(raw_data_file)

        with open("{}/resources/pr_post_processing_with_reactions_example.json".format(
                self.directory_path)) as post_processed_data_file:
            expected = json.load(post_processed_data_file)

        actual = self.extractor.get_pull_features(pr)
        self.assertEqual(expected, actual)

    def test_get_pull_features_returns_none_or_empty_list_for_missing_data(self):
        self.extractor.reaction_flag = False

        pr = {}
        actual = self.extractor.get_pull_features(pr)

        self.assertEqual(None, actual.get("Number"))
        self.assertEqual(None, actual.get("Title"))
        self.assertEqual([], actual.get("Comments"))
        self.assertEqual([], actual.get("Review_Comments"))

    def test_list_of_comments_returns_post_processed_list_with_reactions(self):
        self.extractor.reaction_flag = True

        test_content = "test-content"
        test_date = "test-date"
        test_user_name = "test-user-name"
        test_body = "test-body"

        comments = [
            {
                "author": {"login": test_user_name},
                "createdAt": test_date,
                "body": test_body,
                "updatedAt": test_date,
                "reactions": {"nodes": [
                    {"content": test_content, "createdAt": test_date, "user": {"login": test_user_name}}]}
            }
        ]

        expected = [
            {
                "Created_At": test_date,
                "User": test_user_name,
                "Body": test_body,
                "Updated_At": test_date,
                "Reactions": [{
                    "Content": test_content,
                    "Created_At": test_date,
                    "User": test_user_name
                }]
            }
        ]

        actual = self.extractor.list_of_comments(comments)
        self.assertEqual(expected, actual)
        self.assertTrue(actual[0].get("Reactions"))

    def test_list_of_comments_returns_post_processed_list_without_reactions(self):
        self.extractor.reaction_flag = False

        test_date = "test-date"
        test_user_name = "test-user-name"
        test_body = "test-body"

        comments = [
            {
                "author": {"login": test_user_name},
                "createdAt": test_date,
                "body": test_body,
                "updatedAt": test_date
            }
        ]

        expected = [
            {
                "Created_At": test_date,
                "User": test_user_name,
                "Body": test_body,
                "Updated_At": test_date
            }
        ]

        actual = self.extractor.list_of_comments(comments)
        self.assertEqual(expected, actual)
        self.assertEqual(None, actual[0].get("Reactions"))

    def test_list_of_comments_returns_empty_list_for_missing_data(self):
        self.extractor.reaction_flag = True

        test_date = "test-date"
        test_user_name = "test-user-name"
        test_body = "test-body"

        comment_without_reactions = {
            "author": {"login": test_user_name},
            "createdAt": test_date,
            "body": test_body,
            "updatedAt": test_date
        }
        comments = [comment_without_reactions]

        expected = [
            {
                "Created_At": test_date,
                "User": test_user_name,
                "Body": test_body,
                "Updated_At": test_date,
                "Reactions": []
            }
        ]

        actual = self.extractor.list_of_comments(comments)
        self.assertEqual(expected, actual)
        self.assertEqual(0, len(actual[0].get("Reactions")))

    def test_list_of_comments_replaces_missing_data_with_none(self):
        self.extractor.reaction_flag = True

        test_user_name = "test-user-name"
        comment_with_missing_keys = {
            "author": {"login": test_user_name}
        }
        comments = [comment_with_missing_keys]

        actual = self.extractor.list_of_comments(comments)
        self.assertEqual(None, actual[0].get("Created_At"))
        self.assertEqual(None, actual[0].get("Body"))
        self.assertEqual(None, actual[0].get("Updated_At"))
        self.assertEqual(test_user_name, actual[0].get("User"))
        self.assertEqual([], actual[0].get("Reactions"))

    def test_list_of_comments_returns_empty_list_when_comments_does_not_exist(self):
        self.extractor.reaction_flag = True
        comments = []

        actual = self.extractor.list_of_comments(comments)
        self.assertFalse(actual)

    @unittest.mock.patch("requests.post")
    def test_run_queries_returns_list_of_data(self, mock_request_post):
        test_query = """ { test query } """
        self.extractor.query_repos = test_query

        test_queries_and_variables = {
            "query": test_query,
            "variables": {"key": "value"}
        }

        data = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "test-end-cursor",
                            "hasNextPage": False
                        },
                        "nodes": {
                            "test": "test-value"
                        }
                    }
                }
            }
        }

        mock_request_post.return_value.json.return_value = data
        mock_request_post.return_value.status_code = 200

        self.extractor.run_queries(test_queries_and_variables)

        mock_request_post.assert_called_once_with(
            url='https://api.github.com/graphql',
            json=test_queries_and_variables,
            headers={'Authorization': 'bearer ' + self.test_access_token}
        )

    @unittest.mock.patch("requests.post")
    def test_run_queries_throws_an_exception_if_request_status_code_is_not_200_403_502(self, mock_request_post):
        test_status_code = 401
        test_reason = "test-reason"
        test_json_response = {}

        mock_response = [unittest.mock.MagicMock()]
        mock_response[0].status_code = test_status_code
        mock_response[0].reason = test_reason
        mock_response[0].json.return_value = test_json_response
        mock_request_post.side_effect = mock_response

        expected = "{}: {} {}".format(test_status_code, test_reason, test_json_response)

        with self.assertRaises(requests.HTTPError) as error:
            self.extractor.run_queries({})

        self.assertEqual(expected, error.exception.args[0])

    @unittest.mock.patch("requests.post")
    def test_run_queries_makes_multiple_post_calls_when_next_page_is_available(self, mock_request_post):
        self.extractor.query_repos = """ { test query } """

        test_query_and_variables = {
            "query": self.extractor.query_repos,
            "variables": {"key": "value"}
        }

        data_with_hasNextPage = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "test-end-cursor",
                            "hasNextPage": True
                        },
                        "nodes": {
                            "test": "test-value"
                        }
                    }
                }
            }
        }

        data_without_hasNextPage = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "test-end-cursor",
                            "hasNextPage": False
                        },
                        "nodes": {
                            "test": "test-value"
                        }
                    }
                }
            }
        }

        mock_response = [unittest.mock.MagicMock(), unittest.mock.MagicMock()]
        mock_response[0].json.return_value = data_with_hasNextPage
        mock_response[0].status_code = 200
        mock_response[1].json.return_value = data_without_hasNextPage
        mock_response[1].status_code = 200
        mock_request_post.side_effect = mock_response

        mock_request_post.return_value = unittest.mock.MagicMock(return_value=2)

        self.extractor.run_queries(test_query_and_variables)
        self.assertEqual(2, mock_request_post.call_count)

    @unittest.mock.patch("requests.post")
    def test_run_queries_returns_partial_data_when_rate_limit_reached(self, mock_request_post):
        self.extractor.query_repos = """ { test query } """

        test_query_and_variables = {
            "query": self.extractor.query_repos,
            "variables": {"key": "value"}
        }

        data_with_hasNextPage = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "test-end-cursor",
                            "hasNextPage": True
                        },
                        "nodes": {
                            "test": "test-value"
                        }
                    }
                }
            }
        }

        mock_response = [unittest.mock.MagicMock(), unittest.mock.MagicMock()]
        mock_response[0].json.return_value = data_with_hasNextPage
        mock_response[0].status_code = 200
        mock_response[1].status_code = 403
        mock_request_post.side_effect = mock_response

        actual = self.extractor.run_queries(test_query_and_variables)
        self.assertEqual(2, mock_request_post.call_count)
        self.assertEqual(1, len(actual))

    @unittest.mock.patch("requests.post")
    def test_run_queries_returns_partial_data_when_call_fails_after_retry(self, mock_request_post):
        test_query = """ { test query } """
        self.extractor.query_repos = test_query

        test_queries_and_variables = {
            "query": test_query,
            "variables": {"key": "value"}
        }

        data_with_all_keys = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "test-end-cursor",
                            "hasNextPage": True
                        },
                        "nodes": {
                            "test": "test-value"
                        }
                    }
                }
            }
        }

        data_with_missing_nodes = {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "test-end-cursor",
                            "hasNextPage": False
                        }
                    }
                }
            }
        }

        mock_response = [unittest.mock.MagicMock(), unittest.mock.MagicMock(), unittest.mock.MagicMock()]
        mock_response[0].json.return_value = data_with_all_keys
        mock_response[0].status_code = 200
        mock_response[1].json.return_value = data_with_missing_nodes
        mock_response[1].status_code = 502
        mock_response[2].json.return_value = data_with_missing_nodes
        mock_response[2].status_code = 502
        mock_request_post.side_effect = mock_response

        actual = self.extractor.run_queries(test_queries_and_variables)
        self.assertEqual(mock_request_post.call_count, 3)
        self.assertEqual(1, len(actual))

    @unittest.mock.patch("utils.export_to_cvs")
    @unittest.mock.patch("utils.construct_file_name")
    def test_retrieve_and_export_pull_request_data_exports_data(self, mock_construct_file, mock_export):
        test_data_frame = pd.DataFrame({"test": 1, "one": [{"two": "three"}]})
        self.extractor.get_all_pull_requests = unittest.mock.MagicMock(return_value=test_data_frame)

        test_file_name = "{}_{}.csv".format(self.test_organization, self.test_repo)
        mock_construct_file.return_value = test_file_name

        self.extractor.retrieve_and_export_pull_request_data(repo=self.test_repo, reactions_flag=False, name=None,
                                                             organization=self.test_organization)

        mock_construct_file.assert_called_once_with(None, self.test_organization, self.test_repo)
        mock_export.assert_called_once_with(test_data_frame, test_file_name)


if __name__ == '__main__':
    unittest.main()
