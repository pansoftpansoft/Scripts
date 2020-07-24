import sqlite3
import json
import os
import datetime

# import get_stat_user
db_p = ''


def db_path():
    global db_p
    if db_p == '':
        bot_name_list = os.getcwdb().decode('utf-8').split('\\')
        # print('bot_name = ' + bot_name_list[len(bot_name_list)-1])
        bot_name = bot_name_list[len(bot_name_list) - 1]
        dir = os.path.dirname(os.path.abspath(__file__))
        # считываем все переменные из ини файла
        with open(bot_name + '.ini', 'r', encoding='utf-8') as f_ini:
            for s in f_ini:
                str_ = s.split(';')
                #       print(str_[0])
                if str_[0] == '!':
                    continue
                if str_[0] == 'db_path':
                    db_path = str_[1]
        # print('db_path = ' + db_path)
    return db_path


def connection_db(name_db):
    conn = sqlite3.connect(name_db)  # или :memory: чтобы сохранить в RAM
    return conn


def cursor_db(conn):
    cursor = conn.cursor()
    return cursor


# Проверка существуетли таблица в базе
def sql_check_table(cursor, table_name):
    # table_name='albums'
    sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?"
    cursor.execute(sql, [(table_name)])
    count_table = cursor.fetchone()
    # print(count_table)
    true = count_table[0]
    if true:
        return 0
    else:
        # Создание таблицы
        print('Таблица %s нет в базе!' % table_name)  # or use fetchone()
        if table_name == 'albums':
            cursor.execute("""CREATE TABLE albums
                              (title text, artist text, release_date text,
                               publisher text, media_type text)
                           """)
            print('Создана таблица %s в базе!' % table_name)  # or use fetchone()
            return 0
        if table_name == 'list_result_scan_user':
            cursor.execute("""CREATE TABLE list_result_scan_user
                              (idid INTEGER, parent_name text, publicaciy INTEGER, podpisch INTEGER, podpiski INTEGER
                              , zakruto INTEGER, user_name  text, user_name_h1 text, user_prim text                               
                              , day_w INTEGER, mount_w INTEGER, year_w INTEGER)""")
            print('Создана таблица %s в базе!' % table_name)  # or use fetchone()
            return 0

        else:
            print('Структура таблицци не задана!')  # or use fetchone()
            return 1


def isert_data_in_table(table_name='list_result_scan_user',
                        data_json='{"idid":"1", "parent_name":"iasko10","publicaciy":"0","podpisch":"940","podpiski":"7 488","zakruto":"0", "user_name":"kbasistii", "user_name_h1":"Коля Басстий", "user_prim":""}'):
    #
    conn = connection_db(db_path())
    cursor = cursor_db(conn)

    now = datetime.datetime.now()
    err = sql_check_table(cursor, table_name)
    if err == 1:
        return 1
        print(err)
    data = json.loads(data_json)
    sql_str_into = 'INSERT INTO ' + table_name + '('
    sql_str_data = ' VALUES ('
    for dj in data:
        sql_str_into = sql_str_into + dj.__str__() + ','
        sql_str_data = sql_str_data + "'" + data[dj] + "',"
    sql_str_into = sql_str_into[0:-1] + ')'
    sql_str_data = sql_str_data[0:-1] + ')'
    cursor.execute(sql_str_into + sql_str_data)
    conn.commit()
    cursor.close()
    conn.close()


def check_double_user(user_name_i):
    # conn = connection_db("mydatabase.db")
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    sql = "select count(user_name) from User_i where user_name=? group by user_name HAVING count(user_name)>0"
    cursor.execute(sql, [(user_name_i)])
    count_user = cursor.fetchone()
    print(count_user)
    if count_user is None:
        rc = 0
    else:
        print('count_user[0] = ' + count_user[0].__str__())
        rc = count_user[0]
    cursor.close()
    conn.close()
    return rc


def check_user_is_closed(user_name_i):
    # Проверка закрыт юзер навсегда
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    sql = "select count(user_name) from User_i where is_closed=1 and user_name=? group by user_name HAVING count(user_name)>0"
    cursor.execute(sql, [(user_name_i)])
    count_user = cursor.fetchone()
    print(count_user)
    if count_user is None:
        rc = 0
    else:
        print('count_user[0] = ' + count_user[0].__str__())
        rc = 1
    cursor.close()
    conn.close()
    return rc


