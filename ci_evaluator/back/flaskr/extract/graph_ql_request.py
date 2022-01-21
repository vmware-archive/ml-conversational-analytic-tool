import requests
from flask import request

headers = {"Authorization": "Bearer {YOUR_ACCESS_TOKEN}"}

class MyQuery():
  def run_query(self, query): # A simple function to use requests.post to make the API call. Note the json= section.
      response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
      if response.status_code == 200:
          return response
      else:
          raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


  def pg_query(self, owner, name, whole_name, year):
    return  """
  {{
    repository(owner: {}, name: {}) {{
      name
      nameWithOwner
      owner{{
        login
      }}
    }}
    search(query: "repo:{} is:pr created:{}-01-01..{}-12-31", type: ISSUE, first: 10) {{
        nodes {{
          ... on PullRequest {{
            number
            title
            headRefOid
            author {{
              login
            }}
            labels(first: 2) {{
              nodes {{
                name
              }}
            }}
            url
            state
            additions
            deletions
            comments {{
              totalCount
            }}
            commits {{
              totalCount
            }}
            createdAt
            closedAt
            merged
            mergedAt
            mergedBy {{
              login
            }}
            reviews {{
              totalCount
            }}
            updatedAt
            comments {{
              nodes {{
                createdAt
                author {{
                  login
                }}
                updatedAt
                body
              }}
            }}
            reviews {{
              nodes {{
                createdAt
                author {{
                  login
                }}
                updatedAt
                body
                state
              }}
            }}
          }}
        }}
      }}
  }}
  """.format(f'"{owner}"', f'"{name}"', f'{whole_name}', f'{year}', f'{year}' )

  def pr_query(self, owner, name, pr_number):
    return  """
  {{
  repository(owner: {}, name: {}) {{
    name
    nameWithOwner
    owner{{
      login
    }}
    pullRequest(number: {}) {{
      number
        title
        headRefOid
       	author{{
          login
        }}
        labels(first: 2){{
          nodes{{
            name
          }}
        }}
        url
        state
        additions
        deletions
        comments{{
          totalCount
        }}
        commits{{
          totalCount
        }}
        createdAt
        closedAt
        merged
        mergedAt
        mergedBy{{
          login
        }}
        reviews{{
          totalCount
        }}
        updatedAt
        comments{{
          nodes{{
            createdAt
            author{{
              login
            }}
            updatedAt
            body
          }}
        }}
        reviews{{
          nodes{{
            createdAt
            author{{
              login
            }}
            updatedAt
            body
            state
          }}
        }}
    }}
  }}
}}
""".format(f'"{owner}"', f'"{name}"', f'{pr_number}')
