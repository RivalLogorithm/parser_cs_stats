from re import S
import time

import selenium.common.exceptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium import webdriver
from selenium.webdriver.common.by import By

from mysql.connector import Error, errorcode, connection
url = "https://csfail.net"


def connect_db():
    try:
        con = connection.MySQLConnection(user='root', password='password',
                                         host='db')
        print("Connection successful")
    except Error as e:
        print(e)
        return exit(1)
    return con

def connect_browser():
    try:
        browser = webdriver.Remote("http://firefox:4444/wd/hub", DesiredCapabilities.FIREFOX)
    except selenium.common.exceptions.WebDriverException as e:
        print(e)
        return exit(1)
    return browser

def create_db():
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS csgofail")
        cursor.execute("USE csgofail")
        cursor.execute("""CREATE TABLE log(
                           `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                           `log_date` DATETIME NOT NULL,
                           `previous_coefficient` FLOAT(6,2) NOT NULL,
                           `current_coefficient` FLOAT(6,2) NOT NULL,
                           `money` FLOAT (10,2) NOT NULL,
                           `current_href` TEXT NOT NULL)""")
        print("Create DB successful")
    except Error as e:
        print(e)


def inserting_db(previous_coef, current_coeff, money, current_href):
    sql = """INSERT INTO log (log_date, previous_coefficient, current_coefficient, money, current_href) VALUES 
            (NOW(), %s, %s, %s, %s)"""
    val = (previous_coef, current_coeff, money, current_href)
    try:
        cursor.execute(sql, val)
        con.commit()
        print("Insert successful")
    except Error as e:
        print(e)


def parsing():
    while True:
        try:
            seconds, miliseconds = "", ""
            browser.get(url)
            last_coeff = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".xhistory__content a:nth-child(1) span:nth-child(2)"))).text
            last_coeff = last_coeff[:-1]
            last_href = browser.find_element(By.CSS_SELECTOR, ".xhistory__content a:nth-child(1)").get_attribute('href')
            print("Прошлый коэффициент {}".format(last_coeff))
            print("Ссылка {}".format(last_href))
            current_href = last_href
            board_text = browser.find_element(By.CSS_SELECTOR, ".board__text").text
            if board_text != 'x':
                while seconds != "0":
                    seconds = browser.find_element(By.CSS_SELECTOR, ".board__number.second span:nth-child(2)").text
                while miliseconds != "0":
                    miliseconds = browser.find_element(By.CSS_SELECTOR, ".board__number.msecond span:nth-child(1)").text
                money = browser.find_element(By.CSS_SELECTOR, ".statistics__value.symbol_usd").text
            else:
                money = browser.find_element(By.CSS_SELECTOR, ".statistics__value.symbol_usd").text
            print("Банк: {}".format(money))

            while last_href == current_href:
                current_href = browser.find_element(By.CSS_SELECTOR, ".xhistory__content a:nth-child(1)").get_attribute(
                    'href')

            current_coeff = browser.find_element(By.CSS_SELECTOR,
                                                 ".xhistory__content a:nth-child(1) span:nth-child(2)").text
            current_coeff = current_coeff[:-1]
            print("Текущий коэффициент {}".format(current_coeff))
            print("Ссылка {}".format(current_href))
            inserting_db(last_coeff, current_coeff, money, current_href)

        except KeyboardInterrupt or selenium.common.exceptions.NoSuchWindowException:
            print("Quit program...")
            browser.quit()
            break


if __name__ == "__main__":
    con = connect_db()
    cursor = con.cursor()
    browser = connect_browser()
    try:
        cursor.execute("USE csgofail;")
    except Error as err:
        print("Database csgofail does not exists.")
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_db()
            print("Database csgofail created successfully.")
            con.database = 'csgofail'
        else:
            print(err)
            exit(1)
    parsing()





