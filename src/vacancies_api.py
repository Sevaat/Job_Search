from abc import ABC
from typing import Any, Dict, List

import requests


class VacanciesAPI(ABC):
    HH_API_URL = "https://api.hh.ru"

    def _fetch_company_data(self, company_id: int) -> Any:
        """
        Получить данные о компании по ID
        :param company_id: ID компании, вакансии которой интересуют пользователя
        :return: данные о компании
        """
        url = f"{self.HH_API_URL}/employers/{company_id}"
        response = requests.get(url, headers={"User-Agent": "HH-Data-Parser/1.0"})
        response.raise_for_status()
        return response.json()

    def _fetch_vacancies_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        """
        Получить все вакансии компании (с пагинацией)
        :param company_id: ID компании, вакансии которой интересуют пользователя
        :return: список вакансий
        """
        vacancies = []
        page = 0
        per_page = 100
        while True:
            url = f"{self.HH_API_URL}/vacancies"
            params = {
                "employer_id": company_id,
                "per_page": per_page,
                "page": page,
                "area": 113,
            }
            response = requests.get(url, headers={"User-Agent": "HH-Data-Parser/1.0"}, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            vacancies.extend(items)
            if page >= data.get("pages", 0) - 1:
                break
            page += 1
        return vacancies

    def collect_all_data(self, company_ids: List[int]) -> tuple[List[Dict], List[Dict]]:
        """
        Собрать данные по всем компаниям и вакансиям
        :return: данные компаний, вакансий
        """
        companies = []
        all_vacancies = []

        print("Сбор данных с hh.ru...")
        for cid in company_ids:
            try:
                print(f"Обрабатываем компанию ID {cid}...")
                company = self._fetch_company_data(cid)
                companies.append(
                    {
                        "company_id": company["id"],
                        "name": company["name"],
                        "url": company.get("alternate_url"),
                        "description": company.get("description"),
                        "site_url": company.get("site_url"),
                    }
                )

                vacancies = self._fetch_vacancies_by_company(cid)
                for vac in vacancies:
                    salary = vac.get("salary")
                    all_vacancies.append(
                        {
                            "vacancy_id": vac["id"],
                            "company_id": cid,
                            "name": vac["name"],
                            "salary_from": salary["from"] if salary else None,
                            "salary_to": salary["to"] if salary else None,
                            "currency": salary["currency"] if salary else None,
                            "url": vac["alternate_url"],
                            "area": vac["area"]["name"] if vac.get("area") else None,
                            "published_at": vac["published_at"],
                        }
                    )
            except Exception as e:
                print(f"Ошибка при обработке компании {cid}: {e}")

        print(f"Собрано {len(companies)} компаний и {len(all_vacancies)} вакансий.")
        return companies, all_vacancies
