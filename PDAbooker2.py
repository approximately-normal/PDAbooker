#PDAbooker
#path C:\Users\allan\Documents\pythonStuff\PDAbooker\all_but_web.py

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys

print("Test booker v.4")

test_centre_text = 'West Perth'
earliest_time = "08:00"
latest_time = "17:00"
earliest_dfn = 9
latest_dfn = 15

rootdir = Path('C:/Users/allan/Documents/pythonStuff/PDAbooker')
booked_path = rootdir / "booked_bool.txt"

booked_bool_file = open(str(booked_path), "r")
booked_bool = booked_bool_file.read()

if booked_bool == "TRUE":
    print("Already booked!")
    sys.exit(0)

driver = webdriver.Chrome(r'C:\Users\allan\AppData\Local\Programs\chromedriver\chromedriver.exe')

driver.get('https://online.transport.wa.gov.au/pdabooking/manage/?0')


lic_num = driver.find_element_by_xpath("//*[@id='id8']/ol/li[5]/div/input")
lic_num.send_keys('1234567')

exp_date = driver.find_element_by_id('licenceExpiryDatePicker')
exp_date.send_keys('07/06/2019')

first_name = driver.find_element_by_xpath("//*[@id='id8']/ol/li[9]/div/input")
first_name.send_keys('Jefferson')

surname = driver.find_element_by_xpath("//*[@id='id8']/ol/li[10]/div/input")
surname.send_keys('Allan')

dob = driver.find_element_by_id('dateOfBirthPicker')
dob.send_keys('01/01/0001')

cont_button = driver.find_element_by_id('id5')
cont_button.click()

driver.implicitly_wait(3)
change_button = driver.find_element_by_name('manageBookingContainer:currentBookingsTable:listView:0:listViewPanel:change')
change_button.click()

test_centre = Select(driver.find_element_by_name('searchBookingContainer:siteCode'))
search_button = driver.find_element_by_name('searchBookingContainer:search')

time.sleep(0.5)

def convert24(str1):

    # Checking if last two elements of time
    # is AM and first two elements are 12
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-3]

    # remove the AM
    elif str1[-2:] == "AM":
        return str1[:-3]

    # Checking if last two elements of time
    # is PM and first two elements are 12
    elif str1[-2:] == "PM" and str1[:2] == "12":
        return str1[:-3]

    else:

        # add 12 to hours and remove PM
        return str(int(str1[:2]) + 12) + str1[2:5]

def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def get_test_time_date(input_list):
    print("GETTING TEST TIME DATE")
    i = 0
    global dates
    global times
    global dates_dt
    global times_dt
    dates = []
    times = []
    dates_dt = []
    times_dt = []
    date_pat = r'\d+/\d+/\d+'
    time_pat = r'\d+:\d+\s+\w+'
    for entry in input_list:
        date_gr = re.search(date_pat, entry)
        time_gr = re.search(time_pat, entry)
        #print(date_gr)
        #print(time_gr)
        date = date_gr.group()
        time12 = time_gr.group()
        if len(time12)<8:
            time12 = '0' + time12
        time24 = convert24(time12)
        dt_string = date + ' ' + time24
        print(dt_string)
        date_dt = datetime.strptime(date, '%d/%m/%Y').date()
        time_dt = datetime.strptime(time24, '%H:%M').time()

        print(date)
        #print(time12)
        print(time24)
        print("date_dt: ", date_dt)
        print("time_dt: ", time_dt)
        print("\n")

        dates.append(date)
        times.append(time24)

        dates_dt.append(date_dt)
        times_dt.append(time_dt)

        i = i + 1
    #print(times)
    #print(dates)
    #print(dates_dt)
    #print(dates_dt[1])
    #print(times_dt[1])


def get_test_details():
    print("GETTING TEST DETAILS")
    test_centre_select = Select(driver.find_element_by_name('searchBookingContainer:siteCode'))
    test_centre_select.select_by_visible_text(test_centre_text)
    test_centre_list = driver.find_elements_by_tag_name('option')

    time.sleep(0.5)
    search_button = driver.find_element_by_name('searchBookingContainer:search')
    search_button.click()
    search_res = driver.find_elements_by_xpath("//*[@id='searchResultRadioLabel']")

    i = 0
    search_text = []
    for search_entry in search_res:
        search_text.append(search_entry.text)
        i = i + 1
    print(type(search_text))
    print("\n")
    print(search_text)
    print("\n")
    get_test_time_date(search_text)





def get_suitability(times, dates, early_time, late_time, early_ndays, late_ndays):
    global current_date
    global current_time
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    early_tdelt = timedelta(days = early_ndays)
    late_tdelt = timedelta(days = late_ndays)
    early_date = current_date + early_tdelt
    late_date = current_date + late_tdelt
    early_time = datetime.strptime(early_time, '%H:%M').time()
    late_time = datetime.strptime(late_time, '%H:%M').time()
    print(early_time, " ", late_time)

    global suit
    suit = [False] * len(times)
    suit_time = [True] * len(times)
    suit_date = [True] * len(times)
    for i in range(0,len(times)):
        suit_time[i] = (times_dt[i] >= early_time)&(times_dt[i] <= late_time)
        suit_date[i] = (dates_dt[i] >= early_date)&(dates_dt[i] <= late_date)
        if suit_time[i] & suit_date[i]:
            suit[i] = True

def format_data():

    test_centre_text_list = [test_centre_text] * len(times)

    cur_date_list = [current_date] * len(times)
    cur_time_list = [current_time] * len(times)

    global res_df
    res_df = pd.DataFrame({'location': test_centre_text_list,'suitability': suit,
        'date': dates, 'time': times,  'current date': cur_date_list, 'current time': cur_time_list})


def new_file():
    res_df.to_csv(str(full_path))

def append_file():
    res_df.to_csv(str(full_path), mode='a', header = False)

def save_data():
    #if there's no file for this date, create one. Otherwise save to a new file
    # "YYYY_mm_dd.csv"
    global file_string
    file_string = current_date.strftime('%Y_%m_%d') + ".csv"
    global full_path
    full_path = rootdir / file_string
    for root, dirs, files in os.walk(str(rootdir)):
        i = False
        for file in files:
            if file == file_string:
                i = True
    if i == False:
        new_file()
    else:
        append_file()

def book_test():
    booked = False
    i = 0
    while booked == False and i<len(suit):
        print(len(suit), i)
        if suit[i]==True:
            id = 'searchResultRadio' + str(i)
            test_booking_button = driver.find_element_by_id(id)
            test_booking_button.click()
            confirm_button = driver.find_element_by_name("confirm")
            confirm_button.click()
            booked = True
            print("\n\n\n\n\nBOOKED!\n\n\n\n")
            booked_bool_file = open(str(booked_path), "w")
            booked_bool_file.write("TRUE")
            booked_bool_file.close()
        i=i+1

get_test_details()
get_suitability(times, dates, earliest_time, latest_time, earliest_dfn, latest_dfn)
format_data()
save_data()
print(res_df)
book_test()

time.sleep(10)
driver.close()
quit()
exit()
