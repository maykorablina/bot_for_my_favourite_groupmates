import pandas as pd
from io import BytesIO
import requests
import time


def get_timetable(key):
    # получаем гугл таблицу в качестве датафрейма
    r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={key}&output=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data))
    # заполняем ячейки, где пропущены дни недели
    df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')
    # лекции и семинары записаны в объединенных ячейках, и тут мы заполняем нужные ячейки инфой о лекциях и о семинарах (лекции заполняются для всего потока, семинары только для нашей группы)\
    # потому что бот только для нашей группы!!!
    for index, row in df.iterrows():
        target = str(list(row)[2]).lower()
        if 'lecture' in target:
            df.iloc[index, :] = df.iloc[index, :].fillna(method='ffill', axis=0)
    # поскольку мы делаем бота пока что только для нашей группы, я обрезаю датафрейм и оставляю только наши две подгруппы
    # в дальнейшем это несложно будет поменять
    df = df.iloc[:, [0, 1, 6, 7]]
    for index, row in df.iterrows():
        target = str(row[2]).lower()
        if 'seminar' in target:
            df.iloc[index, :] = df.iloc[index, :].fillna(method='ffill', axis=0)
    # df_233_2 = df.iloc[[1:]:, [0, 1, 3]]
    # тут обрезаем нулевой столбец и переименовываем колонки
    df = df.iloc[1:]
    df.columns = ['day', 'timeslot', '233_1', '233_2']
    return df


def get_rows_as_lists(df):
    # здесь просто делаем из датафрейма список из строк
    l = []
    for _, row in df.iterrows():
        l.append(list(row))
    return l


def check_on_updates(df_base, df_temp):
    # здесь df_temp - это старое расписание, df_temp - новое расписание, которое мы проверяем на обновления
    df_base_rows = get_rows_as_lists(df_base)
    df_temp_rows = get_rows_as_lists(df_temp)
    days_changed = []
    group_changed = []
    # здесь мы с помощью цикла идем по строкам обоих списков (которые из датафреймов)
    # и сравниваем их между собой, для этого и нужно было преобразование дф-ов в списки, так сравнение идет проще и быстрее
    for row in range(len(df_base_rows)):
        # если строки из df_base и df_temp не равны, т.е. Подивилова поменяла расписание, то тогда мы добавляем в
        # days_changed название дня недели, а в groups_changed - название группы

        if df_base_rows[row] != df_temp_rows[row]:
            days_changed.append(df_temp_rows[row][0])
            for j in range(len(df_base_rows[row])):
                if df_base_rows[row][j] != df_temp_rows[row][j]:
                    group_changed.append(df_temp.columns[j])
    # тут смотрим, было ли изменение у конкретно нашей группы
    # в дальнейшем здесь можно будет смотреть расписание для всех групп, лекции в гугл таблице заполнены сразу для всех групп, а про семинары я уже выше писала
    if '233_2' in group_changed:
        # print(f'ИЗМЕНЕНИЕ В РАСПИСАНИИ У ГРУПП {list(set(group_changed))}')
        new_day_table = df_temp[df_temp['day'].isin(days_changed)][['day', 'timeslot', '233_2']]
        # если измения есть, то мы возвращаем список из датафрейма, отфильтрованного по группе и по дням недели
        return get_rows_as_lists(new_day_table)
    # если ничего не изменилось, возвращаем просто датафрейм
    return df_temp_rows
