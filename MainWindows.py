import math
from tkinter import *
import datetime
import random
import json
import time
from tkinter import messagebox

from selenium import webdriver
#
from Like_user import get_coockis, set_coockis, get_zakaz_subscription_time
from SqlLite_metod import get_list_subscribe, get_list_unsubscribe, update_subscribe_un, update_users_i_set_del, \
    get_work, get_stop_users, update_users_i_set_is_closed, update_users_i_set_unusual
from SqlLite_metod import insert_into_subscribe
from SqlLite_metod import delete_user_from_list_result_scan_user
from selenium.webdriver import ActionChains

# pyinstaller MainWindows.py --noconsole --onefile
from log import print_log

owner_user = 'olgapoluektova_style'
password = 'vitavita12'
doner_user = "burdastylerussia"
all_subscribe = 0
all_unsubscribe = 0
browser = webdriver.Chrome('C:\\Python\\chromedriver\\chromedriver.exe')
python_lang = 0


def clicked():
    """
    Запуск браузера
    О
    :return:
    """
    global browser
    zakaz_nomer = 1
    list_user_donor = '{"un":"burdastylerussia"}'
    data = json.loads(list_user_donor)
    print_log(data["un"])

    print_log(data.__str__())
    dir_db = 'mydatabase.db'
    # Определяемся с пользователем
    # olgapoluektova_style - vitavita12
    # owner_user = 'olgapoluektova_style'
    # password = 'vitavita12'

    browser.get("https://www.instagram.com/" + owner_user + "/")
    coockis_error = get_coockis(browser, owner_user)
    browser.refresh()
    time.sleep(10)
    if coockis_error > 0:
        assert owner_user in browser.title
        time.sleep(3)
        checkbox_elems = browser.find_elements_by_css_selector("a[href*='logged_out_half_sheet']")
        print_log(len(checkbox_elems).__str__())  # Результат: 2
        for number in checkbox_elems:
            number.click()

        time.sleep(2)
        input_phone = browser.find_element_by_name("username")
        print_log(input_phone.__str__())
        input_phone.send_keys(owner_user)
        input_password = browser.find_element_by_name("password")
        # input_password.send_keys(zakazchik_data[1])
        input_password.send_keys(password)
        time.sleep(2)
        # "//input[@name='lang' and @value='Python']"
        Button_elems = browser.find_elements_by_xpath("//button[@type='submit']")
        # Button_elems = browser.find_elements_by_link_text('Войти')
        time.sleep(2)
        print_log('2---------------------------------------------------')
        for number in Button_elems:
            print_log(number.text + '^' + number.tag_name)
            # print(number.tag_name)
            print_log(number.parent.__str__())
            print_log(number.location.__str__())
            print_log(number.size.__str__())
            number.click()

        # <button class="aOOlW   HoLwm " tabindex="0">Не сейчас</button>
        time.sleep(3)
        print_log('3---------------------------------------------------')
        Button_elems2 = browser.find_elements_by_xpath("//button[contains(text(), 'Не сейчас')]")
        # Button_elems = browser.find_elements_by_link_text('Войти')
        for number2 in Button_elems2:
            print(number2.text + '^' + number2.tag_name)
            # print(number.tag_name)
            print(number2.parent)
            print(number2.location)
            print(number2.size)
            number2.click()
        print_log('END---------------------------------------------------')
        time.sleep(5)

        z_time = get_zakaz_subscription_time(zakaz_nomer, dir_db)
        print_log(z_time.__str__())
        for z in z_time:
            print_log(z[0])
            print_log(z[1])

    set_coockis(browser, owner_user)


def save_set_coockis():
    set_coockis(browser, owner_user)


def on_closing():
    if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
        try:
            browser.close()
        except:
            pass  # Если ответили да то в любом случае закрываем окно
        finally:
            window.destroy()


def change_state():
    print_log(python_lang.get().__str__())
    if python_lang.get() == 1:
        pass


