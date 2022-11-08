import csv
import math
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side


class DataSet:
    def __init__(self, file_name):
        self.is_empty = False
        self.error_massage = ''
        self.file_name = file_name
        self.vacancies_objects = self.csv_reader()

    def csv_reader(self) -> tuple or str:
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
        return self.formatter(header, vacancies)

    def is_correct_line(self, line: list, header_length: int) -> bool:
        return '' not in line and len(line) == header_length

    def formatter(self, header: list, rows: list) -> list:
        vacancies = []
        for row in rows:
            vacancies_dict = {}
            for i in range(len(header)):
                vacancies_dict[header[i]] = row[i]
            vacancies.append(Vacancy(vacancies_dict))
        return vacancies


class Vacancy:
    def __init__(self, args: dict):
        self.name = args['name'] if 'name' in args.keys() else ''
        self.salary = Salary(args)
        self.area_name = args['area_name'] if 'area_name' in args.keys() else ''
        self.published_at = int(args['published_at'][0:4]) if 'published_at' in args.keys() else ''


class Salary:
    def __init__(self, args: dict):
        self.salary_from = args['salary_from'] if 'salary_from' in args.keys() else ''
        self.salary_to = args['salary_to'] if 'salary_to' in args.keys() else ''
        self.salary_gross = args['salary_gross'] if 'salary_gross' in args.keys() else ''
        self.salary_currency = args['salary_currency'] if 'salary_currency' in args.keys() else ''
        self.average_salary = math.floor(
            ((float(self.salary_from) + float(self.salary_to)) / 2) * self.currency_to_rub[self.salary_currency])

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


class InputConnect:
    def __init__(self):
        self.file_name = input('Введите название файла: ')
        self.vacancy_name = input('Введите название профессии: ')


class Statistics:
    def __init__(self):
        self.input_values = InputConnect()
        self.vacancies = DataSet(self.input_values.file_name).vacancies_objects
        self.salary_by_year = {}
        self.count_by_year = {}
        self.prof_salary_by_year = {}
        self.prof_count_by_year = {}
        self.salary_by_city = {}
        self.count_by_city = {}

    def get_statistics(self) -> None:
        for vacancy in self.vacancies:
            self.update_stats(vacancy.published_at, vacancy.salary.average_salary, self.salary_by_year)
            self.update_stats(vacancy.published_at, 1, self.count_by_year)
            self.update_stats(vacancy.area_name, vacancy.salary.average_salary, self.salary_by_city)
            self.update_stats(vacancy.area_name, 1, self.count_by_city)
            if self.input_values.vacancy_name in vacancy.name:
                self.update_stats(vacancy.published_at, vacancy.salary.average_salary, self.prof_salary_by_year)
                self.update_stats(vacancy.published_at, 1, self.prof_count_by_year)

        self.get_average_salary(self.salary_by_year, self.count_by_year)
        self.get_average_salary(self.prof_salary_by_year, self.prof_count_by_year)
        self.get_average_salary(self.salary_by_city, self.count_by_city)
        self.get_percentage_of_total(self.count_by_city, len(self.vacancies))
        self.get_cities_with_enough_count()

        self.sort_statistics()
        self.print_stats()

    def update_stats(self, key: str, value: int or float, stats: dict) -> None:
        if key in stats.keys():
            stats[key] += value
        else:
            stats[key] = value

    def get_average_salary(self, salary_stats: dict, count_stats: dict) -> None:
        for key in count_stats.keys():
            salary_stats[key] = math.floor(salary_stats[key] / count_stats[key])

    def get_percentage_of_total(self, stats: dict, count: int) -> None:
        for key in stats.keys():
            stats[key] = round(stats[key] / count, 4)

    def get_cities_with_enough_count(self) -> None:
        new_salary_by_city = {}
        new_count_by_city = {}
        for key, value in self.count_by_city.items():
            if value * 100 < 1:
                continue
            new_salary_by_city[key] = self.salary_by_city[key]
            new_count_by_city[key] = value
        self.salary_by_city = new_salary_by_city
        self.count_by_city = new_count_by_city

    def sort_statistics(self) -> None:
        self.prof_salary_by_year = self.prof_salary_by_year if len(self.prof_salary_by_year) != 0 else {2022: 0}
        self.prof_count_by_year = self.prof_count_by_year if len(self.prof_count_by_year) != 0 else {2022: 0}
        self.salary_by_city = dict(sorted(self.salary_by_city.items(), key=lambda x: x[1], reverse=True)[:10])
        self.count_by_city = dict(sorted(self.count_by_city.items(), key=lambda x: x[1], reverse=True)[:10])

    def print_stats(self) -> None:
        print('Динамика уровня зарплат по годам:', self.salary_by_year)
        print('Динамика количества вакансий по годам:', self.count_by_year)
        print('Динамика уровня зарплат по годам для выбранной профессии:', self.prof_salary_by_year)
        print('Динамика количества вакансий по годам для выбранной профессии:', self.prof_count_by_year)
        print('Уровень зарплат по городам (в порядке убывания):', self.salary_by_city)
        print('Доля вакансий по городам (в порядке убывания):', self.count_by_city)


