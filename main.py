import sys
from typing import List

from src.db_manager import DBManager
from src.database_creator import DatabaseCreator
from src.vacancies_api import VacanciesAPI
from src.utils import is_convertible_to_id

if __name__ == "__main__":
    print("Вас приветствует пользовательский интерфейс программы 'Job_Search', необходимая для поиска вакансий!")
    print("Введите ID интересующих Вас организаций через запятую.")
    company_ids: List[int] = [] # [1740, 3529, 41, 65, 2180, 4181, 2748, 78638, 84585, 1122462]
    for i in range(10):
        print("Пример ввода ID организаций '3529, 15478, 2180, 87021, 4181'.")
        company_ids_text = input()
        company_ids_text = company_ids_text.split(',')
        if all(is_convertible_to_id(cidt.strip()) for cidt in company_ids_text):
            company_ids = [int(cidt.strip()) for cidt in company_ids_text]
            print("ID организаций успешно добавлены.")
        else:
            print("Ошибка ввода ID организаций. Попробуйте еще раз.")
    if len(company_ids):
        print("Прекращение работы программы. Обратитесь к администратору.")
        sys.exit()

    # собираем данные
    companies, vacancies = VacanciesAPI.collect_all_data(company_ids)
    print("Данные организаций и вакансий собраны.")

    # подключаемся к БД и создаём таблицы
    DatabaseCreator.create_databases(companies, vacancies)

    # работа с db_manager
    dbm = DBManager()
    while True:
        print("\nКакую операцию вы хотите произвести (введите номер интересующей операции)?")
        print("1 - Получить список всех компаний с количеством вакансий")
        print("2 - Получить все вакансии с названием компании, названием вакансии, ЗП, ссылкой")
        print("3 - Получить среднюю зарплату по всем вакансиям")
        print("4 - Получить вакансии, где хотя бы одна граница зарплаты > средней")
        print("5 - Получить вакансии, в названии которых есть слово")

        print()
        answer = input()
        if answer == "1":
            print("\nCписок всех компаний с количеством вакансий:")
            print(dbm.get_companies_and_vacancies_count())
        elif answer == "2":
            print("\nВсе вакансии с названием компании, названием вакансии, ЗП, ссылкой:")
            print(dbm.get_all_vacancies())
        elif answer == "3":
            print()
            print(dbm.get_avg_salary())
        elif answer == "4":
            print("\nВакансии, где хотя бы одна граница зарплаты > средней:")
            print(dbm.get_vacancies_with_higher_salary())
        elif answer == "5":
            print("\nВведите слово для поиска:")
            word = input()
            print("Вакансии, в названии которых есть слово:")
            print(dbm.get_vacancies_with_keyword(word))
        else:
            print("Пользовательский запрос не распознан, пожалуйста повторите запрос.")
            continue

        print("\nПродолжить работу с программой (1 - Да, 2 - Нет)?")
        answer = input()
        if answer == "1":
            continue
        elif answer == "2":
            break