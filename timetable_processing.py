import pandas as pd
from io import BytesIO
import requests


def get_timetable(key):
    r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={key}&output=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data))  # .fillna(method='ffill', axis=1)
    df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')
    for index, row in df.iterrows():
        target = str(list(row)[2]).lower()
        if 'lecture' in target:
            df.iloc[index, :] = df.iloc[index, :].fillna(method='ffill', axis=0)
    df = df.iloc[:, [0, 1, 6, 7]]
    for index, row in df.iterrows():
        target = str(row[2]).lower()
        if 'seminar' in target:
            df.iloc[index, :] = df.iloc[index, :].fillna(method='ffill', axis=0)
    # df_233_2 = df.iloc[[1:]:, [0, 1, 3]]
    df = df.iloc[1:]
    df.columns = ['day', 'timeslot', '233_1', '233_2']
    return df


def get_rows_as_lists(df):
    l = []
    for _, row in df.iterrows():
        l.append(list(row))
    return l


def check_on_updates(df_base, df_temp):
    # df_base = get_timetable(key=key)
    # df_temp = get_timetable(key=key)
    df_base_rows = get_rows_as_lists(df_base)
    df_temp_rows = get_rows_as_lists(df_temp)
    days_changed = []
    group_changed = []
    for row in range(len(df_base_rows)):
        if df_base_rows[row] != df_temp_rows[row]:
            days_changed.append(df_temp_rows[row][0])
            for j in range(len(df_base_rows[row])):
                if df_base_rows[row][j] != df_temp_rows[row][j]:
                    group_changed.append(df_temp.columns[j])

            # print('ИЗМЕНЕНИЕ В РАСПИСАНИИ')
            # df_base = df_temp.copy()
            # new_day_table = df_temp[df_temp['day'] == df_temp_rows[row][0]]
            # print(new_day_table)
    if len(days_changed) > 0:
        print(f'ИЗМЕНЕНИЕ В РАСПИСАНИИ У ГРУПП {list(set(group_changed))}')
        new_day_table = df_temp[df_temp['day'].isin(days_changed)]
        print(new_day_table)
        df_base = df_temp.copy()
        return new_day_table

#
# class Timetable:
#     def __init__(self, key):
#         r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={key}&output=csv')
#         self.df = pd.read_csv(BytesIO(r.content))  # .fillna(method='ffill', axis=1)
#         self.df.iloc[:, 0] = self.df.iloc[:, 0].fillna(method='ffill')
#         for index, row in self.dfdf.iterrows():
#             target = str(row[2]).lower()
#             if 'lecture' in target:
#                 self.df.iloc[index, :] = self.df.iloc[index, :].fillna(method='ffill', axis=0)
#         self.df = self.df.iloc[:, [0, 1, 6, 7]]
#         for index, row in self.df.iterrows():
#             target = str(row[2]).lower()
#             if 'seminar' in target:
#                 self.df.iloc[index, :] = self.df.iloc[index, :].fillna(method='ffill', axis=0)
#         # df_233_2 = df.iloc[[1:]:, [0, 1, 3]]
#         self.df = self.df.iloc[1:]
#         self.df.columns = ['day', 'timeslot', '233_1', '233_2']
#         self.df_previous_version = self.df.copy()
#
#     def get_dataframe(self):
#         return self.df
#
#     def get_rows_as_lists(self):
#         l = []
#         for _, row in self.df.iterrows():
#             l.append(list(row))
#         return l
#
#     def check_on_updates(self):
#
# def check_on_updates(df_base, df_temp):
#     df_base_rows = get_rows_as_lists(df_base)
#     df_temp_rows = get_rows_as_lists(df_temp)
#     for row in range(len(df_base_rows)):
#         if df_base_rows[row] != df_temp_rows[row]:
#             print('ИЗМЕНЕНИЕ В РАСПИСАНИИ')
#             df_base = df_temp.copy()
#             new_day_table = df_temp[df_temp['day'] == df_temp_rows[row][0]]
#             print(new_day_table)
#             return df_base
#     return df_base
