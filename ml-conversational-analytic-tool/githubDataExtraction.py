# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import time

import argparse
import pandas as pd
from github import Github
from github.GithubException import RateLimitExceededException


class GithubDataExtractor:
    def __init__(self, access_token):
        """
        Constructor requires an access token to start a Github session, and specifies instance variables
        """
        self.g_ses = Github(access_token)  # Github object is used as a channel to the Github API
        self.current_repo = None  # Current Opended Repo
        self.reaction_flag = False
        self.repo_opened = False  # Flag to store state of repo as opened (True) or closed (False)
        self.repo_name = ""
        self.organization = ""

    def openRepo(self, organization, repo_name):
        """
        Method to  open (access) repository with given organization and repository name (reponame).
        Parameters: username - owner of the repository, repo_name - name of repo to be opened
        """
        self.current_repo = self.g_ses.get_repo(organization + "/" + repo_name)  # Open repo
        self.repo_opened = True
        self.repo_name = repo_name
        self.organization = organization
        print("Opened repo {} - {}".format(repo_name, organization))

    def getAllPulls(self, name="", reaction_flag=False, export_to_csv=True):
        """
        Method to form a dataframe containing pull information. Parameters: name - name of exported csv file,
        export - if the dataframe should be exported to csv. Returns: Dataframe with pull data
        """
        self.reaction_flag = reaction_flag
        if self.repo_opened:  # Verify if a repo has been opened
            pull_data = []
            pull_data.extend(self.getPullsByState('open'))  # Access all open pulls
            pull_data.extend(self.getPullsByState('closed'))  # Access all closed pulls
            pull_df = pd.DataFrame(pull_data)  # Convert list of dictionaries to dataframe
            if export_to_csv:  # Export to csv if flag is true
                if not os.path.exists('exports'):
                    os.mkdir('exports')
                if name == "":  # Check if name is provided
                    pull_df.to_csv("exports/" + self.organization + "_" + self.repo_name + ".csv")
                else:
                    pull_df.to_csv("exports/" + name)
            return pull_df
        print("Please open a Repo")

    def getPullsByState(self, state):
        """
        Extract pulls with given state. Parameters: state - state of the pull (open or closed)
        Return: list of dictionaries containing data regardining each pull
        """
        pull_data = []
        try:  # Call the Github api to get all pulls
            pulls = self.current_repo.get_pulls(state=state, sort='create')
        except RateLimitExceededException as e:  # If token has reached limit
            print("Token rate limit exceeded. Waiting for 1 hour", e)
            time.sleep(60 * 60)  # Wait for 1 hour (time required to reset)
            pulls = self.current_repo.get_pulls(state=state, sort='create')  # Get all pulls from Github API again
        # Iterate over each pull
        for pull in pulls:
            try:  # Call to extract features for each pull
                pull_data.append(self.getPullFeatures(pull))
            except RateLimitExceededException as e:  # getPullFeatures accesses the Github API so provisino for rate limit
                print("Token rate limit exceeded. Waiting for 1 hour", e)
                time.sleep(60 * 60)
                pull_data.append(self.getPullFeatures(pull))
        return pull_data

    def listOfComments(self, comments):
        """
        Method to form a list of json strings rerpesenting comments (reviews or issue).
        Parameters: comments - list of comment objects. Returns: List of json strings
        """
        list_comments = []

        # Iterate over each comment
        for comment in comments:
            # Record reactions if Flag is True
            if self.reaction_flag:
                reactions = []
                raw_reactions = []

                try:  # Call to extract all raw reactions
                    raw_reactions = comment.get_reactions()
                except RateLimitExceededException as e:  # get_reactions accesses the Github API so provisino for rate limit
                    print("Token rate limit exceeded. Waiting for 1 hour", e)
                    time.sleep(60 * 60)
                    raw_reactions = comment.get_reactions()

                for reaction in raw_reactions:
                    # Extract information regarding each reaction
                    try:
                        reactions.append((reaction.content, str(reaction.created_at), reaction.user.name))
                    except:
                        reactions.append((reaction.content, str(reaction.created_at), None))

                # Extract information regarding each comment
                try:
                    list_comments.append(
                        str({"Created_At": str(comment.created_at), "User": comment.user.name, "Body": comment.body,
                             "Updated_At": str(comment.updated_at), "Reactions": reactions}))
                except:
                    list_comments.append(str({"Created_At": str(comment.created_at), "User": None, "Body": comment.body,
                                              "Updated_At": str(comment.updated_at), "Reactions": reactions}))
            else:
                try:
                    list_comments.append(
                        str({"Created_At": str(comment.created_at), "User": comment.user.name, "Body": comment.body,
                             "Updated_At": str(comment.updated_at)}))
                except:
                    list_comments.append(str({"Created_At": str(comment.created_at), "User": None, "Body": comment.body,
                                              "Updated_At": str(comment.updated_at)}))
        return list_comments

    def getPullFeatures(self, pull):
        """
        Method to get all data for a particular pull. Parameters: pull - object representing a pull
        Returns: dictionary containing all data of a pull
        """
        pull_dict = {}
        pull_dict["Number"] = pull.number
        pull_dict["Title"] = pull.title
        try:
            pull_dict["User"] = pull.user.name
        except:
            pull_dict["User"] = None
        pull_dict["URL"] = pull.url
        pull_dict["State"] = pull.state
        pull_dict["Body"] = pull.body
        pull_dict["Additions"] = pull.additions
        pull_dict["Deletions"] = pull.deletions
        pull_dict["Comments_Num"] = pull.comments
        pull_dict["Commits_Num"] = pull.commits
        pull_dict["Created_At"] = pull.created_at
        pull_dict["Closed_At"] = pull.closed_at
        pull_dict["Merged"] = pull.merged
        pull_dict["Merged_At"] = pull.merged_at
        try:  # Attribute merged_by might be none if it has not been merged
            pull_dict["Merged_By"] = pull.merged_by.name
        except:  # If not merged then none
            pull_dict["Merged_By"] = None
        pull_dict["Review_Comments_Num"] = pull.review_comments
        pull_dict["Updated_At"] = pull.updated_at
        pull_dict["Comments"] = self.listOfComments(pull.get_issue_comments())
        pull_dict["Review_Comments"] = self.listOfComments(pull.get_review_comments())

        return pull_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create csv for all pulls in repo')
    parser.add_argument('organization', help='Organization the repo belongs to.')
    parser.add_argument('reponame', help='Name of repo')
    parser.add_argument('-reactions', action='store_true', default=False, help='Flag to extract reactions')
    parser.add_argument('--filename', help='Name of file')
    # parser.add_argument('accesstoken', help='Github access token')

    args = parser.parse_args()
    ACCESS_TOKEN = os.environ["GITACCESS"]  # Access Github token from environment for security purposes
    extractor = GithubDataExtractor(ACCESS_TOKEN)  # Create object
    extractor.openRepo(args.organization, args.reponame)  # Open repo

    # Extract all pulls and export them to .csv
    if args.filename:
        extractor.getAllPulls(args.filename, args.reactions)
    else:
        extractor.getAllPulls("", args.reactions)
