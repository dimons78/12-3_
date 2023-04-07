# Уважаемые проверяющие!
# Прошу прощения! 97% кода взял из лекции Тимура

import json
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import time


def get_info(vacancy):
    city = vacancy.find('div', attrs={'data-qa': "vacancy-serp__vacancy-address"}).text.split(',')[0]
    company = vacancy.find('a', attrs={'data-qa': "vacancy-serp__vacancy-employer"}).text
    salary_raw = vacancy.find('span', attrs={'data-qa': "vacancy-serp__vacancy-compensation"})
    salary = salary_raw.text if salary_raw is not None else ''
    link = vacancy.find('a', attrs={'data-qa': "serp-item__title"})['href']

    # print(city)
    # print(company)
    # print(salary)
    # print(link)

    return {
        'city': city,
        'company': company,
        'salary': salary,
        'link': link
    }


def is_suitable(link):
    vacancy_page = requests.get(link,
                    headers=Headers(browser='chrome').generate())
    description = BeautifulSoup(vacancy_page.text, 'html.parser').find("div",
                    class_="vacancy-description").text.lower()

    return 'django' in description or 'flask' in description


item = -1

while True:
    item += 1
    try:
        page = requests.get(f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={item}',
                    headers=Headers(browser='chrome').generate())

        time.sleep(0.4)
        print(item, page.status_code)

        soup = BeautifulSoup(page.text, 'html.parser')
        vacancies = soup.find_all("div", class_="vacancy-serp-item-body__main-info")
        vacancies_info = [get_info(vacancy) for vacancy in vacancies]
        suitable_vacancies = [vacancy for vacancy in vacancies_info if is_suitable(vacancy['link'])]
        # print(len(vacancies))
        # print(vacancies[0])
        # print(len(vacancies_info))
        # print(vacancies_info[5])

        # print(len(suitable_vacancies))
        # print(suitable_vacancies[0])

        with open('data_json', 'a') as f:
            json.dump(suitable_vacancies, f, indent=1, ensure_ascii=False)


    except:
        # если существует следующая страница, то продолжаем, а иначе БРЕАК
        page_ = requests.get(f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={item + 1}',
                    headers=Headers(browser='chrome').generate())
        if page_.status_code == 200:
            continue
        else:
            break