class Report:
    def __init__(self, statistics: Statistics):
        self.statistics = statistics
        self.statistics.get_statistics()
        self.usedColumns = ['A', 'B', 'C', 'D', 'E']

        self.workbook, self.years_sheet, self.cities_sheet = self.initialize_workbook()
        self.add_stats_to_excel()
        self.set_sheets_settings()

        self.workbook.save('report.xlsx')

    def initialize_workbook(self) -> tuple:
        workbook = Workbook()

        years_sheet = workbook.active
        years_sheet.title = 'Статистика по годам'
        cities_sheet = workbook.create_sheet('Статистика по городам')

        years_sheet.append(['Год', 'Средняя зарплата', f'Средняя зарплата - {self.statistics.input_values.vacancy_name}',
                            'Количество вакансий', f'Количество вакансий - {self.statistics.input_values.vacancy_name}'])
        cities_sheet.append(['Город', 'Уровень зарплат', '', 'Город', 'Доля Вакансий'])

        return workbook, years_sheet, cities_sheet

    def add_stats_to_excel(self):
        for year in self.statistics.salary_by_year.keys():
            self.years_sheet.append([year,
                                     self.statistics.salary_by_year[year],
                                     self.statistics.prof_salary_by_year[year],
                                     self.statistics.count_by_year[year],
                                     self.statistics.prof_salary_by_year[year]])

        for city in self.statistics.salary_by_city.keys():
            self.cities_sheet.append([city, self.statistics.salary_by_city[city]])

        for i, city in enumerate(self.statistics.count_by_city.keys(), 2):
            self.cities_sheet[f'D{i}'].value = city
            self.cities_sheet[f'E{i}'].value = f'{round(self.statistics.count_by_city[city] * 100, 2)}%'

    def set_sheets_settings(self) -> None:
        for i in self.usedColumns:
            self.years_sheet[f'{i}1'].font = Font(bold=True)
            self.cities_sheet[f'{i}1'].font = Font(bold=True)
            self.years_sheet.column_dimensions[i].width = max(map(lambda x: len(str(x.value)), self.years_sheet[i])) + 1
            self.cities_sheet.column_dimensions[i].width = max(map(lambda x: len(str(x.value)), self.cities_sheet[i])) + 1

        thins = Side(border_style="thin")
        for column in self.usedColumns:
            for row in range(1, len(self.statistics.salary_by_year.keys()) + 2):
                self.years_sheet[f'{column}{row}'].border = Border(top=thins, bottom=thins, left=thins, right=thins)

        for column in self.usedColumns:
            for row in range(1, len(self.statistics.salary_by_city.keys()) + 2):
                if column == 'C':
                    break
                self.cities_sheet[f'{column}{row}'].border = Border(top=thins, bottom=thins, left=thins, right=thins)


statistics = Statistics()
report = Report(statistics)

