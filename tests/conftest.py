import pytest


@pytest.fixture
def sample_company_data():
    return {
        "id": 123,
        "name": "Test Company",
        "alternate_url": "http://company.url",
        "description": "A test company",
        "site_url": "http://site.url"
    }


@pytest.fixture
def sample_vacancies_page_1():
    return {
        "items": [
            {
                "id": "vac1",
                "name": "Vacancy 1",
                "salary": {"from": 1000, "to": 2000, "currency": "RUB"},
                "alternate_url": "http://vacancy1.url",
                "area": {"name": "Moscow"},
                "published_at": "2025-01-01T12:00:00Z"
            }
        ],
        "pages": 2
    }


@pytest.fixture
def sample_vacancies_page_2():
    return {
        "items": [
            {
                "id": "vac2",
                "name": "Vacancy 2",
                "salary": None,
                "alternate_url": "http://vacancy2.url",
                "area": None,
                "published_at": "2025-01-02T12:00:00Z"
            }
        ],
        "pages": 2
    }


@pytest.fixture
def companies():
    return [
        {
            "company_id": 1,
            "name": "Test Company",
            "url": "http://testcompany.ru",
            "description": "Описание",
            "site_url": "http://site.ru"
        }
    ]


@pytest.fixture
def vacancies():
    return [
        {
            "vacancy_id": 11,
            "company_id": 1,
            "name": "Senior Developer",
            "salary_from": 100000,
            "salary_to": 200000,
            "currency": "RUB",
            "url": "http://vacancy.ru",
            "area": "Москва",
            "published_at": "2025-01-01 12:00:00"
        }
    ]