def like_thread(time_long):
    global all_subscribe
    max_count_user = 8  # максимальное количество подписчиков в запросе
    a = 1
    lime = 0
    while a == 1:
        # что бы небыло подозрения всегда меняем количество подписчиков в запросе
        top_row = 1 + math.floor(max_count_user * random.random())
        print_log('Сейчас подпишемся и поставм лайки ' + top_row.__str__() + ' юзерам.')
        # Запрашиваем лист пользователей для подписки
        list_users = get_list_subscribe(owner_user, doner_user, top_row)
        data = json.loads(list_users)
        time.sleep(8 * random.random() + 10)
        # Перебор всех юзеров
        for d in data:
            # Жесткая проверка времени если закончился час выходим
            if 0 < datetime.datetime.now().minute < (60 - time_long):
                print_log('Время работы прошло ждем новый период')
                a = 0  # Заканчиваем работу потока
                break
            print_log("Начинаем подписку на юзера : " + d["un"])
            # Переходим на страницу юзера
            browser.get("https://www.instagram.com/" + d["un"] + "/")
            time.sleep(5)
            # Ставим глобальный try. Чтобы не случилось мы отметим текущего пользователья как странного
            try:
                # Пробуем подписатся
                try:
                    Button_elems4 = browser.find_element_by_xpath("//button[contains(text(), 'Подписаться')]")
                    Button_elems4.click()
                    insert_into_subscribe(owner_user, d["parent"], d["un"])
                    time.sleep(6)
                except:
                    # Сразу проверяем подписанны мы на этого пользователя или нет
                    try:
                        Button_elems4 = browser.find_element_by_xpath("//div[1]/div[2]/span/span[1]/button")
                        Button_elems4.click()
                        # Если все в порядке то
                        print_log('На этого пользователья мы подписаны желательо его отнести к необычным.')
                        # Неоходимо сделать проверку входит ли он в исключенные юзеры
                        continue
                    except:
                        # На этого пользователья мы явно не подписаны
                        print_log('Возможно ошибка.')
                        try:
                            Button_elements15 = browser.find_element_by_xpath(
                                "//h2[contains(text(), 'Ошибка')]")
                            print_log('На страницу большими буквами написано "Ошибка".')
                            # Ни чего не делаем возможно ошибка на сервере
                            # Хорошо былобы здесь отправить письмо
                            time.sleep(30)
                            continue
                        except:
                            print_log('Точно ошибка. Делаем паузу и преходим к другому аккаунту.')
                            # Помечаем как странного из user_i
                            update_users_i_set_unusual(d["un"])
                            continue

                    # /html/body/div/div[1]/div/div/h2
                    # или это "Мы на этот акаунт уже подписанны"
                    # или этот "К сожалению, эта страница недоступна."

                    print_log('Это закрытый аккаунт или страница не доступна.')
                    Button_elements15 = browser.find_element_by_xpath(
                        "//h2[contains(text(), 'Это закрытый аккаунт')]")
                    print_log('Это закрытый аккаунт.2')
                    if Button_elements15:
                        print_log('Чтото мы сюда никогда не поподали.1')
                        print_log('Аккаунт закрытый. Лайк поставить не удастся')
                        # Обновляем данные что аккаунт закрыт
                        update_users_i_set_is_closed(d["un"])
                        # Делаем небольшую паузу и переходим к другому пользователю
                        time.sleep(random.random() * 15)
                        continue
                    else:
                        print_log('Чтото мы сюда никогда не поподали.2')
                        print_log('Значит нет публикуций.')
                        time.sleep(random.random() * 15)
                        continue

                # Выбираем первую плитку и кликаем на ней.
                # Выбирае случайным образом из первых 3 плиток.
                try:
                    plitka = math.floor(3 * random.random()) + 1
                    print_log('Выбирае случайным образом ' + plitka.__str__() + ' из первых 3 плиток.')
                    time.sleep(1)
                    #print_log('Проверка hover.')
                    hover = browser.find_element_by_xpath(
                        "//div/div[3]/article/div[1]/div/div[1]/div[1]")  # Наведение мыши
                    # //* //div/div[3]/article/div[1]/div/div[1]/div[1]/a/div/div[2]
                    # //*//div/div[2]/article/div[1]/div/div[1]/div[1]
                    #    //div/div[2]/article/div[1]/div/div[1]/div[1]/a/div/div[2]
                    #print_log('Проверка hover.1')
                    ActionChains(browser).move_to_element(hover).perform()
                    #print_log('Проверка hover.2')
                    browser.find_element_by_xpath(
                        "//div/div[3]/article/div[1]/div/div[1]/div[" + plitka.__str__() + "]").click()
                    print_log('Пост открыли.')
                except:
                    try:
                        print_log('Пост не смогли открыть. Смотрим что случилось.')
                        hover = browser.find_element_by_xpath(
                            "//div/div[4]/article/div[1]/div/div[1]/div[1]")  # Наведение мыши
                        # !!!! На что наводим
                        print_log('Проверка hover.5')
                        ActionChains(browser).move_to_element(hover).perform()
                        print_log('Проверка hover.6')
                        browser.find_element_by_xpath(
                            "//div/div[4]/article/div[1]/div/div[1]/div[" + plitka.__str__() + "]").click()
                        print_log('Проверка hover.7')
                    except:
                        try:
                            print_log('Проверка hover.8')
                            hover = browser.find_element_by_xpath(
                                "//div/div[2]/article/div[1]/div/div[1]/div[1]")  # Наведение мыши
                            # !!!! На что наводим
                            print_log('Проверка hover.9')
                            ActionChains(browser).move_to_element(hover).perform()
                            print_log('Проверка hover.10')
                            browser.find_element_by_xpath(
                                "//div/div[2]/article/div[1]/div/div[1]/div[" + plitka.__str__() + "]").click()
                            print_log('Проверка hover.11')
                        except:
                            # Помечаем как странного пользователя и переходим к новому
                            # Здесь нам не удалось найти плитку поставить лайк
                            print_log('Для этого мользователя не удалсь открыть плитку. Что чень странно.')
                            update_users_i_set_unusual(d["un"])
                            continue

                # Стпавим лайк
                time.sleep(5 + math.floor(10 * random.random()))
                # на разных пользовательях разные лайки
                try:
                    print_log('Ставим лайк по 1 пути!')
                    # Первый путь когда нет div с рекомендациями над постами(article/div[2]/section[1])
                    browser.find_element_by_xpath(
                        "//div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button").click()
                except:
                    print_log('Ставим лайк по 2 пути!')
                    # Первый путь когда есть div с рекомендациями над постами(article/div[3]/section[1])
                    try:
                        browser.find_element_by_xpath(
                            "//div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button").click()
                    except:
                        browser.find_element_by_xpath(
                            "//div[3]/div[2]/div/article/div[3]/section[1]/span[1]/button").click()
                        print_log('Ставим лайк по 3 пути!')

                    # //div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button
                    # //div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button/div/svg/path
                    # //div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button
                    # //div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button
                    # //div[3]/div[2]/div/article/div[3]/section[1]/span[1]/button
                    # //*[@id="react-root"]/section/main/div/div[3]/article/div[1]/div/div[1]/div[1]/a/div/div[2]
                    # e_khaliapina разобратся с этим аккаунтом так как там пошло чтото не так
                time.sleep(math.floor(3 * random.random()))
                # Закрываем окно просмотра поста
                try:
                    print_log('Ошибка была сдесь! +9')
                    # hover = browser.find_element_by_xpath("/html/body/div[4]/div[3]/button")  # Наведение мыши
                    #                                        /html/body/div[4]/div[3]/button
                    print_log('Ошибка была сдесь! +91')
                    # ActionChains(browser).move_to_element(hover).perform()
                    print_log('Ошибка была сдесь! +92')
                    browser.find_element_by_xpath("/html/body/div[4]/div[3]/button").click()
                except:
                    print_log('Ошибка была сдесь!')
                    # hover = browser.find_element_by_xpath("//div[4]/div[3]/button")  # Наведение мыши
                    print_log('Ошибка была сдесь!1')
                    # ActionChains(browser).move_to_element(hover).perform()
                    print_log('Ошибка была сдесь!11')
                    try:
                        print_log('Ошибка была сдесь!2')
                        browser.find_element_by_xpath("//div[4]/div[3]/button").click()
                        print_log('Ошибка была сдесь!21')
                    except:
                        print_log('Ошибка была сдесь!3')
                        browser.find_element_by_xpath("//div[3]/div[3]/button").click()
                        print_log('Ошибка была сдесь!31')
                time.sleep(4)

            except:
                # По идеи стдесь мы должны отметить что ошибка неизвестная и пометить пользователея
                # как необычный unusual(user_i)
                # Поэтому тут должен быть такой код
                # print_log('Откуда сюда попал не знаю перед кнопкой 5')
                try:
                    print_log('Откуда сюда попал не знаю перед кнопкой 5')
                    Button_elems5 = browser.find_element_by_xpath(
                        "//h2[contains(text(), 'К сожалению, эта страница недоступна.')]")
                    # print_log(Button_elems5.text)
                    if Button_elems5:
                        print_log('Страница подписчика ' + d["un"] + ' закрыта!')
                        # print_log(Button_elems5.text)
                        # Удоляем из списка сосканированных ползователей
                        delete_user_from_list_result_scan_user(d["un"])
                        # Помечаем как удоленного из user_i
                        update_users_i_set_del(d["un"])
                    else:
                        print_log('Наверное мы сюда никогда не попадем.')
                except:
                    print_log('Нет страницы пользователя. Помечаем как удаленного.')
                    print_log('Это закрытый аккаунт или страница не доступна.')
                    # Если дошли до это то отправим пользователя в странные
                    update_users_i_set_unusual(d["un"])
                    Button_elements15 = browser.find_element_by_xpath(
                        "//h2[contains(text(), 'Это закрытый аккаунт')]")
                    print_log('Это закрытый аккаунт.2')
                    if Button_elements15:
                        print_log('Аккаунт закрытый. Лайк поставить не удастся')
                        # Обновляем данные что аккаунт закрыт
                        update_users_i_set_is_closed(d["un"])
                        # Делаем небольшую паузу и переходим к другому пользователю
                        time.sleep(random.random() * 15)
                        continue
                    else:
                        print_log('С аккаунтом явно что не так.')
                        time.sleep(random.random() * 15)
                        # Удоляем из списка сосканированных ползователей
                        delete_user_from_list_result_scan_user(d["un"])
                        # Помечаем как удоленного из user_i
                        update_users_i_set_del(d["un"])
                        # Помечаем как странного из user_i
                        update_users_i_set_unusual(d["un"])
                        continue

                # В дальнейшем разобратся с этим пользователем, почему кнопка Подписатся не доступна
                # Проверить доступна ли кнопка Отписатся если нет то пользователя в бан.
                # Что именно случилось с этим пользователем толи страници не оступна или еще что.
            time.sleep(1)
            look_storis()
            lime = lime + 1
            all_subscribe = all_subscribe + 1
            print_log('lime = ' + lime.__str__())
            if lime > top_row:
                # browser.close()
                a = 0  # Заканчиваем работу потока
                break
            else:
                # Отдыхаем и идем на следующий круг
                # Таймацт до следующего цикла
                time.sleep(10 * random.random() * random.random() * 14)
        a = 0  # Заканчиваем работу цикла WHILE


