from unittest.mock import Mock, patch, MagicMock

from src.db_manager import DBManager

@patch("src.db_manager.psycopg2.connect")
@patch("src.db_manager.load_dotenv")
def test_connect(mock_load_dotenv, mock_connect):
    # тест на подключение к БД
    dbm = DBManager()
    dbm.conn = None
    mock_connect.return_value = Mock(closed=False)
    dbm._connect()
    mock_connect.assert_called_once()

def test_enter_exit_context():
    # тест на отключение от БД
    with patch("src.db_manager.psycopg2.connect", return_value=Mock(closed=False)) as mock_connect:
        dbm = DBManager()
        with dbm as manager:
            assert manager.conn is not None
        manager.conn.close.assert_called_once()

@patch("src.db_manager.psycopg2.connect")
def test_get_companies_and_vacancies_count(mock_connect, company_rows):
    # тест на запрос по компаниям и количеству вакансий
    dbm = DBManager()
    mocked_conn = MagicMock()
    mocked_cur = MagicMock()
    mocked_conn.cursor.return_value.__enter__.return_value = mocked_cur
    mock_connect.return_value = mocked_conn

    mocked_cur.fetchall.return_value = [company_rows[0], company_rows[1]]
    result = dbm.get_companies_and_vacancies_count()
    assert "Компания А" in result and "2" in result
    assert "Компания Б" in result and "1" in result

@patch("src.db_manager.psycopg2.connect")
def test_get_all_vacancies(mock_connect, vacancy_rows):
    # тест на получение всех вакансий
    dbm = DBManager()
    mocked_conn = MagicMock()
    mocked_cur = MagicMock()
    mocked_conn.cursor.return_value.__enter__.return_value = mocked_cur
    mock_connect.return_value = mocked_conn
    mocked_cur.fetchall.return_value = [vacancy_rows[0]]
    result = dbm.get_all_vacancies()
    assert "Python Developer" in result and "100000-150000" in result

@patch("src.db_manager.psycopg2.connect")
def test_get_avg_salary_str_and_float(mock_connect, salary_row):
    # тест на получение средней ЗП по вакансиям
    dbm = DBManager()
    mocked_conn = MagicMock()
    mocked_cur = MagicMock()
    mocked_conn.cursor.return_value.__enter__.return_value = mocked_cur
    mock_connect.return_value = mocked_conn
    mocked_cur.fetchone.return_value = salary_row
    result_str = dbm.get_avg_salary(is_float=False)
    result_float = dbm.get_avg_salary(is_float=True)
    assert "120000.0" in result_str
    assert result_float == 120000.0

@patch("src.db_manager.psycopg2.connect")
def test_get_vacancies_with_higher_salary(mock_connect, vacancy_rows):
    # тест на поиск ЗП выше средней
    dbm = DBManager()
    mocked_conn = MagicMock()
    mocked_cur = MagicMock()
    mocked_conn.cursor.return_value.__enter__.return_value = mocked_cur
    mock_connect.return_value = mocked_conn
    mocked_cur.fetchone.return_value = {"avg_salary": 100000}
    mocked_cur.fetchall.return_value = [vacancy_rows[0]]
    with patch.object(DBManager, "get_avg_salary", return_value=100000.0):
        result = dbm.get_vacancies_with_higher_salary()
    assert "Python Developer" in result

@patch("src.db_manager.psycopg2.connect")
def test_get_vacancies_with_keyword(mock_connect, vacancy_rows):
    # тест на поиск по ключевому слову
    dbm = DBManager()
    mocked_conn = MagicMock()
    mocked_cur = MagicMock()
    mocked_conn.cursor.return_value.__enter__.return_value = mocked_cur
    mock_connect.return_value = mocked_conn
    mocked_cur.fetchall.return_value = [vacancy_rows[0]]
    result = dbm.get_vacancies_with_keyword("Python")
    assert "Python Developer" in result