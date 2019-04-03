from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import xlwt
import re
import datetime
import sys


def str_to_date(string):
    month_dict = dict(Января=1,
                      Февраля=2,
                      Марта=3,
                      Апреля=4,
                      Мая=5,
                      Июня=6,
                      Июля=7,
                      Августа=8,
                      Сентября=9,
                      Октября=10,
                      Ноября=11,
                      Декабря=12,
                      January=1,
                      February=2,
                      March=3,
                      April=4,
                      May=5,
                      June=6,
                      July=7,
                      August=8,
                      September=9,
                      October=10,
                      November=11,
                      December=12)

    time = re.split(' ', string)
    for key in month_dict:
        if time[1] == key:
            return datetime.date(year=int(time[2]), day=int(time[0]), month=month_dict.get(key))


def initiate_date():
    while True:
        key = input('Проверить ВСЕ штрафы?(y/n):\n(При выборе \'n\' будет произведена проверка с выбранной даты)\n')
        if key == 'y':
            return [False, datetime.datetime.now()]
        else:
            if key == 'n':
                while(True):
                    print('Введите дату, начиная с которой будут проверены штрафы:')
                    try:
                        res_date = datetime.date(year=int(input('Год:')), day=int(input('День:')), month=int(input('Месяц:')))
                        break
                    except:
                        print('Неверный формат !')
                return [True, res_date]


def pure_html_format(string, img_exsts):
    try:
        date = re.split(r'(e\">)', re.search(r'(<div class=\"date\">)[0-9,A-z,А-я,\., ,\,,:]+', string)[0])[2]
    except:
        print(re.search(r'(<div class=\"date\">)[0-9,A-z,А-я,\., ,\,,:]+', string)[0])
    try:
        price = int(re.split(r'\">\n', re.search(r'(<div class=\"((price through)|(price ))\">)[0-9, ,\n]+', string)[0])[1])
    except:
        print(re.search(r'(<div class=\"((price through)|(price ))\">)[0-9, ,\n]+', string)[0])
    try:
        num = re.split(r'(<dd>)', re.search(r'(<dd>)[0-9]+', string)[0])[2]
    except:
        print(re.search(r'(Дата постановления<\/dt>\n)[ ]+(<dd>)[0-9,А-я,\-,\., ,\,,:]+', string)[0])
    try:
        date_num = re.split(r'(<dd>)', re.search(r'(Дата постановления<\/dt>\n)[ ]+(<dd>)[0-9,\-,A-z,А-я,\., ,\,,:]+', string)[0])[2]
    except:
        print(re.search(r'(Дата постановления<\/dt>\n)[ ]+(<dd>)[0-9,A-z,А-я,\., ,\,,:]+', string)[0])
    try:
        sts = re.search(r'\d\d[0-9,А-я,A-z]+', re.search(r'(<h4>)[0-9,А-я,A-z, ,\n,\"]+', string)[0])[0]
    except:
        print(re.search(r'(<h4>)[0-9,А-я,A-z, ,\n,\"]+')[0])
        sts = '*'
    if img_exsts:
        photo_date = input('СТС {}\nВведите дату с фото:'.format(sts))
        print(photo_date)
    else:
        photo_date = ''
    result = {'plate_num': '',
            'sts': sts,
            'date': date,
            'price': price,
            'num': num,
            'date_num': date_num,
            'photo_date': photo_date
            }
    print(result)
    return result


def tuple_format(fines_list):
    sts_num = ''
    for fine in fines_list:
        if str(sts_num) == str(fine['sts']):
            fine['sts'] = ''
        else:
            sts_num = fine['sts']
            fine['plate_num'] = check_plate_num(sts_num.strip(' \n'), 'Cars.txt')
    print('sheet formatted')
    return fines_list


def check_plate_num(sts_num, file_name):
    file = open(file_name, 'r')
    result = ''
    for line in file:
        dat = re.split(' ', line)
        if dat[0] == sts_num:
            result = dat[1]
            break
    file.close()
    return result


def login(driver, email, password):
    driver.get("https://rosfines.ru/")
    driver.refresh()
    while(True):
        try:
            log_link = driver.find_element(By.LINK_TEXT, "Войти")
            log_link.click()
            sleep(1)
            email_field = driver.find_element(By.ID, "username")
            email_field.send_keys(email)
            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            password_field.send_keys(Keys.ENTER)
            break
        except:
            driver.refresh()
            sleep(2)
    print("login input successed")