def dislike_thread(time_long):
    global all_unsubscribe
    a = 1
    max_count_user = 6  # максимальное количество подписчиков в запросе
    un_lime = 0
    while a == 1:
        top_row = 1 + math.floor(max_count_user * random.random())
        print_log('dislike_thread top_row = ' + top_row.__str__())
        # Запрашиваем лист пользователей для подписки
        list_users = get_list_unsubscribe(owner_user, top_row)
        data = json.loads(list_users)
        time.sleep(18)
        for d in data:
            # Жесткая проверка времени если закончился час выходим
            if 0 < datetime.datetime.now().minute < (60 - time_long):
                print_log('Время работы прошло ждем новый период')
                a = 0  # Заканчиваем работу потока
                break
            print_log(d["un"])
            browser.get("https://www.instagram.com/" + d["un"] + "/")
            time.sleep(5)
            try:
                # Нажимаем кнопку отписатся
                Button_elems4 = browser.find_element_by_xpath("//div[1]/div[2]/span/span[1]/button")
                Button_elems4.click()
                # Нажимаем пожтверждение отписки
                time.sleep(5 * random.random())
                Button_elems4 = browser.find_element_by_xpath("//div[4]/div/div/div/div[3]/button[1]")
                Button_elems4.click()
            except:
                time.sleep(3)
            finally:
                update_subscribe_un(owner_user, d["un"])
                time.sleep(1)
                look_storis()

            un_lime = un_lime + 1
            all_unsubscribe = all_unsubscribe + 1
            print_log('unlime = ' + un_lime.__str__())
            # Если количество циклов превысило количество подписчиков из запроса то выходим
            if un_lime > top_row:
                # browser.close()
                a = 0  # Заканчиваем работу потока
                break
            else:
                # Отдыхаем и идем на следующий круг
                # Таймацт до следующего цикла
                time.sleep(10 * random.random() * random.random() * 17)
        a = 0  # Заканчиваем работу цикла WHILE


