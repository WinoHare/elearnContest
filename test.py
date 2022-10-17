import csv
import math
import re
import prettytable

title_dictionary = {
    'name': 'Название',
    'description': 'Описание',
    'key_skills': 'Навыки',
    'experience_id': 'Опыт работы',
    'premium': 'Премиум-вакансия',
    'employer_name': 'Компания',
    'salary': 'Оклад',
    'area_name': 'Название региона',
    'published_at': 'Дата публикации вакансии'
}

experience_dictionary = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет"
}

currency_dicitonary = {
    "AZN": "Манаты",
    "BYR": "Белорусские рубли",
    "EUR": "Евро",
    "GEL": "Грузинский лари",
    "KGS": "Киргизский сом",
    "KZT": "Тенге",
    "RUR": "Рубли",
    "UAH": "Гривны",
    "USD": "Доллары",
    "UZS": "Узбекский сум"
}

filter_parameters = {
    "Навыки": lambda vacanies, **skills: all(s in skills for s in vacanies['key_skills'].split(', ')),
    "Оклад": lambda vacancies, **salary: filter(lambda v: salary[0] <= v['']),
    "Дата публикации вакансии": lambda x : x,
    "Опыт работы": lambda x: x,
    "Премиум-вакансия": lambda x: x,
    "Идентификатор валюты оклада": lambda x: x,
    "Название": lambda x: x,
    "Название региона": lambda x: x,
    "Компания": lambda x: x
}


class Vacancie:
    def __init__(self, titles):
        self.name = titles[0]
        self.description = titles[1]
        self.key_skills = titles[2].split(', ')
        self.experience_id = titles[3]
        self.premium = titles[4]
        self.employer_name = titles[5]
        self.salary_from = parse_number(titles[6])
        self.salary_to = parse_number(titles[7])
        self.salary_gross = titles[8]
        self.salary_currency = titles[9]
        self.area_name = titles[10]
        self.published_at = titles[11]

    def get_formatted_vacancie(self):
        return [self.name, self.description, ', '.join(self.key_skills),
                experience_dictionary[self.experience_id], premium_yes_no(self.premium), self.employer_name,
                f'{self.salary_from} - {self.salary_to} ({currency_dicitonary[self.salary_currency]}) ({tax_yes_no(self.salary_gross)})',
                self.area_name, f'{self.published_at[8:10]}.{self.published_at[5:7]}.{self.published_at[0:4]}']


def is_correct_line(line, header_length):
    return '' not in line and len(line) == header_length


def premium_yes_no(premium):
    return 'Да' if premium == 'True' else 'Нет'


def tax_yes_no(tax):
    return 'Без вычета налогов' if tax == 'TRUE' or tax == 'True' else 'С вычетом налогов'


def clean_line(line):
    line = re.sub('<[^<]+?>', '', line)
    while '  ' in line:
        line = line.replace('  ', ' ')
    if len(line) > 100:
        line = line[0:100] + (' ...' if line[100] == ' ' else '...')
    return line


def parse_number(number):
    number = str(math.floor(float(number)))
    length = len(number)
    return f'{number[0:length - 3]} {number[length - 3: length]}'


def get_input_values(vacancies_length):
    range = input()
    if ' ' in range:
        start_position, end_position = range.split(' ')
        start_position, end_position = int(start_position) - 1, int(end_position) - 1
    elif len(range) != 0:
        start_position, end_position = int(range) - 1, vacancies_length - 1
    else:
        start_position, end_position = 0, vacancies_length - 1
    titles = input()
    titles = titles.split(', ') if len(titles) > 1 else titles
    return start_position, end_position, titles


def csv_reader(file_name):
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


def formatter(rows):
    vacancies = []
    for row in rows:
        vacancie = Vacancie(list(map(lambda t: clean_line(t), row)))
        vacancies.append(vacancie)
    return vacancies


def print_table(dicts):
    counter = 0
    table = prettytable.PrettyTable(
        hrules=prettytable.ALL,
        align='l',
        field_names=['№'] + list(title_dictionary.values()), )
    for title in title_dictionary.values():
        table._max_width[title] = 20
    for vacancie in dicts:
        counter += 1
        table.add_row([counter] + vacancie.get_formatted_vacancie())
    table_data = get_input_values(len(title_dictionary.values()) + 1)
    print(table.get_string(start=table_data[0], end=table_data[1],
                           fields=['№'] + table_data[2] if len(table_data[2]) != 0 else ['№'] + table.field_names))


def parse_csv(file_name):
    csv_file = csv_reader(file_name)
    header, vacancies = csv_file[0], csv_file[1]
    if len(header) == 0:
        print('Пустой файл')
        return
    dicts = formatter(vacancies)
    if len(dicts) == 0:
        print('Нет данных')
        return
    print_table(dicts)


parse_csv(input())
