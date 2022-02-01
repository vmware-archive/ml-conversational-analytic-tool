# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import argparse
import os

import pandas as pd
import requests

import utils


class GithubDataExtractor:
    def __init__(self, access_token, organization):
        """
        Constructor requires an access token to start a Github session, and specifies instance variables
        """
        self.reaction_flag = False
        self.organization = organization
        self.query_repos = self.load_query('repos.graphql')
        self.query_pull_requests_without_reactions = self.load_query('pull_requests_without_reactions.graphql')
        self.query_pull_requests_with_reactions = self.load_query('pull_requests_with_reactions.graphql')
        self.headers = {'Authorization': 'bearer ' + access_token}

    def get_all_repos(self):
        """
         Method to get all repos of an organization
         Parameters: None
         Returns: A list of repository names
         """
        queries_and_variables = {
            'query': self.query_repos,
            'variables': {'owner': self.organization}
        }
        repository_list = self.run_queries(query=queries_and_variables)
        repositories = [repository.get('name') for repository in repository_list]
        return repositories

    def get_all_pull_requests(self, repo, reaction_flag=False):
        """
        Method to get all pull requests from a repo
        Parameters:
            repo - string
            reaction_flag - boolean
        Returns: dataframe containing rows of pull requests
        """
        self.reaction_flag = reaction_flag
        if self.reaction_flag:
            query = self.query_pull_requests_with_reactions
        else:
            query = self.query_pull_requests_without_reactions

        queries_and_variables = {
            'query': query,
            'variables': {'owner': self.organization, 'repo': repo}
        }
        pull_request_list = self.run_queries(query=queries_and_variables)
        pull_data = (self.get_pull_features(pr) for pr in pull_request_list)
        pull_request_df = pd.DataFrame(pull_data)

        try:
            # sort by the first column: Pull request number
            return pull_request_df.sort_values(by=pull_request_df.columns[0])
        except IndexError:
            return pull_request_df

    def load_query(self, file_name, directory='queries'):
        """
        Method to load graphql queries
        Parameters: file_name - name of the graphql query file
        Returns: string
        """
        directory_path = os.path.dirname(os.path.realpath(__file__))
        query_path = os.path.join(directory_path, directory, file_name)

        with open(query_path) as file:
            return file.read()

    def run_queries(self, query):
        """
        Method to run graphql queries
        Parameters: query - dict of graphql query and variables
        Returns: json string
        """
        has_next_page, allow_retry = True, True
        end_cursor = None
        data = []

        while has_next_page:
            print('retrieving data...')

            response = requests.post(url='https://api.github.com/graphql', json=query, headers=self.headers)
            status_code = response.status_code
            response_reason = response.reason
            response_json = response.json()

            if status_code != 200 and status_code != 403 and status_code != 502:
                raise requests.HTTPError('{}: {} {}'.format(status_code, response_reason, response_json))

            if status_code == 403:
                # Rate limit
                # Exception is not thrown to allow partially collected data to be exported
                print('Retrieval of all data failed: {} {} {}'.format(status_code, response_reason, response_json))
                break

            elif status_code == 502:
                # Bad Gateway results are resolved after trying the same request once more
                # Exception is not thrown to allow retry once and to allow partially collected data to be exported
                if allow_retry:
                    print('retrying with cursor: {}'.format(end_cursor))
                    allow_retry = False
                else:
                    print('Retrieval of all data failed: {} {} {}'.format(status_code, response_reason, response_json))
                    has_next_page = False

            else:
                if query['query'] == self.query_repos:
                    org_repos = response_json['data']['organization']['repositories']
                    page_info = org_repos['pageInfo']
                    nodes = org_repos['nodes']
                else:
                    repo_pull_requests = response_json['data']['repository']['pullRequests']
                    page_info = repo_pull_requests['pageInfo']
                    nodes = repo_pull_requests['nodes']

                end_cursor = page_info['endCursor']
                has_next_page = page_info['hasNextPage']

                variables = query['variables']
                variables['cursor'] = end_cursor
                query = {'query': query['query'], 'variables': variables}

                data += nodes
                allow_retry = True
        return data

    def list_of_comments(self, comments):
        """
        Method to form a list of json strings representing comments, reviews, or issue.
        Parameters: comments - list of comments
        Returns: List of json strings
        """
        list_comments = []

        # Iterate over each comment
        for comment in comments:
            comment_user = comment.get("author").get("login", None) if comment.get("author") is not None else None

            # Record reactions if Flag is True
            if self.reaction_flag:
                reactions = []
                raw_reactions = comment.get("reactions").get("nodes", None) if comment.get(
                    "reactions") is not None else []

                for reaction in raw_reactions:
                    reaction_user = reaction.get("user").get("login", None) if reaction.get(
                        "user") is not None else None

                    # Extract information regarding each reaction
                    reactions.append({"Content": reaction.get("content", None),
                                      "Created_At": reaction.get("createdAt", None),
                                      "User": reaction_user})

                # Extract information regarding each comment
                list_comments.append({"Created_At": comment.get("createdAt", None),
                                      "User": comment_user,
                                      "Body": comment.get("body", None),
                                      "Updated_At": comment.get("updatedAt", None),
                                      "Reactions": reactions})
            else:
                list_comments.append({"Created_At": comment.get("createdAt", None),
                                      "User": comment_user,
                                      "Body": comment.get("body", None),
                                      "Updated_At": comment.get("updatedAt", None)})
        return list_comments

    def get_pull_features(self, pull):
        """
        Method to get all data for a particular pull. Parameters: pull - object representing a pull
        Returns: dictionary containing all data of a pull
        """
        comments = pull.get('comments').get('nodes', None) if 'comments' in pull else None
        reviews = pull.get("reviews").get("nodes", None) if "reviews" in pull else None

        return {
            'Number': pull.get('number', None),
            'Title': pull.get('title', None),
            'User': pull.get('author').get('login', None) if pull.get('author') is not None else None,
            'URL': pull.get('url', None),
            'State': pull.get('state', None),
            'Body': pull.get('body', None),
            'Additions': pull.get('additions', None),
            'Deletions': pull.get('deletions', None),
            'Comments_Num': pull.get('comments').get('totalCount', None) if pull.get('comments') is not None else None,
            'Commits_Num': pull.get('comments').get('totalCount', None) if pull.get('commits') is not None else None,
            'Created_At': pull.get('createdAt', None),
            'Closed_At': pull.get('closedAt', None),
            'Merged': pull.get('merged', None),
            'Merged_At': pull.get('mergedAt', None),
            'Merged_By': pull.get('mergedBy').get('login', None) if pull.get('mergedBy') is not None else None,
            'Review_Comments_Num': pull.get('reviews').get('totalCount', None) if pull.get(
                'reviews') is not None else None,
            'Updated_At': pull.get('updatedAt'),
            'Comments': self.list_of_comments(comments) if comments is not None else [],
            "Review_Comments": self.list_of_comments(reviews) if reviews is not None else []
        }

    def retrieve_and_export_pull_request_data(self, repo, reactions_flag, name, organization):
        df = self.get_all_pull_requests(repo, reactions_flag)
        file_name = utils.construct_file_name(name, organization, repo)
        utils.export_to_cvs(df, file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create CSV/s for all pulls in repo/s')
    parser.add_argument('organization', help='Organization the repo belongs to.')
    parser.add_argument('-R', '--repo', help='Name of repo.')
    parser.add_argument('--reactions', action='store_true', default=False, help='Flag to extract reactions')
    parser.add_argument('-n', "--name",
                        help='Output file name. If not specified, the name is constructed like this: <organization>_<repo>.csv')

    args = parser.parse_args()
    ACCESS_TOKEN = os.environ["GITACCESS"]  # Access Github token from environment for security purposes
    extractor = GithubDataExtractor(ACCESS_TOKEN, args.organization)

    if args.repo is None:
        # Extract data for all repositories in organization
        repos = extractor.get_all_repos()
        for repo in repos:
            extractor.retrieve_and_export_pull_request_data(repo=repo, reactions_flag=args.reactions, name=None,
                                                            organization=args.organization)
    else:
        # Extract data for an individual repository
        extractor.retrieve_and_export_pull_request_data(repo=args.repo, reactions_flag=args.reactions, name=args.name,
                                                        organization=args.organization)