def look_storis():
    time.sleep(3 * random.random() + 3)
    try:
        Button_elems4 = browser.find_element_by_xpath("//div[2]/div/div/div[1]/a/div/div/img")
        Button_elems4.click()
    except:
        pass
    time.sleep(7 * random.random())

    try:
        Button_elems4 = browser.find_element_by_xpath("//div[4]/div/div/div/div[3]/button[2]")
        Button_elems4.click()
    except:
        time.sleep(4 * random.random())
    time.sleep(3 * random.random())

    li_num = math.floor(4 * random.random()) + 3
    # print_log("li_num = " + li_num.__str__() + "   //div/div[1]/div/div/div/div/ul/li[" + li_num.__str__() + "]/div/button")
    try:

        Button_elems4 = browser.find_element_by_xpath(
            "//div/div[1]/div/div/div/div/ul/li[" + li_num.__str__() + "]/div/button")
        # //*[@id="react-root"]/section/main/section/div/div[1]/div/div/div/div/ul/li[4]/div/button
        Button_elems4.click()
    except:
        time.sleep(3 * random.random())


def auto_work(minute_work):
    global browser
    ff = 0                                      # Операция которая сейчас выполняется 0 - подписка/ 1 - отписка
    wwww = 1                                    # Переменная для прерывания бесконечного цикла
    first_start_browser = 0                     # Статус браузера 0 - не запущен, 1 - запущен
    auto_work_datetime = time.time() / 60       # Значение времени в минутах на начало работы робота
    # while (auto_work_datetime_new.__int__() - auto_work_datetime.__int__()) < minute_work.__int__():
    while wwww == 1:

        date_r = datetime.datetime.now()
        data_day = date_r.__str__()[0:10]
        date_clock = int(date_r.__str__()[11:13])
        print(get_work('', data_day, date_clock))
        # Делаем ограничение по часам работы в сутки
        if 7 < datetime.datetime.now().hour < 22:
            print_log("Пора поработать. Час: " + datetime.datetime.now().hour.__str__())
            # Делаем ограничение по минутам работы в час
            if 0 < datetime.datetime.now().minute < (60 - minute_work):
                print_log('Пошел спать на 30 секунд - ' + datetime.datetime.now().minute.__str__())
                if first_start_browser == 1:
                    browser.close()
                    browser = webdriver.Chrome('C:\\Python\\chromedriver\\chromedriver.exe')
                    first_start_browser = 0
                time.sleep(30)
                continue
            if first_start_browser == 0:
                clicked()
                first_start_browser = 1
            print_log('ff =' + ff.__str__())
            if ff == 0:
                print_log('Сейчас начнется подписка(' + ff.__str__()+').')
                like_thread(minute_work)
                ff = 1
            else:
                print_log('Сейчас начнется отписка(' + ff.__str__() + ').')
                dislike_thread(minute_work)
                ff = 0
            auto_work_datetime_new = time.time() / 60
            print_log("В этом часе робат отработал: " + (auto_work_datetime_new - auto_work_datetime).__str__() + " минут.")
        else:
            print_log("Часы работы еше не наступили.")
            time.sleep(600)