def check_fines(driver, date_tr):
    result = []
    sleep(1)
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/ul/li[2]"))
    )

    i = 0
    while (i<12):
        sleep(5)
        info_windows = driver.find_elements(By.LINK_TEXT, "i")
        if not(info_windows):
            i+=1
        else:
            i=12

    if not info_windows:
        print("fines not found")
        print("check success")
        return 0
    else:
        for info_window in info_windows:
            info_window.click()
            sleep(0.7)
            inner_html_data = driver.find_element(By.CLASS_NAME, "map").get_attribute('innerHTML')
            blocks = driver.find_elements(By.CLASS_NAME, "block")
            for block in blocks:
                inner_html_data = inner_html_data + block.get_attribute('innerHTML')

            img = True
            try:
                driver.find_element(By.CLASS_NAME, 'b-photo')
            except:
                img = False

            try:
                if date_tr[0]:
                #date = str_to_date(re.split(r'(<dd>)', re.search(r'(Дата постановления<\/dt>\n)[ ]+(<dd>)[0-9,А-я,\., ,\,,:]+', inner_html_data)[0])[2])
                    date = re.search(r'"date">[0-9, ,A-z,А-я,.]+', inner_html_data)
                    date = re.split(r'>', date[0])
                    date = str_to_date(date[1])
                    if date >= date_tr[1]:
                        result.append(pure_html_format(inner_html_data, img))
                else:
                    result.append(pure_html_format(inner_html_data, img))
            except:
                print('No data received !')
            not_clicked_Exit = True
            while(not_clicked_Exit):
                try:
                    esc_button = driver.find_element(By.LINK_TEXT, "Закрыть")
                    sleep(1)
                    esc_button.click()
                    not_clicked_Exit = False
                except:
                    print("Exit button not found")
            sleep(1)
        print("check success")
        return result


def xl_write(list, fines_data, y_coord):
    for fine in fines_data:
        list.write(y_coord, 0, fine['plate_num'])
        list.write(y_coord, 1, fine['sts'])
        list.write(y_coord, 2, fine['num'])
        list.write(y_coord, 3, fine['date_num'])
        list.write(y_coord, 4, fine['date'])
        list.write(y_coord, 5, fine['price'])
        list.write(y_coord, 6, fine['photo_date'])
        y_coord += 1
    return y_coord


def xl_create_book():
    book = xlwt.Workbook()
    sheet = book.add_sheet('Проверенные машины')
    sheet.write(0, 0, '№ Машины')
    sheet.write(0, 1, 'Стс')
    sheet.write(0, 2, '№ Постановления')
    sheet.write(0, 3, 'Дата постановления')
    sheet.write(0, 4, 'Дата нарушения')
    sheet.write(0, 5, 'Стоимость штрафа')
    sheet.write(0, 6, 'Дата по фото')
    sheet.write(0, 7, 'Оплачен')
    y = 1
    print('book created')
    return book, sheet, y


log_mail = sys.argv[1]
log_password = sys.argv[2]
date_trig = initiate_date()
if date_trig[0]:
    print('Проверка штрафов с {}:\n'.format(date_trig[1]))
driver = webdriver.Chrome('chromedriver.exe')
login(driver, log_mail, log_password)
sleep(1)
driver.get('https://rosfines.ru/finelist')
fines_data = check_fines(driver, date_trig)
if fines_data:
    fines_data = sorted(fines_data, key=lambda fine: fine['sts'])
    fines_data = tuple_format(fines_data)
    fines_book, fines_sheet, fines_y = xl_create_book()
    xl_write(fines_sheet, fines_data, fines_y)
    now = datetime.datetime.now()
    if not date_trig[0]:
        fines_book.save(r'D:\CheckRosFines\fines\Штрафы {}.{}.{}.xls'.format(now.day, now.month, now.year))
    else:
        fines_book.save(r'D:\CheckRosFines\fines\Штрафы {}.{}.{}-{}.{}.{}.xls'.format(date_trig[1].day, date_trig[1].month, date_trig[1].year, now.day, now.month, now.year))
else:
    print('Штрафов нет!')
driver.close()