def delete_user_from_list_result_scan_user(user_name_i):
    """
    Удаляем пользователя из спсиска сканированных
    А зачем? А затем:
    Так как этот пользователь удален системой Инстаграм но в дальнейшем
    может появится такой же пользователь
    то мы его удаляем из текущего списка сканированных пользователей.
    В списке user_i мы помечаем его как удаленного
    :param user_name_i:
    :return: 1
    """
    # Проверка закрыт юзер навсегда
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    sql = "DELETE FROM list_result_scan_user WHERE user_name = ?;"
    cursor.execute(sql, [(user_name_i)])
    conn.commit()
    cursor.close()
    conn.close()
    return 1


def check_again_scan_user(user_name_i):
    # проверка на недавнее сканирование пользователя
    # conn = connection_db("mydatabase.db")
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    # sql = "select count(user_name) from List_User_i where user_name=? group by user_name HAVING count(user_name)>0"
    sql = "select count(user_name) from list_result_scan_user where user_name = '" + user_name_i + "' and (select again_scan from User_i where " \
                                                                                                   "user_name='" + user_name_i + "') > julianday() - julianday((select distinct max(data_w) from list_result_scan_user where user_name = ?)) "
    # print(sql)
    cursor.execute(sql, [(user_name_i)])
    count_user = cursor.fetchone()
    print(count_user)
    if count_user is None:
        rc = 0
    else:
        print('count_user[0] = ' + count_user[0].__str__())
        rc = count_user[0]
    cursor.close()
    conn.close()
    return rc


def get_list_donor(user_name_i):
    # получение списка донорских аккаунтов от конкретного пользователья
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    publicaciy_limit = 30
    podpisch_limit = 100
    podpiski_limit_max = 500
    podpiski_limit_min = 100
    # sql = "select count(user_name) from list_result_scan_user where user_name=? group by user_name HAVING count(user_name)>0"
    # print(sql)
    # " l.podpiski+100 <l.podpisch and "
    sql = "select l.user_name from list_result_scan_user l where l.parent_name=? and  l.zakruto=0 and" \
          " l.publicaciy>" + publicaciy_limit.__str__() + " and " \
                                                          " l.podpisch>" + podpisch_limit.__str__() + " and " \
                                                                                                      " (l.podpiski>" + podpiski_limit_min.__str__() + " and  l.podpiski<" + podpiski_limit_max.__str__() + ") and" \
                                                                                                                                                                                                            " l.user_name not in " \
                                                                                                                                                                                                            " (select s.parent_name from list_result_scan_user s " \
                                                                                                                                                                                                            " where (select again_scan from User_i where user_name=s.user_name) > julianday() - " \
                                                                                                                                                                                                            " julianday((select distinct max(data_w) from list_result_scan_user where    user_name = s.user_name)))"
    rows = cursor.execute(sql, [(user_name_i)])
    rez = '['
    for row in rows:
        rez = rez + '{"un":"' + row[0].__str__() + '"},'
    rez = rez[0:-1] + ']'
    if rez == '[':
        rez = ''
    if rez == ']':
        rez = ''
    cursor.close()
    conn.close()
    return rez


def get_list_subscribe(owner_name, doner_name, top_row):
    # получение списка для подписок
    # top_row - определяет количество первых записей отбираемых для лайков
    conn = connection_db(db_path())
    cursor = cursor_db(conn)

    rez = '['
    publicaciy_limit = 30
    podpisch_limit = 100
    podpiski_limit_max = 500
    podpiski_limit_min = 100
    # sql = "select count(user_name) from list_result_scan_user where user_name=? group by user_name HAVING count(user_name)>0"
    # print(sql)
    # " l.podpiski+100 <l.podpisch and "

    sql = " select l.user_name, l.parent_name " \
          " from list_result_scan_user l " \
          " where l.zakruto=0 " \
          " and l.parent_name='" + doner_name + \
          "' and (l.publicaciy>10 and  l.publicaciy<1000) " \
          " and (l.podpisch>30 and  l.podpisch<1000) " \
          " and (l.podpiski<1000) " \
          " and l.user_name not in  (select user_name from user_i where user_del=1 ) " \
          " and l.user_name not in  (select user_name from user_i where unusual>0 ) " \
          " and l.user_name not in  (select stop_user_name from stop_users) " \
          " and l.user_name not in  (select s.target_s from subscription_list s where s.owner_s=?) LIMIT 0, " + str(
        top_row)
    print(sql + owner_name)
    rows = cursor.execute(sql, [(owner_name)])
    print('rows = ' + rows.rowcount.__str__())
    for row in rows:
        rez = rez + '{"un":"' + row[0].__str__() + '","parent":"' + row[1].__str__() + '"},'

    rez = rez[0:-1] + ']'
    if rez == '[':
        rez = ''
    if rez == ']':
        rez = ''
    print('rez = ' + rez)
    cursor.close()
    conn.close()
    return rez


