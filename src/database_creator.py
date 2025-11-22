import os
from abc import ABC
from typing import Any, Dict, List

import psycopg2
from dotenv import load_dotenv

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT,
    description TEXT,
    site_url TEXT
);

CREATE TABLE IF NOT EXISTS vacancies (
    vacancy_id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    salary_from INTEGER,
    salary_to INTEGER,
    currency VARCHAR(10),
    url TEXT,
    area VARCHAR(100),
    published_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vacancies_company ON vacancies(company_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from ON vacancies(salary_from);
CREATE INDEX IF NOT EXISTS idx_vacancies_salary_to ON vacancies(salary_to);
"""


class DatabaseCreator(ABC):
    """
    Подключиться к БД для создания таблиц
    """

    @staticmethod
    def _create_tables(conn: Any) -> None:
        """
        Создать таблицы в БД: работодатели и вакансии
        :param conn: активное соединение psycopg2
        :return:
        """
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
            conn.commit()
        print("Таблицы созданы.")

    @staticmethod
    def _insert_companies(conn: Any, companies: List[Dict]) -> None:
        """
        Загружать или обновлять данные о компаниях в таблицу companies
        :param conn: соединение с БД
        :param companies: список словарей (результат collect_all_data)
        :return:
        """
        with conn.cursor() as cur:
            for comp in companies:
                cur.execute(
                    """
                    INSERT INTO companies (company_id, name, url, description, site_url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (company_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        site_url = EXCLUDED.site_url;
                """,
                    (comp["company_id"], comp["name"], comp["url"], comp["description"], comp["site_url"]),
                )
            conn.commit()
        print(f"Загружено {len(companies)} компаний.")

    @staticmethod
    def _insert_vacancies(conn: Any, vacancies: List[Dict]) -> None:
        """
        Загружать или обновлять вакансии
        :param conn: соединение с БД
        :param vacancies: список словарей (результат collect_all_data)
        :return:
        """
        with conn.cursor() as cur:
            for vac in vacancies:
                cur.execute(
                    """
                    INSERT INTO vacancies (
                        vacancy_id, company_id, name, salary_from, salary_to,
                        currency, url, area, published_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        url = EXCLUDED.url,
                        area = EXCLUDED.area,
                        published_at = EXCLUDED.published_at;
                """,
                    (
                        vac["vacancy_id"],
                        vac["company_id"],
                        vac["name"],
                        vac["salary_from"],
                        vac["salary_to"],
                        vac["currency"],
                        vac["url"],
                        vac["area"],
                        vac["published_at"],
                    ),
                )
            conn.commit()
        print(f"Загружено {len(vacancies)} вакансий.")

    @staticmethod
    def create_databases(companies: List[Dict], vacancies: List[Dict]) -> None:
        """
        Подключиться к БД и создать таблицы
        :param companies: данные компаний
        :param vacancies: данные вакансий
        :return:
        """
        load_dotenv()
        DB_CONFIG = {
            "dbname": os.getenv("DBNAME"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
            "host": os.getenv("HOST"),
            "port": os.getenv("PORT"),
        }

        conn = psycopg2.connect(**DB_CONFIG)
        DatabaseCreator._create_tables(conn)
        DatabaseCreator._insert_companies(conn, companies)
        DatabaseCreator._insert_vacancies(conn, vacancies)
        conn.close()
