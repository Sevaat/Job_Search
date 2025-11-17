import os
from typing import Any, Self

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


class DBManager:
    def __init__(self) -> None:
        load_dotenv()
        self.conn_params = {
            "dbname": os.getenv("DBNAME"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
            "host": os.getenv("HOST"),
            "port": os.getenv("PORT"),
        }
        self.conn: Any = None

    def _connect(self) -> None:
        """
        Установить соединение с БД, если его нет или оно закрыто
        :return:
        """
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)

    def __enter__(self) -> Self:
        self._connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.conn:
            self.conn.close()

    def get_companies_and_vacancies_count(self) -> str:
        """
        Получить список всех компаний с количеством вакансий
        :return: список компаний с количеством вакансий
        """
        self._connect()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, COUNT(v.vacancy_id) as vacancies_count
                FROM companies c
                LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.company_id, c.name
                ORDER BY vacancies_count DESC;
            """
            )
            text_list = []
            for d in [dict(row) for row in cur.fetchall()]:
                text = f"Наименование организации: {d['name']}\n"
                text += f"Количество вакансий от организации: {d['vacancies_count']}"
                text_list.append(text)
            return "\n".join(text_list)

    def get_all_vacancies(self) -> str:
        """
        Получить все вакансии с названием компании, названием вакансии, ЗП, ссылкой
        :return: список данных о вакансиях
        """
        self._connect()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    c.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
                ORDER BY v.published_at DESC;
            """
            )
            text_list = []
            for d in [dict(row) for row in cur.fetchall()]:
                text = f"Наименование организации: {d['company_name']}\n"
                text += f"Наименование вакансии: {d['vacancy_name']}"
                text += f"Заработная плата, {d['currency']}: {d['salary_from']}-{d['salary_to']}\n"
                text += f"Ссылка на hh.ru вакансии: {d['url']}"
                text_list.append(text)
            return "\n".join(text_list)

    def get_avg_salary(self) -> str:
        """
        Получить среднюю зарплату по всем вакансиям
        :return: средняя ЗП
        """
        self._connect()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    AVG(
                        COALESCE(salary_from, 0) + COALESCE(salary_to, 0)
                    ) / 2 AS avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
            """
            )
            result = cur.fetchone()
            return (
                f'Средняя зарплата по всем вакансиям: {float(result["avg_salary"]) if result["avg_salary"] else 0.0}'
            )

    def get_vacancies_with_higher_salary(self) -> str:
        """
        Получить вакансии, где хотя бы одна граница зарплаты > средней
        :return: список вакансий
        """
        avg_salary = self.get_avg_salary()
        self._connect()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    c.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
                WHERE 
                    (v.salary_from IS NOT NULL AND v.salary_from > %s) OR
                    (v.salary_to IS NOT NULL AND v.salary_to > %s)
                ORDER BY GREATEST(v.salary_from, v.salary_to) DESC;
            """,
                (avg_salary, avg_salary),
            )
            text_list = []
            for d in [dict(row) for row in cur.fetchall()]:
                text = f"Наименование организации: {d['company_name']}\n"
                text += f"Наименование вакансии: {d['vacancy_name']}"
                text += f"Заработная плата, {d['currency']}: {d['salary_from']}-{d['salary_to']}\n"
                text += f"Ссылка на hh.ru вакансии: {d['url']}"
                text_list.append(text)
            return "\n".join(text_list)

    def get_vacancies_with_keyword(self, keyword: str) -> str:
        """
        Получить вакансии, в названии которых есть слово (регистронезависимо)
        :param keyword: список вакансий
        :return:
        """
        self._connect()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    c.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
                WHERE LOWER(v.name) LIKE LOWER(%s)
                ORDER BY v.published_at DESC;
            """,
                (f"%{keyword}%",),
            )
            text_list = []
            for d in [dict(row) for row in cur.fetchall()]:
                text = f"Наименование организации: {d['company_name']}\n"
                text += f"Наименование вакансии: {d['vacancy_name']}"
                text += f"Заработная плата, {d['currency']}: {d['salary_from']}-{d['salary_to']}\n"
                text += f"Ссылка на hh.ru вакансии: {d['url']}"
                text_list.append(text)
            return "\n".join(text_list)