def get_list_unsubscribe(owner_name, top_row):
    # получение списка для отписок
    # top_row - определяет количество первых записей отбираемых для лайков
    conn = connection_db(db_path())
    cursor = cursor_db(conn)

    rez = '['
    publicaciy_limit = 30
    podpisch_limit = 100
    podpiski_limit_max = 500
    podpiski_limit_min = 100
    sql = "select target_s, owner_s  from subscription_list " \
          + " where owner_s = ? " \
          + " and target_s not in (select stop_user_name from stop_users) " \
          + " and data_uns IS NULL " \
          + " order by data_s  LIMIT 0, " + str(top_row)

    # sql = "select l.user_name, l.parent_name from list_result_scan_user l where l.zakruto=0 and l.parent_name='" + doner_name + "' and (l.publicaciy>10 and  l.publicaciy<1000) and (l.podpisch>30 and  l.podpisch<1000) and  (l.podpiski<1000) and l.user_name not in (select s.target_s from subscription_list s where s.owner_s=?) LIMIT 0, "+str(top_row)
    # print(sql + owner_name)
    rows = cursor.execute(sql, [owner_name])
    print('rows = ' + rows.rowcount.__str__())
    for row in rows:
        rez = rez + '{"un":"' + row[0].__str__() + '","parent":"' + row[1].__str__() + '"},'

    rez = rez[0:-1] + ']'
    if rez == '[':
        rez = ''
    if rez == ']':
        rez = ''
    print('rez = ' + rez)
    cursor.close()
    conn.close()
    return rez


def update_subscribe_un(owner_user, user_name_i):
    # Добавленеи в базу информации о подписке
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    now = datetime.datetime.now()
    d1 = now.date().__str__()
    t1 = now.time().__str__()
    sql = "update subscription_list " \
          + " set data_uns = '" + d1 + "'" \
          + ", time_uns = '" + t1 + "'" \
          + " where owner_s = '" + owner_user + "'" \
          + " and target_s = '" + user_name_i + "'"
    # print(sql)
    ee = cursor.executescript(sql)
    cursor.close()
    conn.close()
    rez = 0
    return rez


def insert_into_subscribe(owner_user, parent_user, user_name_i):
    # Добавленеи в базу информации о подписке
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    now = datetime.datetime.now()
    d1 = now.date().__str__()
    t1 = now.time().__str__()
    sql = "INSERT INTO subscription_list (owner_s,parent_s,target_s,data_s,time_s) " \
          "VALUES ('" + owner_user + "','" + parent_user + "','" + user_name_i + "','" + d1 + "','" + t1 + "');"
    # print(sql)
    ee = cursor.executescript(sql)
    cursor.close()
    conn.close()
    rez = 0
    return rez


def update_users_i_set_is_closed(user_name_i):
    """
        Обновляем данные об аккаунте
        Ставим признак что  аккаунт закрыт для других пользователей
        :param user_name_i:
        :return: error
    """

    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    sql = "UPDATE user_i  SET is_closed = 1 WHERE user_name = '" + user_name_i + "'"
    cursor.executescript(sql)
    cursor.close()
    conn.close()
    rez = 0
    return rez


def update_users_i_set_del(user_name_i):
    """
    Ставит пометку что пользователь удален из инстаграмма
    чтобы в дальнейшем он не попадал в запросы
    :param user_name_i:
    :return:
    """
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    sql = "UPDATE user_i  SET user_del = 1 WHERE user_name = '" + user_name_i + "'"
    # print(sql)
    cursor.executescript(sql)
    cursor.close()
    conn.close()
    rez = 0
    return rez


