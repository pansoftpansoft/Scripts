import datetime
import json
import time
import win32con
from selenium import webdriver
from SqlLite_metod import get_list_subscribe
from SqlLite_metod import insert_into_subscribe
from SqlLite_metod import delete_user_from_list_result_scan_user
from chrom_proxy import get_chromedriver
from selenium.webdriver import ActionChains
import sqlite3 as lite

import pickle
import selenium.webdriver


def get_zakazchik(owner_user: str, dir_db):
    """
    zakazchik_name - 0
    zakazchik_pasw - 1
    famil - 2
    imy - 3
    otch - 4
    proxy_ip - 5
    proxy_port - 6
    proxy_user - 7
    proxy_pasw - 8
    :param insta_user:
    :return:
    """
    zakazchik_data = []
    print(owner_user)
    con = lite.connect(dir_db)
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT zakazchik_name, zakazchik_pasw, famil, imy, otch, proxy_ip, proxy_port, proxy_user, proxy_pasw FROM zakazchik where zakazchik_name='" + owner_user + "'")
        print(
            "SELECT zakazchik_name, zakazchik_pasw, famil, imy, otch, proxy_ip, proxy_port, proxy_user, proxy_pasw FROM zakazchik where zakazchik_name='" + owner_user + "'")
        rows = cur.fetchall()
        for row in rows:
            print(row[0])
            zakazchik_data.append(row[0])
            zakazchik_data.append(row[1])
            zakazchik_data.append(row[2])
            zakazchik_data.append(row[3])
            zakazchik_data.append(row[4])
            zakazchik_data.append(row[5])
            zakazchik_data.append(row[6])
            zakazchik_data.append(row[7])
            zakazchik_data.append(row[8])
    return zakazchik_data


def get_zakaz_subscription_time(nomer_zakaz, dir_db):
    """
    Возвращает время работы робота для конкретного заказа
    nomer_zakaz - номер заказа
    dir_db - база данных к которой ведется обращение
    """
    zakaz_subscription_time = []
    print(nomer_zakaz)
    con = lite.connect(dir_db)
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT start_t, stop_t FROM zakaz_subscription_time  where  not_work=0 and nomer_zakaz =" + nomer_zakaz.__str__() + "  order by start_t")
        print(
            "SELECT start_t, stop_t FROM zakaz_subscription_time  where  not_work=0 and nomer_zakaz =" + nomer_zakaz.__str__() + "  order by start_t")
        rows = cur.fetchall()
        for row in rows:
            t = []
            t.append(row[0])
            t.append(row[1])
            ss = row[0]
            t1 = parse_time(ss)
            ss = row[1]
            now = datetime.datetime.now()
            ss = str(now.time())
            t2 = parse_time(ss)
            dt = t2 - t1
            print(dt.seconds / 60)
    return zakaz_subscription_time


def parse_time(ss):
    """
    Преобразует время формата  17:00:00.000000 в 0001-01-01 17:00:00
    полсле чего можно сделать вычитание
    :param ss: строка времени в формате 17:00:00.000000
    :return: 0001-01-01 17:00:00
    """
    p = 0
    i = 0
    t = ''
    secund = 0
    milisecund = 0
    hour = 0
    for s in ss:
        i = i + 1  # Зделано так  стобы поймать реальну точку
        if s != ':':
            t = t + s
        elif s == ':' or s == '.':
            p = p + 1
            if p == 1:
                hour = int(t)
                t = ''
            elif p == 2:
                minute = int(t)
                t = ''
                secund = int(ss[i:i + 2])
            elif p == 3:
                if ss[i:] == '':
                    milisecund = 0
                else:
                    milisecund = int(ss[i:])
    # sss = datetime.datetime(1, 1, 1, 17, 00, 00, 0)
    sss = datetime.datetime(1, 1, 1, hour, minute, secund, milisecund)
    return (sss)


