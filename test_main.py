import pytest
import csv
import os
from tempfile import NamedTemporaryFile
from main import load_csv, parse_where_condition, filter_data, aggregate_data


@pytest.fixture
def sample_csv_file():
    """Фикстура создает временный CSV файл для тестов"""
    data = [
        {"name": "Alice", "age": "25", "score": "4.5"},
        {"name": "Bob", "age": "30", "score": "3.8"},
        {"name": "Charlie", "age": "35", "score": "4.2"},
    ]

    with NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "score"])
        writer.writeheader()
        writer.writerows(data)
        f.flush()

        yield f.name

    os.unlink(f.name)


def test_load_csv(sample_csv_file):
    """Тест загрузки CSV файла"""
    result = load_csv(sample_csv_file)
    assert len(result) == 3
    assert result[0]["name"] == "Alice"
    assert result[1]["age"] == "30"
    assert result[2]["score"] == "4.2"


def test_parse_where_condition():
    """Тест разбора условий WHERE"""
    assert parse_where_condition("age>25") == ("age", ">", "25")
    assert parse_where_condition("score <= 4.0") == ("score", "<=", "4.0")
    assert parse_where_condition("name=Alice") == ("name", "=", "Alice")

    with pytest.raises(ValueError):
        parse_where_condition("age!25")


def test_filter_data(sample_csv_file):
    """Тест фильтрации данных"""
    data = load_csv(sample_csv_file)

    # Фильтрация по числовому полю (age > 25)
    filtered = filter_data(data, "age", ">", "25")
    assert len(filtered) == 2
    assert filtered[0]["name"] == "Bob"
    assert filtered[1]["name"] == "Charlie"

    # Фильтрация по текстовому полю (name = Alice)
    filtered = filter_data(data, "name", "=", "Alice")
    assert len(filtered) == 1
    assert filtered[0]["age"] == "25"

    # Фильтрация с несуществующей колонкой
    filtered = filter_data(data, "nonexistent", "=", "value")
    assert len(filtered) == 0


def test_aggregate_data(sample_csv_file):
    """Тест агрегации данных"""
    data = load_csv(sample_csv_file)

    # Тест среднего значения
    result = aggregate_data(data, "score=avg")
    assert result == [{"avg": pytest.approx(4.166666, rel=1e-6)}]

    # Тест минимального значения
    result = aggregate_data(data, "age=min")
    assert result == [{"min": 25.0}]

    # Тест максимального значения
    result = aggregate_data(data, "score=max")
    assert result == [{"max": 4.5}]

    # Тест с несуществующей колонкой
    result = aggregate_data(data, "nonexistent=avg")
    assert result is None

    # Тест с некорректным оператором
    with pytest.raises(ValueError):
        aggregate_data(data, "score=unknown")


def test_aggregate_empty_data():
    """Тест агрегации с пустыми данными"""
    assert aggregate_data([], "age=avg") is None
    assert aggregate_data([{"name": "Alice"}], "age=avg") is None
