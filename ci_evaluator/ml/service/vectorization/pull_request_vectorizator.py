from datetime import datetime
import nlp
import pandas as pd
from sklearn.preprocessing import StandardScaler


class PullRequestVectorizator:

    def __init__(self):
        self.nlp = nlp.nlp()
        
        
    def getPRinfos(self, df) :
        pr_df = df.iloc[:,:22]
        pr_df = pr_df.drop_duplicates(subset=['PR_Number'])
        pr_df.sort_values(by=['PR_Created_At'], inplace=True, ascending=True)
        pr_df.index = [i for i in range(len(pr_df))]
        pr_df['PR_Title_and_Body'] = pr_df['PR_Title'].astype(str) + ' ' + pr_df['PR_Body'].astype(str)
        
        return pr_df
    
    
    def getFirstPRTmstmp(self, df) :
        dt = df['PR_Created_At'].loc[0]
        return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    
    
    def getPRcommentsLabels(self, df, pr_number) :
        temp = df.loc[df['PR_Number'] == pr_number]
        return temp[['Inclusiveness_Scale_1_to_10', 'Constructiveness_Scale_1_to_10']]
    
    
    def getPRFreqPerUser(self, df) :
        usersIDs_df = df['User']
        PRs_per_user = {}
        prfu = {}
        for PR_id in range(len(df)):
            user_id = usersIDs_df[PR_id]
            if PRs_per_user.get(user_id) == None:
                PRs_per_user[user_id] = 1
                prfu[str(PR_id)] = 1
            else:
                PRs_per_user[user_id] += 1
                prfu[str(PR_id)] = PRs_per_user[user_id]

        prfu_df = pd.DataFrame(columns=['PR_freq_per_user'])
        for PR_id in range(len(df)):
            prfu_df.loc[PR_id] = prfu[str(PR_id)]

        return prfu_df
    
    
    def getTimesBetwPRs(self, pr_df) :
        first_PR_ts = self.getFirstPRTmstmp(pr_df)
        PR_timestamps_df = pr_df['PR_Created_At']
        
        times_since_last_PR = {}
        for PR_id in range(len(pr_df)) :
            if PR_id == 0 :
                times_since_last_PR[str(PR_id)] = 0
            else :
                PR_dt = datetime.strptime(PR_timestamps_df[PR_id], '%Y-%m-%d %H:%M:%S')
                prev_PR_dt = datetime.strptime(PR_timestamps_df[PR_id-1], '%Y-%m-%d %H:%M:%S')
                diff = (PR_dt - prev_PR_dt).total_seconds()
                if diff < 0 : diff = 0
                times_since_last_PR[str(PR_id)] = diff

        times_df = pd.DataFrame(columns=['times_since_prev_PR'])
        for PR_id in range(len(pr_df)) :
            times_df.loc[PR_id] = times_since_last_PR[str(PR_id)]

        return times_df
    
    
    def getTimesBetween(self, pr_df, feature1, feature2) :
        temp = {}
        for item in range(len(pr_df)) :
            if type(pr_df[feature1][item]) == str and type(pr_df[feature2][item]) == str :    
                time1 = datetime.strptime(pr_df[feature1][item], '%Y-%m-%d %H:%M:%S')
                time2 = datetime.strptime(pr_df[feature2][item], '%Y-%m-%d %H:%M:%S')

                diff = (time1 - time2).total_seconds()
                if diff < 0 : diff = 0
                temp[str(item)] = diff
            else :
                temp[str(item)] = None

        times_df = pd.DataFrame(columns=['Time_between_' + feature1 + '_and_' + feature2])
        for item in range(len(pr_df)) :
            times_df.loc[item] = temp[str(item)]

        return times_df
    
    
    def getICdistrDiscriminatives(self, df, pr_df) :
        dist_dicriminative_infos = ['I_mean', 'I_std', 'I_min', 'I_25%', 'I_50%', 'I_75%', 'I_max', 
                            'I_var', 'I_mode', 'C_mean', 'C_std', 'C_min', 'C_25%', 'C_50%', 
                            'C_75%', 'C_max', 'C_var', 'C_mode']

        IC_dist_discriminatives_df = pd.DataFrame(columns=dist_dicriminative_infos)
        
        IC_dist_discriminatives = {}
        for pr_id in range(len(pr_df)) :
            IC_dist_discriminatives[pr_id] = []

            pr_comments_labels = self.getPRcommentsLabels(df, pr_df['PR_Number'][pr_id])
            info = pr_comments_labels.describe()

            for i in info.index[1:] :
                IC_dist_discriminatives[pr_id].append(info.loc[i]['Inclusiveness_Scale_1_to_10'])
            IC_dist_discriminatives[pr_id].append(pr_comments_labels['Inclusiveness_Scale_1_to_10'].var())
            IC_dist_discriminatives[pr_id].append(pr_comments_labels['Inclusiveness_Scale_1_to_10'].mode())
            for i in info.index[1:] :
                IC_dist_discriminatives[pr_id].append(info.loc[i]['Constructiveness_Scale_1_to_10'])
            IC_dist_discriminatives[pr_id].append(pr_comments_labels['Constructiveness_Scale_1_to_10'].var())
            IC_dist_discriminatives[pr_id].append(pr_comments_labels['Constructiveness_Scale_1_to_10'].mode())


        for pr_id in range(len(pr_df)) :
            IC_dist_discriminatives_df.loc[pr_id] = IC_dist_discriminatives[pr_id]
            
        return IC_dist_discriminatives_df
    
        
    def vectorize(self, df) :    
        self.pr_df = self.getPRinfos(df)
        
        tfidfs_df = self.nlp.getTFIDFs(self.pr_df['PR_Title_and_Body'])
        sa_df = self.nlp.getSentimentalAnalisys(self.pr_df['PR_Title_and_Body'])
        prfu_df = self.getPRFreqPerUser(self.pr_df)
        times_btw_df = self.getTimesBetwPRs(self.pr_df)
        
        tbcc_df = self.getTimesBetween(self.pr_df, 'PR_Closed_At', 'PR_Created_At')
        tbcc_df.columns = ['time_between_creation_and_closing']
        
        others_df = self.pr_df[['PR_Number', 'PR_State', 'PR_Additions', 'PR_Deletions', 
                          'PR_Comments_Num', 'PR_Commits_Num', 'PR_Merged', 'PR_Review_Comments_Num']]

        others_df['PR_State'].replace('open', 0, inplace=True)
        others_df['PR_State'].replace('closed', 1, inplace=True)
        others_df['PR_Merged'].replace(False, 0, inplace=True)
        others_df['PR_Merged'].replace(True, 1, inplace=True)
        
        IC_dist_discriminatives_df = self.getICdistrDiscriminatives(df, self.pr_df)
        
        temp_df = pd.concat([tfidfs_df, prfu_df, times_btw_df, tbcc_df, others_df], axis=1)
        scaled_temp = StandardScaler().fit_transform(temp_df)
        scaled_temp_df = pd.DataFrame(scaled_temp, columns=temp_df.columns)
        vectors_df = pd.concat([scaled_temp_df, sa_df, IC_dist_discriminatives_df], axis=1)
        
        return vectors_df