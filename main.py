import pandas as pd
import openpyxl
import numpy as np
import pyarrow
import time
import datetime
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import wait
from selenium.webdriver.support.wait import WebDriverWait

bef_des_post_date = input('Digite a data anterior à data desejada (Ex.: desejada = 2/17/2024, seu input = 2/16/2024) (m/d/a): ')


def job_scraper():
    driver = webdriver.Chrome(options=Options())
    wait = WebDriverWait(driver, 10)
    url = "https://seasonaljobs.dol.gov/archive?search=&location=&start_date=&job_type=H-2A&sort=accepted_date&job_status=active"
    driver.get(url)


    # A posterior busca só funciona se descer a página até que os empregos estejam à vista
    iframe = driver.find_element(By.XPATH, '//*[@id="find-jobs"]/div[2]/form/div[1]/div/button[2]')
    scroll_origin = ScrollOrigin.from_element(iframe)
    ActionChains(driver) \
        .scroll_from_origin(scroll_origin, 0, 600) \
        .perform()


    # Iterar sobre os empregos
    i = 1
    data = []
    while True:
        #temp_data = []
        #time.sleep(3)

        # Clicar no emprego
        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-content"]/div/div[1]/div[2]/div/article[{}]'.format(i))))
        job_button = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div[1]/div[2]/div/article[{}]'.format(i))
        job_button.click()

        # Descer a barra de rolagem dentro dos empregos
        if i>1:
            iframe = job_button
            scroll_origin = ScrollOrigin.from_element(iframe)
            ActionChains(driver) \
                .scroll_from_origin(scroll_origin, 0, 156) \
                .perform()


        # Comparar data de postagem
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="job-detail"]/section/section[5]/dl/div[3]/dd')))
        post_date = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/section[5]/dl/div[3]/dd')
        if post_date.text == bef_des_post_date:
            break
        else:
            localization_raw = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/div[1]/div[1]/div/p[2]').text
            wage_raw = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/div[1]/div[1]/p').text

            job_name = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/a/h2').text
            city = localization_raw.rsplit(',')[0]
            state = localization_raw.rsplit(',')[1].strip()
            #wage = wage_raw.rsplit(" ")[0].lstrip("$").replace(",", "")

            contact_info = ''
            contact_sec = driver.find_elements(By.XPATH, '//*[@id="job-detail"]/section/address/section/dl')
            for element in contact_sec:
                contact_info = contact_info + element.text

            #contact_info_1 = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/address/section/dl/div[1]/dd/a').text
            #contact_info_2 = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/address/section/dl/div[2]/dd/a').text
            link = driver.find_element(By.XPATH, '//*[@id="job-detail"]/section/section[6]/div[1]/input').get_attribute('value')
            data.append([job_name, city, state, wage_raw, contact_info, link])

        i += 1
    return data


def write_excel(data):
    df = pd.DataFrame(data, columns=['Job', 'City', 'State', 'Wage', 'Contact Info', 'Link'])
    df.to_excel("job_search.xlsx")


def main():
    write_excel(job_scraper())


if __name__ == "__main__":
    main()
