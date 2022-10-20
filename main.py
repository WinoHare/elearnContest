import csv
import math
import re
import prettytable
import datetime

titles = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад', 'Название региона',
          'Дата публикации вакансии']

translate = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет", "between3And6": "От 3 до 6 лет",
             "moreThan6": "Более 6 лет", "AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро",
             "GEL": "Грузинский лари", "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли", "UAH": "Гривны",
             "USD": "Доллары", "UZS": "Узбекский сум", "TRUE": 'Без вычета налогов', "True": 'Без вычета налогов',
             "FALSE": 'С вычетом налогов', "False": 'С вычетом налогов'
             }
reversedTranslate = dict(zip(translate.values(), translate.keys()))

experience_rate = {"noExperience": 0, "between1And3": 1, "between3And6": 2, "moreThan6": 3}

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}


def premium_yes_no(premium: str) -> str:
    return 'Да' if premium == 'True' else 'Нет'


def reverse_premium(premium: str) -> str:
    return 'True' if premium == 'Да' else 'False'


filter_parameters = {
    '': lambda vacancies, some_param: vacancies,
    "Навыки": lambda vacancies, skills: filter(lambda v: all(s in v.key_skills for s in skills), vacancies),
    "Оклад": lambda vacancies, salary: filter(lambda v: v.salary_from <= math.floor(float(salary)) <= v.salary_to,
                                              vacancies),
    "Дата публикации вакансии": lambda vacancies, date:
    filter(lambda v: v.published_at.strftime('%d.%m.%Y') == date, vacancies),
    "Опыт работы": lambda vacancies, experience:
    filter(lambda v: v.experience_id == reversedTranslate[experience], vacancies),
    "Премиум-вакансия": lambda vacancies, premium: filter(lambda v: v.premium == reverse_premium(premium), vacancies),
    "Идентификатор валюты оклада": lambda vacancies, currency:
    filter(lambda v: v.salary_currency == reversedTranslate[currency], vacancies),
    "Название": lambda vacancies, name: filter(lambda v: v.name == name, vacancies),
    "Название региона": lambda vacancies, area: filter(lambda v: v.area_name == area, vacancies),
    "Компания": lambda vacancies, employer_name: filter(lambda v: v.employer_name == employer_name, vacancies)
}

sort_parameters = {
    'Название': lambda vacancie: vacancie.name,
    'Описание': lambda vacancie: vacancie.description,
    'Навыки': lambda vacancie: len(vacancie.key_skills),
    'Опыт работы': lambda vacancie: experience_rate[vacancie.experience_id],
    'Премиум-вакансия': lambda vacancie: vacancie.premium,
    'Компания': lambda vacancie: vacancie.employer_name,
    'Оклад': lambda vacancie: vacancie.salary_average,
    'Название региона': lambda vacancie: vacancie.area_name,
    'Дата публикации вакансии': lambda vacancie:
    (vacancie.published_at.strftime('%Y.%m.%d'), vacancie.published_at.strftime('%H.%M.%S'))
}


class Vacancie:
    def __init__(self, args):
        self.name = args[0]
        self.description = args[1]
        self.key_skills = args[2].split('\n')
        self.experience_id = args[3]
        self.premium = args[4]
        self.employer_name = args[5]
        self.salary_from = math.floor(float(args[6]))
        self.salary_to = math.floor(float(args[7]))
        self.salary_gross = args[8]
        self.salary_currency = args[9]
        self.salary_average = math.floor((self.salary_from + self.salary_to) / 2) \
                              * currency_to_rub[self.salary_currency]
        self.area_name = args[10]
        self.published_at = datetime.datetime(int(args[11][0:4]), int(args[11][5:7]), int(args[11][8:10]),
                                              int(args[11][11:13]), int(args[11][14:16]), int(args[11][17:19]))

    def get_russian_format(self) -> list:
        return [self.name, cut_line(self.description), cut_line('\n'.join(self.key_skills)),
                translate[self.experience_id], premium_yes_no(self.premium), self.employer_name,
                f'{format_number(self.salary_from)} - {format_number(self.salary_to)}'
                f' ({translate[self.salary_currency]}) ({translate[self.salary_gross]})',
                self.area_name, self.published_at.strftime('%d.%m.%Y')]


