import pandas as pd


def read_csv(name):
    return pd.read_csv(name, delimiter=',')
    
def combine_two_dataset_rows(dataset1, dataset2):
    df = pd.concat([dataset1, dataset2])
    df.reset_index(inplace=True, drop=True)
    return pd.DataFrame(df)
    
def save_dataset_as_csv(dataset, name):
    dataset.to_csv(name)

def combine_and_clean(df1name, df2name):
    df1 = read_csv(df1name)
    df2 = read_csv(df2name)
    df = combine_two_dataset_rows(df1, df2)
    df.drop(['Unnamed: 0','Index'], axis=1, inplace=True)
    df = set_three_label_input(df)
    save_dataset_as_csv(df, 'test.csv')
    return pd.DataFrame(df)

def set_three_label_input(df):
    df.rename(columns={"Inclusiveness_5_Categories": "Inclusiveness", "Constructiveness_5_Categories": "Constructiveness"}, inplace=True)
    df_ic = pd.DataFrame(df['Inclusiveness'])
    df_ic['Constructiveness'] = df['Constructiveness']
    df.drop(columns=['Inclusiveness_Scale_1_to_10', 'Inclusiveness_2_Categories', 'Constructiveness_Scale_1_to_10', 'Constructiveness_2_Categories', 'Constructiveness', 'Inclusiveness'], inplace=True)
    
    df_ic.replace(['somewhat inclusive', 'somewhat inclusive ', 'inclusive '], 'inclusive', inplace=True)
    df_ic.replace(['somewhat not inclusive', 'somewhat not inclusive '], 'not inclusive', inplace=True)
    df_ic.replace(['somewhat constructive', 'somewhat constructive ', 'ssomewhat constuctive', 'constructive ', 'somewhat constuctive'], 'constructive', inplace=True)
    df_ic.replace(['somewhat not constructive', 'somewhat not constructive '], 'not constructive', inplace=True)
    df_ic.replace(['netrual', 'netural', 'neutral', 'neutral '], 'neutral', inplace=True)
    
    df['Inclusiveness'] = df_ic['Inclusiveness']
    df['Constructiveness'] = df_ic['Constructiveness']
    return pd.DataFrame(df)

def combine_two_datasets_by_column(df1, df2):
    return pd.DataFrame(pd.concat([df1, df2], axis=1))


if __name__ == '__main__':
    df1 = read_csv('example_one_with_labels.csv')
    df2 = read_csv('example_two_with_labels.csv')
    df = combine_two_dataset_rows(df1, df2)
    df.drop(['Unnamed: 0','Index'], axis=1, inplace=True)
    df_final = set_three_label_input(df)
    print(df_final.tail())
    save_dataset_as_csv(df_final, 'combined_data.csv')
