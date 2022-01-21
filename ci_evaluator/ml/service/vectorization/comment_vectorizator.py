from datetime import datetime
from .nlp import NLP
import pandas as pd
from sklearn.preprocessing import StandardScaler


class CommentVectorizator:

    def __init__(self):
        self.nlp = NLP()

        
    def getCommentFreqPerUser(self, df):
        usersIDs_df = df['Comment_User']
        comments_per_user = {}
        cfu = {}
        for comm_id in range(len(df)):
            user_id = usersIDs_df[comm_id]
            if comments_per_user.get(user_id) == None:
                comments_per_user[user_id] = 1
                cfu[str(comm_id)] = 1
            else:
                comments_per_user[user_id] += 1
                cfu[str(comm_id)] = comments_per_user[user_id]

        cfu_df = pd.DataFrame(columns=['comment_freq_per_user'])
        for comm_id in range(len(df)):
            cfu_df.loc[comm_id] = cfu[str(comm_id)]

        return cfu_df

    
    def getTimeBetwComments(self, df):
        comm_timestamps_df = df['Comment_Created_At']
        times = {}
        for comm_id in range(len(df)):
            if comm_id == 0 or (df['PR_Number'][comm_id] != df['PR_Number'][comm_id-1]) :
                times[str(comm_id)] = 0
            else:
                comm_dt = datetime.strptime(comm_timestamps_df[comm_id], '%Y-%m-%d %H:%M:%S')
                prev_comm_dt = datetime.strptime(comm_timestamps_df[comm_id - 1], '%Y-%m-%d %H:%M:%S')
                diff = (comm_dt - prev_comm_dt).total_seconds()
                if diff < 0: diff = 0
                times[str(comm_id)] = diff

        times_df = pd.DataFrame(columns=['times_since_last_comment'])
        for comm_id in range(len(df)):
            times_df.loc[comm_id] = times[str(comm_id)]

        return times_df

    
    def vectorize(self, df):
        comments_df = df['Comment']

        times_df = self.getTimeBetwComments(df)
        cfu_df = self.getCommentFreqPerUser(df)
        tfidfs_df = self.nlp.getTFIDFs(comments_df)
        sentiment_df = self.nlp.getSentimentalAnalisys(comments_df)

        df['Review_Comment'].replace('TRUE', 1, inplace=True)
        df['Review_Comment'].replace('FALSE', 0, inplace=True)
        rev_df = df['Review_Comment']

        temp_df = pd.concat([tfidfs_df, rev_df, cfu_df, times_df], axis=1)
        scaled_temp = StandardScaler().fit_transform(temp_df)
        scaled_temp_df = pd.DataFrame(scaled_temp, columns=temp_df.columns)
        vectors_df = pd.concat([scaled_temp_df, sentiment_df], axis=1)

        return vectors_df



