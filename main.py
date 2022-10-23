import csv
import math
import re
import prettytable

titles = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад', 'Название региона',
          'Дата публикации вакансии']

experience_rate = {"noExperience": 0, "between1And3": 1, "between3And6": 2, "moreThan6": 3}


filter_parameters = {
    '': lambda vacancies, some_param: vacancies,
    "Навыки": lambda vacancies, skills: filter(lambda v: all(s in v.key_skills for s in skills), vacancies),
    "Оклад": lambda vacancies, salary:
    filter(lambda v: math.floor(float(v.salary.salary_from)) <= math.floor(float(salary)) <= math.floor(float(v.salary.salary_to)), vacancies),
    "Дата публикации вакансии": lambda vacancies, date:
    filter(lambda v: f'{v.published_at[8:10]}.{v.published_at[5:7]}.{v.published_at[0:4]}' == date, vacancies),
    "Опыт работы": lambda vacancies, experience:
    filter(lambda v: v.experience_id == v.reversedTranslate[experience], vacancies),
    "Премиум-вакансия": lambda vacancies, premium: filter(lambda v: v.premium == v.reverse_premium(premium), vacancies),
    "Идентификатор валюты оклада": lambda vacancies, currency:
    filter(lambda v: v.salary.salary_currency == v.reversedTranslate[currency], vacancies),
    "Название": lambda vacancies, name: filter(lambda v: v.name == name, vacancies),
    "Название региона": lambda vacancies, area: filter(lambda v: v.area_name == area, vacancies),
    "Компания": lambda vacancies, employer_name: filter(lambda v: v.employer_name == employer_name, vacancies)
}

sort_parameters = {
    'Название': lambda vacancy: vacancy.name,
    'Описание': lambda vacancy: vacancy.description,
    'Навыки': lambda vacancy: len(vacancy.key_skills),
    'Опыт работы': lambda vacancy: experience_rate[vacancy.experience_id],
    'Премиум-вакансия': lambda vacancy: vacancy.premium,
    'Компания': lambda vacancy: vacancy.employer_name,
    'Оклад': lambda vacancy:
    math.floor((vacancy.salary.get_salary_from_in_RUR() + vacancy.salary.get_salary_to_in_RUR()) / 2),
    'Название региона': lambda vacancy: vacancy.area_name,
    'Дата публикации вакансии': lambda vacancy:
    (f'{vacancy.published_at[0:4]}.{vacancy.published_at[5:7]}.{vacancy.published_at[8:10]}',
     f'{vacancy.published_at[11:13]}.{vacancy.published_at[14:16]}.{vacancy.published_at[17:19]}')
}


class DataSet:
    def __init__(self, file_name):
        self.is_empty = False
        self.error_massage = ''
        self.file_name = file_name
        self.vacancies_objects = self.csv_reader()

    def csv_reader(self) -> tuple or None:
        is_header = True
        vacancies = []
        header = []
        header_length = 0
        with open(self.file_name, encoding='utf-8') as csv_file:
            file = csv.reader(csv_file)
            for row in file:
                if is_header:
                    is_header = False
                    header = row
                    header_length = len(header)
                    continue
                if self.is_correct_line(row, header_length):
                    vacancies.append(row)
        if len(header) == 0:
            self.is_empty = True
            self.error_massage = 'Пустой файл'
        elif len(vacancies) == 0:
            self.is_empty = True
            self.error_massage = 'Нет данных'
        return list(map(lambda r: Vacancy(list(map(lambda t: self.clean_line(t), r))), vacancies))


    def is_correct_line(self, line: list, header_length: int) -> bool:
        return '' not in line and len(line) == header_length

    def clean_line(self, line: str) -> str:
        line = re.sub('<[^<]+?>', '', line).replace('\xa0', ' ').replace(" ", ' ').strip()
        while '  ' in line:
            line = line.replace('  ', ' ')
        return line

    def filter_sort_data(self, filter_key, filter_value, sort_param, is_rev):
        self.vacancies_objects = list(filter_parameters[filter_key](self.vacancies_objects, filter_value))
        self.vacancies_objects = self.vacancies_objects if sort_param == '' \
            else sorted(self.vacancies_objects, key=sort_parameters[sort_param], reverse=bool(is_rev))