def get_browser_for_zakazchik(zakazchik_data):
    """
    Функция возвращает драйвер браузере с прописаным прокси
    :param insta_user: имя пользователья для которого создается браузер
    :param dir_db: Директория базы данных, Sqlite
    :return: возвращеется браузер
    """
    # Делаем запрос в базу данных для получения параметров прокси
    # PROXY_HOST = '195.62.53.110'  # rotating proxy or host
    # PROXY_PORT = 16986 # port
    # proxy_user = 'rp10v6090638' # username
    # proxy_pass = 'vGHRtazxPx' # password
    # ip; port; login; pwd; out_ipv6; user_i; pass_i; mail_tel; mail_a; mail_p

    ip = zakazchik_data[5]
    proxy_port = zakazchik_data[6]
    proxy_user = zakazchik_data[7]
    proxy_pass = zakazchik_data[8]
    print(ip, proxy_port, proxy_user, proxy_pass)
    time.sleep(5)
    # def get_chromedriver(use_proxy=False, user_agent=None, _PROXY_HOST='185.158.113.41', _PROXY_PORT=16986, _PROXY_USER='rp10v6090638', _PROXY_PASS='vGHRtazxPx'):
    browser = get_chromedriver(use_proxy=False, user_agent=None, _PROXY_HOST=ip, _PROXY_PORT=proxy_port,
                               _PROXY_USER=proxy_user, _PROXY_PASS=proxy_pass)

    return browser


def get_coockis(browser, owner_user):
    try:
        file="C:\\Python\\Coockis\\" + owner_user + "_cookies.pkl"
        cookies = pickle.load(open(file, "rb"))
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            browser.add_cookie(cookie)
        print(0)
        return 0
    except:
        print(1)
        return 1


def set_coockis(browser, owner_user):
    #try:
    pickle.dump(browser.get_cookies(), open("C:\\Python\\Coockis\\" + owner_user + "_cookies.pkl", "wb"))
    #except:
    #    print('cookies не сохранены')


