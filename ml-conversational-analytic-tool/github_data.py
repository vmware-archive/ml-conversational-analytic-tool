import argparse

import pandas as pd

import utils

FILE_NAME_SUFFIX = "unannotated"


class GitHubData:
    """
    Reformat raw data for annotation
    """

    def __init__(self, raw_filename):
        self.raw_filename = raw_filename
        self.raw_data = None

    def read_raw_data(self):
        """
        Function to read raw data stored as csv
        """
        self.raw_data = pd.read_csv(self.raw_filename)

        # Convert Comments and Review Comments to dictionary
        self.raw_data['Comments'] = self.raw_data['Comments'].apply(lambda comment: utils.string_to_dict(comment))
        self.raw_data['Review_Comments'] = self.raw_data['Review_Comments'].apply(lambda comment: utils.string_to_dict(comment))

    def reformat_data(self):
        """
        Function to reformat raw data as form conversation strings given communication on a pull requests
        """

        # Store each interaction and pull URL for export
        conversations = []
        pull_urls = []
        pull_numbers = []

        for index, row in self.raw_data.iterrows():
            # Make pull message
            conversations.append(self.merge_comments(row))
            pull_urls.append(row["URL"])
            pull_numbers.append(row["Number"])

        # Export conversation field dataset
        export_df = pd.DataFrame()
        export_df["Number"] = pull_numbers
        export_df["URL"] = pull_urls
        export_df["Thread"] = conversations
        return export_df

    def merge_comments(self, row):
        """
        merge comments and review comments to form a conversation
        """
        conversation = "{} ({}) : {}\n{}".format(row["User"], row["Created_At"], row["Title"], row["Body"])
        temp_df_comments = pd.DataFrame(row['Comments'])
        temp_df_review_comments = pd.DataFrame(row["Review_Comments"])
        if len(temp_df_comments) > 0 or len(temp_df_review_comments) > 0:
            all_comments = temp_df_comments.append(temp_df_review_comments)
            all_comments['Created_At'] = pd.to_datetime(all_comments['Created_At'])
            all_comments = all_comments.sort_values(by=['Created_At'])  # Sort data so as to export in order

            for comment_index, comment_row in all_comments.iterrows():
                conversation = conversation + "\n{} ({}) : {}".format(comment_row["User"],
                                                                      comment_row["Created_At"],
                                                                      comment_row["Body"])
        return conversation.encode("ascii", "ignore").decode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reformat raw data for annotation.')
    parser.add_argument('rawdatafile', help='Raw Data Filename')
    parser.add_argument('-n', '--name', required=False, help='Output file name. If not specified, the name is '
                                                             'constructed like this: <rawdatafile>{'
                                                             'suffix}.csv'.format(suffix=FILE_NAME_SUFFIX))
    args = parser.parse_args()

    data_reformat = GitHubData(args.rawdatafile)
    data_reformat.read_raw_data()

    df = data_reformat.reformat_data()
    file_name = utils.construct_file_name(args.name, args.rawdatafile, FILE_NAME_SUFFIX)
    utils.export_to_cvs(df, file_name)
