import pandas as pd


def run():
    file_1_name = 'file_1.csv'
    file_2_name = 'file_2.csv'

    file_1 = pd.read_csv(file_1_name, header=None)
    file_2 = pd.read_csv(file_2_name, header=None)
    empty_dataframe = pd.DataFrame({'':['', '']})

    merged = pd.concat([file_1, empty_dataframe, file_2])
    merged.to_csv("output.csv", header=None, index=None)