def main():
    zakaz_nomer = 1
    list_user_donor = '{"un":"burdastylerussia"}'
    data = json.loads(list_user_donor)
    print(data["un"])
    doner_user = data["un"]

    # data = json.loads(list_users)
    print(data)
    dir_db = 'mydatabase.db'
    # Определяемся с пользователем
    owner_user = 'books_for_business_ru'
    zakazchik_data = get_zakazchik(owner_user, dir_db)

    assert isinstance(win32con.MOUSEEVENTF_WHEEL, object)
    browser = get_browser_for_zakazchik(zakazchik_data)
    # browser = webdriver.Chrome('C:\\Python\\chromedriver\\chromedriver.exe')
    browser.get("https://www.instagram.com/" + owner_user + "/")
    coockis_error=get_coockis(browser, owner_user)
    if coockis_error>0:
        assert owner_user in browser.title
        time.sleep(3)
        # browser.get("https://yandex.ru/internet/")
        # time.sleep(10)
        checkbox_elems = browser.find_elements_by_css_selector("a[href*='logged_out_half_sheet']")
        print(len(checkbox_elems))  # Результат: 2
        for number in checkbox_elems:
            number.click()

        time.sleep(2)
        input_phone = browser.find_element_by_name("username")
        print(input_phone)
        input_phone.send_keys(owner_user)
        input_password = browser.find_element_by_name("password")
        input_password.send_keys(zakazchik_data[1])
        time.sleep(2)
        # "//input[@name='lang' and @value='Python']"
        Button_elems = browser.find_elements_by_xpath("//button[@type='submit']")
        # Button_elems = browser.find_elements_by_link_text('Войти')
        time.sleep(2)
        print('2---------------------------------------------------')
        for number in Button_elems:
            print(number.text + '^' + number.tag_name)
            # print(number.tag_name)
            print(number.parent)
            print(number.location)
            print(number.size)
            number.click()

        # <button class="aOOlW   HoLwm " tabindex="0">Не сейчас</button>
        time.sleep(3)
        print('3---------------------------------------------------')
        Button_elems2 = browser.find_elements_by_xpath("//button[contains(text(), 'Не сейчас')]")
        # Button_elems = browser.find_elements_by_link_text('Войти')
        for number2 in Button_elems2:
            print(number2.text + '^' + number2.tag_name)
            # print(number.tag_name)
            print(number2.parent)
            print(number2.location)
            print(number2.size)
            number2.click()
        print('END---------------------------------------------------')
        time.sleep(5)

        z_time = get_zakaz_subscription_time(zakaz_nomer, dir_db)
        print(z_time)
        for z in z_time:
            # now = time.strftime("%H.%M.%S", z[1])
            # then = time.strftime("%H.%M.%S", z[0])
            # print(now)
            # print(then)
            # Кол-во времени между датами.
            # delta = now - then

            # print(delta.days)  # 38
            # print(delta.seconds)  # 1131
            # ttt = z[1]-z[0]
            print(z[0])
            print(z[1])
            t_start = z[0]
            t_end = z[1]

    top_row = 9
    list_users = get_list_subscribe(owner_user, doner_user, top_row)
    data = json.loads(list_users)
    for d in data:
        print(d["un"])
        browser.get("https://www.instagram.com/" + d["un"] + "/")
        time.sleep(2)
        try:
            # Выбираем первую плитку и кликаем на ней.

            Button_elems4 = browser.find_element_by_xpath("//button[contains(text(), 'Подписаться')]")
            Button_elems4.click()
            insert_into_subscribe(owner_user, d["parent"], d["un"])
            time.sleep(2)
            #
            try:
                hover = browser.find_element_by_xpath("//div/div[3]/article/div[1]/div/div[1]/div[1]")  # Наведение мыши
                ActionChains(browser).move_to_element(hover).perform()
                browser.find_element_by_xpath("//div/div[3]/article/div[1]/div/div[1]/div[1]").click()
            except:
                hover = browser.find_element_by_xpath("//div/div[4]/article/div[1]/div/div[1]/div[1]")  # Наведение мыши
                ActionChains(browser).move_to_element(hover).perform()
                browser.find_element_by_xpath("//div/div[4]/article/div[1]/div/div[1]/div[1]").click()
            #Стпавим лайк
            #time.sleep(7)
            #browser.find_element_by_xpath("//div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button").click()
            #time.sleep(3)

            # zoom in with mouse wheel
            #browser.wheel_element(elm, -120)
            # zoom out with mouse wheel
            #browser.wheel_element(elm, 120)

            # Закрываем окно просмотра поста
            hover = browser.find_element_by_xpath("/html/body/div[4]/div[3]/button")  # Наведение мыши
            ActionChains(browser).move_to_element(hover).perform()
            browser.find_element_by_xpath("/html/body/div[4]/div[3]/button").click()
            time.sleep(3)

        except:
            try:
                Button_elems5 = browser.find_element_by_xpath(
                    "//h2[contains(text(), 'К сожалению, эта страница недоступна.')]")
                if Button_elems5:
                    print('Элемент нашел')
                    print(Button_elems5)
                    delete_user_from_list_result_scan_user(d["un"])
                else:
                    print('энет')
            except:
                print('Не нашел элемент')
            # В дальнейшем разобратся с этим пользователем, почему кнопка Подписатся не доступна
            # Проверить доступна ли кнопка Отписатся если нет то пользователя в бан.
            #
            # Что именно случилось с этим пользователем толи страници не оступна или еще что.
            #pass
        # get element

        #elm = browser.find_element_by_xpath('//*[ @ id = "react-root"]/section/main/div')  # Наведение мыши

        # zoom in with mouse wheel
        #browser.wheel_element(elm, -120)
        # zoom out with mouse wheel
        #browser.wheel_element(elm, 120)

        time.sleep(70)

        set_coockis(browser, owner_user)


# b=get_browser_for_zakazchik('ivan_2082_ivanov', 'mydatabase.db')
# b = get_zakaz_subscription_time(2, 'mydatabase.db')


if __name__ == "__main__":
    main()
