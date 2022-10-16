import csv
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


def is_correct_line(line, header_length):
    if not len(line) == header_length:
        return False
    for item in line:
        if item == '':
            return False
    return True


def clean_string(str):
    str = re.sub('<[^<]+?>', '', str)
    while '  ' in str:
        str = str.replace('  ', ' ')
    if len(str) > 100:
        str = str[0:100] + (' ...' if str[100] == ' ' else '...')
    return str


def premium_yes_no(str):
    return 'Да' if str == 'True' else 'Нет'


def tax_yes_no(str):
    return 'Без вычета налогов' if str == 'TRUE' or str == 'True' else 'С вычетом налогов'


def parse_number(number):
    number = str(int(float(number)))
    length = len(number)
    number = '{0} {1}'.format(number[0:length - 3], number[length - 3: length]).strip()
    return number


def get_input_values(vacancies_length):
    range = input()
    if ' ' in range:
        startPosition, endPosition = range.split(' ')
        startPosition, endPosition = int(startPosition) - 1, int(endPosition) - 1
    elif len(range) != 0:
        startPosition, endPosition = int(range) - 1, vacancies_length - 1
    else:
        startPosition, endPosition = 0, vacancies_length - 1
    titles = input()
    titles = titles.split(', ') if len(titles) > 1 else titles
    return startPosition, endPosition, titles


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
    return (header, vacancies)


def csv_filer(vacancies, header):
    dicts_vacancies = []
    for vacancie in vacancies:
        dict = {}
        for i in range(0, len(header)):
            dict[header[i]] = clean_string(vacancie[i])
        dicts_vacancies.append(dict)
    return dicts_vacancies


def formatter(rows):
    vacancies = []
    for row in rows:
        vacancie = {
            'name': row['name'],
            'description': row['description'],
            'key_skills': row['key_skills'],
            'experience_id': experience_dictionary[row['experience_id']],
            'premium': premium_yes_no(row['premium']),
            'employer_name': row['employer_name'],
            'salary': '{0} - {1} ({2}) ({3})'.format(parse_number(row['salary_from']), parse_number(row['salary_to']),
                                                     currency_dicitonary[row['salary_currency']],
                                                     tax_yes_no(row['salary_gross']), ),
            'area_name': row['area_name'],
            'published_at': '{0}.{1}.{2}'.format(row['published_at'][8:10], row['published_at'][5:7],
                                                 row['published_at'][0:4])
        }
        vacancies.append(vacancie)
    return vacancies


def print_table(dicts):
    counter = 0
    table = prettytable.PrettyTable(
        hrules=prettytable.ALL,
        align='l',
        field_names=['№'] + list(title_dictionary.values()))
    for title in title_dictionary.values():
        table._max_width[title] = 20
    for vacancie in dicts:
        counter += 1
        table.add_row([counter] + list(vacancie.values()))
    table_data = get_input_values(len(title_dictionary.values()) + 1)
    print(table.get_string(start=table_data[0], end=table_data[1],
                           fields=['№'] + table_data[2] if len(table_data[2]) != 0 else ['№'] + table.field_names))


def parse_csv(file_name):
    csv_file = csv_reader(file_name)
    header, vacancies = csv_file[0], csv_file[1]
    if len(header) == 0:
        print('Пустой файл')
        return
    dicts = formatter(csv_filer(vacancies, header))
    if len(dicts) == 0:
        print('Нет данных')
        return
    print_table(dicts)


parse_csv(input())