class Vacancy:
    def __init__(self, args: list):
        self.name = args[0]
        self.description = args[1]
        self.key_skills = args[2].split('\n')
        self.experience_id = args[3]
        self.premium = args[4]
        self.employer_name = args[5]
        self.salary = Salary(args[6], args[7], args[8], args[9])
        self.area_name = args[10]
        self.published_at = args[11]

    translate = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет", "between3And6": "От 3 до 6 лет",
                 "moreThan6": "Более 6 лет", "AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро",
                 "GEL": "Грузинский лари", "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли", "UAH": "Гривны",
                 "USD": "Доллары", "UZS": "Узбекский сум", "TRUE": 'Без вычета налогов', "True": 'Без вычета налогов',
                 "FALSE": 'С вычетом налогов', "False": 'С вычетом налогов'
                 }
    reversedTranslate = dict(zip(translate.values(), translate.keys()))

    def get_russian_format(self) -> list:
        return [self.name, self.cut_line(self.description), self.cut_line('\n'.join(self.key_skills)),
                self.translate[self.experience_id], self.premium_yes_no(), self.employer_name,
                f'{self.format_number(self.salary.salary_from)} - {self.format_number(self.salary.salary_to)}'
                f' ({self.translate[self.salary.salary_currency]}) ({self.translate[self.salary.salary_gross]})',
                self.area_name, f'{self.published_at[8:10]}.{self.published_at[5:7]}.{self.published_at[0:4]}']

    def premium_yes_no(self) -> str:
        return 'Да' if self.premium == 'True' else 'Нет'

    def cut_line(self, line: str) -> str:
        return line[0:100] + '...' if len(line) > 100 else line

    def format_number(self, number: int) -> str:
        return '{:3,d}'.format(math.floor(float(number))).replace(',', ' ')

    def reverse_premium(self, premium: str) -> str:
        return 'True' if premium == 'Да' else 'False'


class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

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

    def get_salary_from_in_RUR(self):
        return math.floor(float(self.salary_from) * self.currency_to_rub[self.salary_currency])

    def get_salary_to_in_RUR(self):
        return math.floor(float(self.salary_to) * self.currency_to_rub[self.salary_currency])


class InputConnect:
    def __init__(self):
        self.is_input_correct = True
        self.error_massage = ''
        self.file_name = input('Введите название файла: ')
        self.filter_key, self.filter_value = self.get_filter_parameter()
        self.sort_parameter = self.get_sort_parameter()
        self.sort_reversed = self.get_sort_reversed()
        self.range_to_print = self.get_range_to_print()
        self.titles_to_print = self.get_titles_to_print()

    def get_filter_parameter(self):
        filter_parameter = input('Введите параметр фильтрации: ')
        key, value = '', ''
        if ': ' in filter_parameter:
            key, value = filter_parameter.split(': ')
            if key == "Навыки":
                value = value.split(', ')

        if filter_parameter != '' and ': ' not in filter_parameter:
            self.error_massage = "Формат ввода некорректен"
            self.is_input_correct = False
        elif key != '' and key not in filter_parameters:
            self.error_massage = "Параметр поиска некорректен" if self.error_massage == '' else self.error_massage
            self.is_input_correct = False

        return key, value

    def get_sort_parameter(self):
        sort_parameter = input('Введите параметр сортировки: ')
        if sort_parameter not in titles and sort_parameter != '':
            self.error_massage = "Параметр сортировки некорректен" if self.error_massage == '' else self.error_massage
            self.is_input_correct = False
            return
        return sort_parameter

    def get_sort_reversed(self):
        sort_direction = input('Обратный порядок сортировки (Да / Нет): ')
        if sort_direction == 'Да':
            sort_direction = True
        elif sort_direction == 'Нет' or sort_direction == '':
            sort_direction = False
        if type(sort_direction) != bool:
            self.error_massage = "Порядок сортировки задан некорректно" if self.error_massage == '' else self.error_massage
            self.is_input_correct = False
            return
        return sort_direction

    def get_range_to_print(self):
        start = 0
        end = 100000000000
        range_to_print = input('Введите диапазон вывода: ').split()
        if len(range_to_print) == 2:
            start, end = int(range_to_print[0]) - 1, int(range_to_print[1]) - 1
        elif len(range_to_print) == 1:
            start = int(range_to_print[0]) - 1
        return start, end

    def get_titles_to_print(self):
        titles_to_print = input('Введите требуемые столбцы: ')
        return titles_to_print.split(', ') if len(titles_to_print) > 1 else titles_to_print

    def print_table(self):
        if not self.is_input_correct:
            print(self.error_massage)
            return
        data_set = DataSet(self.file_name)
        if data_set.is_empty:
            print(data_set.error_massage)
            return
        counter = 0
        table = prettytable.PrettyTable(
            hrules=prettytable.ALL,
            align='l',
            field_names=['№'] + titles,
            max_width=20)
        data_set.filter_sort_data(self.filter_key, self.filter_value, self.sort_parameter, self.sort_reversed)
        if len(data_set.vacancies_objects) == 0:
            print('Ничего не найдено')
            return
        for vacancie in data_set.vacancies_objects:
            counter += 1
            table.add_row([counter] + vacancie.get_russian_format())
        print(table.get_string(start=self.range_to_print[0], end=self.range_to_print[1],
                               fields=['№'] + self.titles_to_print if len(self.titles_to_print) != 0 else [
                                                                                                              '№'] + table.field_names))


InputConnect().print_table()

