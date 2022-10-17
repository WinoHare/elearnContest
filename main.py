import csv
import math
import re
import prettytable
import datetime

titles = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад', 'Название региона',
          'Дата публикации вакансии']

experience_dictionary = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет",
                         "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"}

currency_dictionary = {"AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро", "GEL": "Грузинский лари",
                       "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли", "UAH": "Гривны", "USD": "Доллары",
                       "UZS": "Узбекский сум"}


def premium_yes_no(premium: str) -> str:
    return 'Да' if premium == 'True' else 'Нет'


def tax_yes_no(tax: str) -> str:
    return 'Без вычета налогов' if tax == 'TRUE' or tax == 'True' else 'С вычетом налогов'


filter_parameters = {
    "Навыки": lambda vacancies, skills: filter(lambda v: all(s in v.key_skills for s in skills), vacancies),
    "Оклад": lambda vacancies, salary: filter(lambda v: v.salary_from <= math.floor(float(salary)) <= v.salary_to,
                                              vacancies),
    "Дата публикации вакансии": lambda vacancies, date: filter(lambda v: v.published_at == date, vacancies),
    "Опыт работы": lambda vacancies, experience:
    filter(lambda v: v.experience_id == experience, vacancies),
    "Премиум-вакансия": lambda vacancies, premium: filter(lambda v: v.premium == premium, vacancies),
    "Идентификатор валюты оклада": lambda vacancies, currency:
    filter(lambda v: v.salary_currency == currency, vacancies),
    "Название": lambda vacancies, name: filter(lambda v: v.name == name, vacancies),
    "Название региона": lambda vacancies, area: filter(lambda v: v.area_name == area, vacancies),
    "Компания": lambda vacancies, employer_name: filter(lambda v: v.employer_name == employer_name, vacancies)
}


class Vacancie:
    def __init__(self, args):
        self.name = args[0]
        self.description = args[1]
        self.key_skills = args[2].split('\n')
        self.experience_id = experience_dictionary[args[3]]
        self.premium = premium_yes_no(args[4])
        self.employer_name = args[5]
        self.salary_from = math.floor(float(args[6]))
        self.salary_to = math.floor(float(args[7]))
        self.salary_gross = tax_yes_no(args[8])
        self.salary_currency = currency_dictionary[args[9]]
        self.area_name = args[10]
        self.published_at = datetime.date(int(args[11][0:4]), int(args[11][5:7]), int(args[11][8:10])).strftime(
            '%d.%m.%Y')

    def get_formatted_vacancie(self) -> list:
        return [self.name, cut_line(self.description), cut_line('\n'.join(self.key_skills)),
                self.experience_id, self.premium, self.employer_name,
                f'{format_number(self.salary_from)} - {format_number(self.salary_to)} ({self.salary_currency}) ({self.salary_gross})',
                self.area_name, self.published_at]


def is_correct_line(line: list, header_length: int) -> bool:
    return '' not in line and len(line) == header_length


def clean_line(line: str) -> str:
    line = re.sub('<[^<]+?>', '', line)
    while '\xa0' in line:
        line = line.replace('\xa0', ' ')
    while '  ' in line:
        line = line.replace('  ', ' ')
    line = line.strip()
    return line


def cut_line(line: str) -> str:
    return line[0:100] + '...' if len(line) > 100 else line


def format_number(number: int) -> str:
    number = str(number)
    length = len(number)
    return f'{number[0:length - 3]} {number[length - 3: length]}' if length > 3 else f'{number[length - 3: length]}'


def get_input_values(vacancies_length: int) -> tuple:
    filter_parameter = input()

    start_position = 0
    end_position = vacancies_length
    range_to_print = input().split()
    if len(range_to_print) == 2:
        start_position, end_position = int(range_to_print[0]) - 1, int(range_to_print[1]) - 1
    elif len(range_to_print) == 1:
        start_position = int(range_to_print[0]) - 1

    titles_to_print = input()
    titles_to_print = titles_to_print.split(', ') if len(titles_to_print) > 1 else titles_to_print

    return filter_parameter, start_position, end_position, titles_to_print


def csv_reader(file_name: str) -> tuple:
    is_header = True
    vacancies = []
    header = []
    header_length = 0
    with open(file_name, encoding='utf-8') as csv_file:
        file = csv.reader(csv_file)
        for row in file:
            if is_header:
                is_header = False
                header = row
                header_length = len(header)
                continue
            if is_correct_line(row, header_length):
                vacancies.append(row)
    return header, vacancies


def formatter(rows: list) -> list:
    return list(map(lambda r: Vacancie(list(map(lambda t: clean_line(t), r))), rows))


def filter_vacancies(vacancies: list, filter_parameter: str) -> list or str:
    if filter_parameter == '':
        return vacancies

    if ': ' in filter_parameter:
        filter_key, filter_value = filter_parameter.split(': ')
        if filter_key == "Навыки":
            filter_value = filter_value.split(', ')
    else:
        return "Формат ввода некорректен"
    if filter_key not in filter_parameters:
        return "Параметр поиска некорректен"

    filtered_vacancies = list(filter_parameters[filter_key](vacancies, filter_value))
    if len(filtered_vacancies) == 0:
        return "Ничего не найдено"
    return filtered_vacancies


def print_table(vacancies: list) -> None:
    counter = 0
    table = prettytable.PrettyTable(
        hrules=prettytable.ALL,
        align='l',
        field_names=['№'] + titles,
        max_width=20)
    table_data = get_input_values(len(vacancies))
    filtered_vacancies = filter_vacancies(vacancies, table_data[0])
    if type(filtered_vacancies) == str:
        print(filtered_vacancies)
        return
    for vacancie in filtered_vacancies:
        counter += 1
        table.add_row([counter] + vacancie.get_formatted_vacancie())
    print(table.get_string(start=table_data[1], end=table_data[2],
                           fields=['№'] + table_data[3] if len(table_data[3]) != 0 else ['№'] + table.field_names))


def parse_csv(file_name: str) -> None:
    header, vacancies = csv_reader(file_name)
    if len(header) == 0:
        print('Пустой файл')
        return
    vacancies = formatter(vacancies)
    if len(vacancies) == 0:
        print('Нет данных')
        return
    print_table(vacancies)


parse_csv(input())
