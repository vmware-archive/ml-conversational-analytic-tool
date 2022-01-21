#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import json
import re
import ast


class DataFormatting():
    def format_pr(self, json_obj):
        # pr = pd.DataFrame(json_obj)
        pr = json_obj
        pr_data = []
        pr_body = None
        for index, row in pr.iterrows():
            if index == 0:
                json_pr = row[1] # Get data from row
                json_pr = ast.literal_eval(json_pr)

                # PR Data
                repo = json_pr['name']
                org = json_pr['owner']['login']

                d = json_pr['pullRequest']

                number = d['number']
                title = d['title']
                headRef = d['headRefOid']
                user = d['author']['login']
                labels = d['labels']['nodes']
                url = d['url']
                state = d['state']
                additions = d['additions']
                deletions = d['deletions']
                numComments = d['comments']['totalCount']
                numCommits = d['commits']['totalCount']
                createdAt = (re.sub("[A-X]", " ", d['createdAt'])[:-1] if d['createdAt'] else None)
                closedAt = (re.sub("[A-X]", " ", d['closedAt'])[:-1] if d['closedAt'] else None)
                merged = d['merged']
                mergedAt = (re.sub("[A-X]", " ", d['mergedAt'])[:-1] if d['mergedAt'] else None)
                updatedAt = (re.sub("[A-X]", " ", d['updatedAt'])[:-1] if d['updatedAt'] else None)
                mergedBy = (d['mergedBy']['login'] if d['mergedBy'] else None)
                numReviews = d['reviews']['totalCount']

                # Comment Data
                if numComments:
                    for i in range(numComments):
                        c = d['comments']['nodes'][i]
                        cAuthor = c['author']['login']
                        cCreatedAt = (re.sub("[A-X]", " ", c['createdAt'])[:-1] if c['createdAt'] else None)
                        cUpdatedAt = (re.sub("[A-X]", " ", c['updatedAt'])[:-1] if c['updatedAt'] else None)
                        cBody = c['body']

                        pr_data.append([repo, org, number, title, headRef, user, labels, url, state, pr_body,
                                          additions, deletions, numComments, numCommits, createdAt, closedAt, 
                                          merged, mergedAt, mergedBy, numReviews, updatedAt, "FALSE",
                                          cCreatedAt, cAuthor, cUpdatedAt, cBody])

                # Review Data
                if numReviews:
                    for i in range(numReviews):
                        r = d['reviews']['nodes'][i]
                        rAuthor = r['author']['login']
                        rCreatedAt = (re.sub("[A-X]", " ", r['createdAt'])[:-1] if r['createdAt'] else None)
                        rUpdatedAt = (re.sub("[A-X]", " ", r['updatedAt'])[:-1] if r['updatedAt'] else None)
                        rBody = r['body']

                        pr_data.append([repo, org, number, title, headRef, user, labels, url, state, pr_body,
                                          additions, deletions, numComments, numCommits, createdAt, closedAt, 
                                          merged, mergedAt, mergedBy, numReviews, updatedAt, "TRUE",
                                          rCreatedAt, rAuthor, rUpdatedAt, rBody])
        
        formatted_pr = pd.DataFrame(pr_data, columns = ["Repo_Name", "Organization_Name", "PR_Number", "PR_Title", "PR_Head", "User", "PR_Labels", "URL", "PR_State", "PR_Body", 
                                              "PR_Additions", "PR_Deletions", "PR_Comments_Num", "PR_Commits_Num", "PR_Created_At", "PR_Closed_At", 
                                              "PR_Merged", "PR_Merged_At", "PR_Merged_By", "PR_Review_Comments_Num", "PR_Updated_At", "Review_Comment", 
                                              "Comment_Created_At", "Comment_User", "Comment_Updated_At", "Comment"])
        return formatted_pr

        
    def format_project(self, json_obj):
        dd = pd.DataFrame(json_obj)
        full_data = [] # List of lists to be used to create model input dataframe

        repo = ""
        org = ""
        pr_body = None # Not found in the data
        for index, row in dd.iterrows(): # Iterate through the df rows
            if index == 0: # Select 'repository' row (i.e. repository JSON)
                json_repository = row[1] # Get data from row
                json_repository = ast.literal_eval(json_repository)
                
                repo = json_repository['name']
                org = json_repository['owner']['login']
            elif index == 1: # Select 'search' row (i.e. search JSON)
                json_search = row[1] # Get data from row
                json_search = ast.literal_eval(json_search)
                for i in range(len(json_search['nodes']) - 1):
                    d = json_search['nodes'][i]

                    # PR Data
                    number = d['number']
                    title = d['title']
                    headRef = d['headRefOid']
                    user = d['author']['login']
                    labels = d['labels']['nodes']
                    url = d['url']
                    state = d['state']
                    additions = d['additions']
                    deletions = d['deletions']
                    numComments = d['comments']['totalCount']
                    numCommits = d['commits']['totalCount']
                    createdAt = (re.sub("[A-X]", " ", d['createdAt'])[:-1] if d['createdAt'] else None)
                    closedAt = (re.sub("[A-X]", " ", d['closedAt'])[:-1] if d['closedAt'] else None)
                    merged = d['merged']
                    mergedAt = (re.sub("[A-X]", " ", d['mergedAt'])[:-1] if d['mergedAt'] else None)
                    updatedAt = (re.sub("[A-X]", " ", d['updatedAt'])[:-1] if d['updatedAt'] else None)
                    mergedBy = (d['mergedBy']['login'] if d['mergedBy'] else None)
                    numReviews = d['reviews']['totalCount']

                    # Comment Data
                    if numComments:
                        for i in range(numComments):
                            c = d['comments']['nodes'][i]
                            cAuthor = c['author']['login']
                            cCreatedAt = (re.sub("[A-X]", " ", c['createdAt'])[:-1] if c['createdAt'] else None)
                            cUpdatedAt = (re.sub("[A-X]", " ", c['updatedAt'])[:-1] if c['updatedAt'] else None)
                            cBody = c['body']

                            full_data.append([repo, org, number, title, headRef, user, labels, url, state, pr_body,
                                              additions, deletions, numComments, numCommits, createdAt, closedAt, 
                                              merged, mergedAt, mergedBy, numReviews, updatedAt, "FALSE",
                                              cCreatedAt, cAuthor, cUpdatedAt, cBody])

                    # Review Data
                    if numReviews:
                        for i in range(numReviews):
                            r = d['reviews']['nodes'][i]
                            rAuthor = r['author']['login']
                            rCreatedAt = (re.sub("[A-X]", " ", r['createdAt'])[:-1] if r['createdAt'] else None)
                            rUpdatedAt = (re.sub("[A-X]", " ", r['updatedAt'])[:-1] if r['updatedAt'] else None)
                            rBody = r['body']

                            full_data.append([repo, org, number, title, headRef, user, labels, url, state, pr_body,
                                              additions, deletions, numComments, numCommits, createdAt, closedAt, 
                                              merged, mergedAt, mergedBy, numReviews, updatedAt, "TRUE",
                                              rCreatedAt, rAuthor, rUpdatedAt, rBody])
            
        formatted_project = pd.DataFrame(full_data, columns = ["Repo_Name", "Organization_Name", "PR_Number", "PR_Title", "PR_Head", "User", "PR_Labels", "URL", "PR_State", "PR_Body", 
                                              "PR_Additions", "PR_Deletions", "PR_Comments_Num", "PR_Commits_Num", "PR_Created_At", "PR_Closed_At", 
                                              "PR_Merged", "PR_Merged_At", "PR_Merged_By", "PR_Review_Comments_Num", "PR_Updated_At", "Review_Comment", 
                                              "Comment_Created_At", "Comment_User", "Comment_Updated_At", "Comment"])
        return formatted_project





