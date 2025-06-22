import argparse
import csv

from tabulate import tabulate


def load_csv(file_path: str) -> list[dict]:
    """Загрузка CSV-файла в список словарей"""
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)


def parse_where_condition(where_str: str):
    """Разбор условия WHERE на компоненты"""
    operators_list = ('>=', '<=', '>', '<', '=')

    for operator in operators_list:
        if operator in where_str:
            column, value = where_str.split(operator, 1)
            return column.strip(), operator, value.strip()

    raise ValueError(f"Неизвестный оператор в условии WHERE: {where_str}")


def filter_data(data: list[dict], column: str, operator: str, value: str) -> list:
    """Фильтрация данных по условию"""
    filtered = []
    for row in data:
        if column not in row:
            continue

        numeric = False
        cell_value = row[column]

        # проверка числовое ли значение в строке
        if cell_value.replace('.', '').replace(',', '').isdigit():
            cell_value_num = float(cell_value)
            value_num = float(value)
            numeric = True

        if operator == '=':
            if numeric:
                if cell_value_num == value_num:
                    filtered.append(row)
            else:
                if cell_value == value:
                    filtered.append(row)
        elif operator == '>':
            if numeric and cell_value_num > value_num:
                filtered.append(row)
        elif operator == '<':
            if numeric and cell_value_num < value_num:
                filtered.append(row)
        elif operator == '>=':
            if numeric and cell_value_num >= value_num:
                filtered.append(row)
        elif operator == '<=':
            if numeric and cell_value_num <= value_num:
                filtered.append(row)
    return filtered


def aggregate_data(data: list[dict], operation: str) -> list[dict] | None:
    """Агрегация данных по указанной операции"""
    values = []
    if '=' in operation:
        column, operator = operation.split('=')
        for row in data:
            try:
                values.append(float(row[column]))
            except (ValueError, KeyError):
                continue
    else:
        raise ValueError(f"Неизвестный оператор в условии AGGREGATE: {operation}")

    if not values:
        return None

    if operator == 'avg':
        return [{'avg': sum(values) / len(values)}]
    elif operator == 'min':
        return [{'min': min(values)}]
    elif operator == 'max':
        return [{'max': max(values)}]
    else:
        raise ValueError(f"Недопустимая операция агрегации: {operator}")


def main():
    parser = argparse.ArgumentParser(description='Обработка CSV-файлов')
    parser.add_argument('--file', help='Путь к CSV-файлу')

    # Группа для фильтрации
    filter_group = parser.add_argument_group('Фильтрация')
    filter_group.add_argument('--where', help='Условие фильтрации')

    # # Группа для агрегации
    agg_group = parser.add_argument_group('Агрегация')
    agg_group.add_argument('--aggregate', help='Условие агрегации')

    args = parser.parse_args()

    data = load_csv(args.file)

    if args.where:
        try:
            column, operator, value = parse_where_condition(args.where)
            data = filter_data(data, column, operator, value)
        except ValueError as e:
            print(f"Ошибка в условии WHERE: {e}")
            return

    # Применение агрегации, если указаны параметры
    if args.aggregate:
        result = aggregate_data(data, args.aggregate)
        if result is not None:
            print(tabulate(result, headers="keys", tablefmt="grid"))
        else:
            print("Невозможно выполнить агрегацию - нет числовых данных")
    else:
        # Вывод отфильтрованных данных, если не было агрегации
        if data:
            print(tabulate(data, headers="keys", tablefmt="grid"))
        else:
            print("Нет данных, соответствующих условиям фильтрации")


if __name__ == '__main__':
    main()