def is_correct_line(line: list, header_length: int) -> bool:
    return '' not in line and len(line) == header_length


def clean_line(line: str) -> str:
    line = re.sub('<[^<]+?>', '', line)
    line = line.replace('\xa0', ' ')
    line = line.replace(" ", ' ')
    while '  ' in line:
        line = line.replace('  ', ' ')
    line = line.strip()
    return line


def cut_line(line: str) -> str:
    return line[0:100] + '...' if len(line) > 100 else line


def format_number(number: int) -> str:
    return '{:3,d}'.format(number).replace(',', ' ')


def get_input_values() -> str or tuple:
    file_name = input('Введите название файла: ')
    filter_parameter = input('Введите параметр фильтрации: ')
    key, value = '', ''
    if ': ' in filter_parameter:
        key, value = filter_parameter.split(': ')
        if key == "Навыки":
            value = value.split(', ')

    sort_parameter = input('Введите параметр сортировки: ')

    sort_direction = input('Обратный порядок сортировки (Да / Нет): ')
    if sort_direction == 'Да':
        sort_direction = True
    elif sort_direction == 'Нет' or sort_direction == '':
        sort_direction = False

    start = 0
    end = 100000000000
    range_to_print = input('Введите диапазон вывода: ').split()
    if len(range_to_print) == 2:
        start, end = int(range_to_print[0]) - 1, int(range_to_print[1]) - 1
    elif len(range_to_print) == 1:
        start = int(range_to_print[0]) - 1

    titles_to_print = input('Введите требуемые столбцы: ')
    titles_to_print = titles_to_print.split(', ') if len(titles_to_print) > 1 else titles_to_print

    if filter_parameter != '' and ': ' not in filter_parameter:
        return "Формат ввода некорректен"
    if key != '' and key not in filter_parameters:
        return "Параметр поиска некорректен"
    if sort_parameter not in titles and sort_parameter != '':
        return "Параметр сортировки некорректен"
    if type(sort_direction) != bool:
        return "Порядок сортировки задан некорректно"
    return file_name, key, value, sort_parameter, sort_direction, start, end, titles_to_print


def filter_vacancies(vacancies: list, filter_key, filter_value) -> list or str:
    filtered_vacancies = list(filter_parameters[filter_key](vacancies, filter_value))
    return "Ничего не найдено" if len(filtered_vacancies) == 0 else filtered_vacancies


def sort_vacancies(vacancies, param, is_rev) -> list:
    return vacancies if param == '' else sorted(vacancies, key=sort_parameters[param], reverse=bool(is_rev))


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


def print_table(vacancies: list, data) -> None:
    counter = 0
    table = prettytable.PrettyTable(
        hrules=prettytable.ALL,
        align='l',
        field_names=['№'] + titles,
        max_width=20)
    vacancies = filter_vacancies(vacancies, data[1], data[2])
    if type(vacancies) == str:
        print(vacancies)
        return
    vacancies = sort_vacancies(vacancies, data[3], data[4])
    for vacancie in vacancies:
        counter += 1
        table.add_row([counter] + vacancie.get_russian_format())
    print(table.get_string(start=data[5], end=data[6],
                           fields=['№'] + data[7] if len(data[7]) != 0 else ['№'] + table.field_names))


def RussianPrint(fn):
    def print_russian():
        input_values = get_input_values()
        if type(input_values) == str:
            print(input_values)
            return
        vacancies = fn(input_values[0])
        if vacancies is None:
            return
        else:
            print_table(vacancies, input_values)

    return print_russian


@RussianPrint
def parse_csv(file_name: str) -> list or None:
    header, vacancies = csv_reader(file_name)
    if len(header) == 0:
        print('Пустой файл')
        return
    vacancies = formatter(vacancies)
    if len(vacancies) == 0:
        print('Нет данных')
        return
    return vacancies


parse_csv()
