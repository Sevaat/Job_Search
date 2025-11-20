from unittest.mock import Mock, patch
from src.database_creator import DatabaseCreator, CREATE_TABLES_SQL

def setup_mock_conn():
    mock_cur = Mock()
    mock_context_manager = Mock()
    mock_context_manager.__enter__ = Mock(return_value=mock_cur)
    mock_context_manager.__exit__ = Mock(return_value=None)
    mock_conn = Mock()
    mock_conn.cursor = Mock(return_value=mock_context_manager)
    return mock_conn, mock_cur

def test_create_tables():
    # тест на создание таблиц
    mock_conn, mock_cur = setup_mock_conn()
    DatabaseCreator._create_tables(mock_conn)
    mock_cur.execute.assert_called_once_with(CREATE_TABLES_SQL)
    mock_conn.commit.assert_called_once()

def test_insert_companies(companies):
    # тест на добавление данных компаний
    mock_conn, mock_cur = setup_mock_conn()
    DatabaseCreator._insert_companies(mock_conn, companies)
    mock_conn.commit.assert_called_once()
    mock_cur.execute.assert_called_once()
    args, kwargs = mock_cur.execute.call_args
    assert "INSERT INTO companies" in args[0]
    assert args[1][0] == companies[0]["company_id"]

def test_insert_vacancies(vacancies):
    # тест на добавление данных вакансий
    mock_conn, mock_cur = setup_mock_conn()
    DatabaseCreator._insert_vacancies(mock_conn, vacancies)
    mock_conn.commit.assert_called_once()
    mock_cur.execute.assert_called_once()
    args, kwargs = mock_cur.execute.call_args
    assert "INSERT INTO vacancies" in args[0]
    assert args[1][0] == vacancies[0]["vacancy_id"]

@patch("src.database_creator.psycopg2.connect")
@patch("src.database_creator.load_dotenv")
def test_create_databases(mock_load_dotenv, mock_connect, companies, vacancies):
    # тест на полную работу
    mock_conn, _ = setup_mock_conn()
    mock_connect.return_value = mock_conn
    DatabaseCreator.create_databases(companies, vacancies)
    assert mock_connect.called
    assert mock_conn.close.called