def update_users_i_set_unusual(user_name_i):
    """
    Ставит пометку что пользователь какойто странный
    чтобы в дальнейшем он не попадал в запросы и мы могли с ним разобратся
    В следующих версиях должен появится параметр почему пользователь странный
    :param user_name_i:
    :return:
    """
    conn = connection_db(db_path())
    cursor = cursor_db(conn)
    sql = "UPDATE user_i  SET unusual = 1 WHERE user_name = '" + user_name_i + "'"
    # print(sql)
    cursor.executescript(sql)
    cursor.close()
    conn.close()
    rez = 0
    return rez


def get_stop_users(user_name_i):
    """
    Получить список пользователей которых нельзя удаляь
    :param user_name_i:
    :return:
    """
    conn = connection_db(db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT stop_user_name FROM stop_users")

    data = (row for row in cursor.fetchall())
    print('data = ' + data.__str__())
    # list.append(x)

    return data


def generet_donor_list(user_name_i):
    str1 = get_list_donor(user_name_i)
    print(str1)
    if str1 == '':
        return
    with open('.\\donor_list\\user_for_scan_' + user_name_i + '.txt', 'w') as file:
        file.write(str1)


def get_work(owner_name, date_day=None, date_clock=None):
    """ Функция возвращает количество подписок
    и отписок за день и за последние два час для конкретного юзера
    """
    conn = connection_db(db_path())
    cursor = cursor_db(conn)

    rez = '['

    sql = """select sum(subday) subday, sum(subhour_ex) subhour_ex, sum(subhour) subhour, 
          sum(unsubday) unsubday, sum(unsubhour_ex) unsubhour_ex, sum(unsubhour) unsubhour 
          from (
          SELECT COUNT(1) subday, 0 subhour_ex, 0 subhour,0 unsubday,0 unsubhour_ex,0 unsubhour 
          FROM subscription_list 
          where data_s = :date_day 
          union all 
          SELECT 0, COUNT(1) subhour_ex, 0, 0, 0 , 0 FROM subscription_list 
          where data_s = :date_day 
          and cast(substr(time_s,1,2) as INTEGER)= :date_clock_ex 
          union all 
          SELECT 0,0, COUNT(1) subhour,0, 0, 0 FROM subscription_list 
          where data_s = :date_day 
          and cast(substr(time_s,1,2) as INTEGER)= :date_clock 
          union all 
          SELECT 0,0,0,COUNT(1)unsubday ,0,0 FROM subscription_list 
          where data_uns = :date_day 
          union all 
          SELECT 0,0,0,0,COUNT(1) unsubhour_ex,0 FROM subscription_list  
          where data_uns = :date_day 
          and cast(substr(time_uns,1,2) as INTEGER)= :date_clock_ex 
          union all 
          SELECT 0,0,0,0,0,COUNT(1) unsubhour FROM subscription_list  
          where data_uns = :date_day 
          and cast(substr(time_uns,1,2) as INTEGER)=:date_clock ) t"""

    param = {"date_day": date_day, "date_clock_ex": date_clock - 1, "date_clock": date_clock}
    # print(sql + owner_name, param)
    # print(param)

    rows = cursor.execute(sql, param)
    # print('rows = ' + rows.rowcount.__str__())
    for row in rows:
        rez = rez + '{"subscribe_all":"' + row[0].__str__() + \
              '","subscribe_hour_ex":"' + row[1].__str__() + '",' \
                                                             ' "subscribe_hour":"' + row[2].__str__() + '",' \
                                                                                                        '","unsubscribe_all":"' + \
              row[3].__str__() + '",' \
                                 '","unsubscribe_hour_ex":"' + row[4].__str__() + '",' \
                                                                                  '"unsubscribe_hour":"' + row[
                  5].__str__() + '"},'

    rez = rez[0:-1] + ']'
    if rez == '[':
        rez = ''
    if rez == ']':
        rez = ''
    # print('rez = ' + rez)
    cursor.close()
    conn.close()
    return rez


def main():
    print(get_stop_users(''))
    # date_r = datetime.datetime.now()
    # data_day = date_r.__str__()[0:10]
    # date_clock = int(date_r.__str__()[11:13])
    # get_work('', data_day, date_clock)


if __name__ == "__main__":
    main()
