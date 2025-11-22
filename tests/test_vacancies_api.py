import pytest
from unittest.mock import patch, Mock
from src.vacancies_api import VacanciesAPI

@patch('requests.get')
def test_fetch_company_data(mock_get, sample_company_data):
    # тест на получение данных компаний
    mock_response = Mock()
    mock_response.json.return_value = sample_company_data
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = VacanciesAPI._fetch_company_data(123)

    mock_get.assert_called_once_with(
        'https://api.hh.ru/employers/123',
        headers={'User-Agent': 'HH-Data-Parser/1.0'}
    )
    assert result == sample_company_data

@patch('requests.get')
def test_fetch_vacancies_by_company(mock_get, sample_vacancies_page_1, sample_vacancies_page_2):
    # тест на получение вакансий с пагинацией
    mock_response1 = Mock()
    mock_response1.json.return_value = sample_vacancies_page_1
    mock_response1.raise_for_status = Mock()

    mock_response2 = Mock()
    mock_response2.json.return_value = sample_vacancies_page_2
    mock_response2.raise_for_status = Mock()

    mock_get.side_effect = [mock_response1, mock_response2]

    results = VacanciesAPI._fetch_vacancies_by_company(123)

    assert len(results) == 2
    assert results[0]['id'] == 'vac1'
    assert results[1]['id'] == 'vac2'

@patch('requests.get')
def test_collect_all_data_success(mock_get, sample_company_data, sample_vacancies_page_1, sample_vacancies_page_2):
    # полный сбор данных с успешными запросами
    mock_company_response = Mock()
    mock_company_response.json.return_value = sample_company_data
    mock_company_response.raise_for_status = Mock()

    mock_vacancies_response1 = Mock()
    mock_vacancies_response1.json.return_value = sample_vacancies_page_1
    mock_vacancies_response1.raise_for_status = Mock()

    mock_vacancies_response2 = Mock()
    mock_vacancies_response2.json.return_value = sample_vacancies_page_2
    mock_vacancies_response2.raise_for_status = Mock()

    mock_get.side_effect = [mock_company_response, mock_vacancies_response1, mock_vacancies_response2]

    companies, vacancies = VacanciesAPI.collect_all_data([123])

    assert len(companies) == 1
    assert companies[0]['company_id'] == 123
    assert len(vacancies) == 2
    assert vacancies[0]['vacancy_id'] == 'vac1'
    assert vacancies[1]['vacancy_id'] == 'vac2'

@patch('requests.get')
def test_collect_all_data_exception_handling(mock_get):
    # обработку исключений при сбое API
    mock_get.side_effect = Exception('API failure')

    companies, vacancies = VacanciesAPI.collect_all_data([999])

    assert companies == []
    assert vacancies == []