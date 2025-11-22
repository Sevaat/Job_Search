import pytest
from unittest.mock import patch
from src.user_interface import UserInterface

def test_entering_company_ids_valid(monkeypatch):
    # тест на корректный ввод на первой попытке
    inputs = ["3529, 15478, 2180", "", "", "", "", "", "", "", "", ""]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    with patch("src.utils.is_convertible_to_id", return_value=True):
        with patch("builtins.print"):
            result = UserInterface._entering_company_ids()
            assert result == [3529, 15478, 2180]

def test_entering_company_ids_invalid_then_valid(monkeypatch):
    # первая попытка - некорректный ввод, вторая - ок
    inputs = ["bad_input", "3529, 15478", "", "", "", "", "", "", "", "", ""]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    def fake_convert(idstr):
        return idstr.isdigit()

    with patch("src.utils.is_convertible_to_id", side_effect=fake_convert):
        with patch("builtins.print"):
            result = UserInterface._entering_company_ids()
            assert result == [3529, 15478]

def test_entering_company_ids_exit(monkeypatch):
    # все попытки некорректные — должен быть sys.exit
    inputs = ["bad_input"] * 10
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    with patch("src.utils.is_convertible_to_id", return_value=False):
        with patch("builtins.print"), pytest.raises(SystemExit):
            UserInterface._entering_company_ids()