def main():
    global python_lang
    print_log(browser.__str__())
    current_datetime = datetime.datetime.now().minute
    print_log(current_datetime.__str__())
    print_log((time.time() / 60).__str__())
    # print_log(current_datetime.hour.__str__())
    # print_log(current_datetime.minute.__str__())

    window = Tk()
    window.title("Добро пожаловать в приложение PythonRu")
    window.geometry('400x250')
    btn = Button(window, text="Зайти на мою страницу инстаграма", command=clicked)
    btn.grid(column=1, row=0)
    btn = Button(window, text="Запомнить меня", command=save_set_coockis)
    btn.grid(column=2, row=0)

    btn = Button(window, text="Запустить робота", command=save_set_coockis)
    btn.grid(column=2, row=0)

    python_lang = IntVar()
    python_checkbutton = Checkbutton(text="Python", variable=python_lang,
                                     onvalue=1, offvalue=0, padx=15, pady=20, command=change_state)
    python_checkbutton.grid(row=2, column=2, sticky=W)
    auto_work(35)
    # x = threading.Thread(target=auto_work, args=[30])  # Создание потока
    # print_log('Запускаем поток auto_work.')
    # x.start()  # Запуск потока
    # print_log('Ждем когда завершиться поток.')

    # x = threading.Thread(target=like_thread, args=())  # Создание потока
    # print_log('Запускаем поток like_thread.')
    # x.start()  # Запуск потока
    # print_log('Ждем когда завершиться поток.')

    # xd = threading.Thread(target=dislike_thread, args=())  # Создание потока
    # print_log('Запускаем поток dislike_thread.')
    # xd.start()  # Запуск потока

    data = get_stop_users('')

    languages_listbox = Listbox()

    for d1 in data:
        languages_listbox.insert(END, d1)

    languages_listbox.grid(column=1, row=2)
    # languages_listbox.pack()

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


if __name__ == "__main__":
    main()

# To Do
# 1. Добавить Часы выполнения с 8-00 до 22-00
# 2. Передать запуск и остановка пууза на кнопку на форме.
# 3. Окошко вывода логов
# 4. Настройка Rubbit
# 5. Разработка робота по сбору подписчиков
# 6. Рассылка писем
#    5.1. Пробный запуск.
# 7. Протестировать использование куки из от Хрома
#    Где находятся cookie: C: \Users \Имя_пользователя \AppData \Local \Google \Chrome \User Data \Default.
#    Файл с куками называется Cookies и не имеет расширения.
#    В старых версиях Chrome последняя папка может называться Profile.