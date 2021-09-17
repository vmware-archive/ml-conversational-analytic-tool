# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import argparse
import os

from githubDataExtraction import GithubDataExtractor


def getRepos(access_token, organization, reaction):
    """
    Method to extract data for all repositories in organization
    """
    extractor = GithubDataExtractor(access_token)  # Create object
    repos = extractor.g_ses.get_organization(organization).get_repos()
    for repo in repos:
        print("Starting: {}".format(repo.name))
        extractor.openRepo(organization, repo.name)
        extractor.getAllPulls("", reaction)


def getRepo(access_token, organization, reponame, reaction):
    """
    Method to extract data for an individual repository
    """
    extractor = GithubDataExtractor(access_token)  # Create object 
    extractor.openRepo(organization, reponame)
    extractor.getAllPulls("", reaction)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create csv for all pulls in each repo for the organzation')
    parser.add_argument('organization', help='Organization the repo belongs to.')
    parser.add_argument('repo', help='Repo name or all if all repos in organization')
    parser.add_argument('-reactions', action='store_true', default=False, help='Flag to extract reactions')

    args = parser.parse_args()
    ACCESS_TOKEN = os.environ["GITACCESS"]  # Access Github token from environment for security purposes
    if args.repo == 'all':
        getRepos(ACCESS_TOKEN, args.organization, args.reactions)
    else:
        getRepo(ACCESS_TOKEN, args.organization, args.repo, args.reactions)
