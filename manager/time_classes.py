from .models import Person, Department, Record, ExceptionDay
from .consts import TYPE_CHOICES, STR_MONTH, STR_MONTH2, \
    TYPE_NONE, TYPE_ADMIN, TYPE_OTGUL, TYPE_HOSP, TYPE_OTPUSK, TYPE_KOMAND, \
    ID_NONE, ID_ADMIN, ID_OTGUL, ID_HOSP, ID_OTPUSK, ID_KOMAND
from datetime import datetime, timedelta, time, date
from django.db import models
import pytz
from .utils import td, tr, table


class Report:
    def __init__(self, request):
        self.person = self.get_person(request['person'])
        self.report_type = int(request['type'])
        self.date_from, self.date_to = self.dates_parse(request['date_from'], request['time_from'],
                                                        request['date_to'], request['time_to'])
        self.reason = self.get_reason()

    def get_person(self, request_person):
        print(f'report get person {request_person}')
        person_field = request_person
        name, number = person_field.split('; ')
        person = Person.objects.get(personnel_number=number)
        return person

    def dates_parse(self, date_from, time_from, date_to, time_to):
        if time_from in [None, '']:
            time_from = '00:00'
        datetime_from = datetime.strptime(f'{date_from} {time_from}', '%Y-%m-%d %H:%M')

        if time_to in [None, '']:
            time_to = '00:00'
        if date_to in [None, '']:
            datetime_to = datetime_from
        else:
            datetime_to = datetime.strptime(f'{date_to} {time_to}', '%Y-%m-%d %H:%M')
        return datetime_from, datetime_to

    def get_reason(self):
        report_date = self.get_report_date()
        if self.report_type == int(ID_ADMIN):
            return f'Прошу предоставить мне отпуск без сохранения заработной платы {report_date}' \
                   f' по семейным обстоятельствам.'
        elif self.report_type == int(ID_OTGUL):
            return f'Прошу предоставить мне отгул {report_date} за заранее отработанное время'
        elif self.report_type == int(ID_OTPUSK):
            return f'Прошу предоставить очередной отпуск за {self.date_from.year} г. ' \
                   f'{report_date}.'
        else:
            return ''

    def get_report_date(self):
        if self.date_to == self.date_from:
            return self.date_from.strftime('%d.%m.%Y')
        elif self.date_from.hour != 0 and self.date_from.day == self.date_to.day:
            return f'{self.date_from.strftime("%d.%m.%Y")} с {self.date_from.strftime("%H.%M")}' \
                   f' по {self.date_to.strftime("%H.%M")}'
        else:
            return f'с {self.date_from.strftime("%d.%m.%Y")} по {self.date_to.strftime("%d.%m.%Y")}'

    def pdf_needed(self):
        if self.reason == '':  # на больничный и командировку заявку не пишем
            return False
        else:
            return True

    def make_html(self): # obsolete
        html = '''
                <html>
                    <head>
                        <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
                        <style type="text/css">
                            @page { size: A4; margin: 1cm; }
                            @font-face {
                                font-family: FreeSerif;
                                src: url("/home/alexey/python_projects/ldsp_env/ldsp_src/media/arial.ttf");
                                }
                            body {font-family: FreeSerif; font-size: 16px; }
                            .report-to{margin-left: 500px;}
                            .report-title{text-align: center;}
                        </style>
                    </head>
                    <body>''' + \
                        f'<div class="report-to">Главному конструктору-<br>Начальнику {self.person.department.super_name}<br>'
        html += f'{self.person.department.boss_name}<br>' \
                f'от {self.person.job2}<br>{self.person.department}<br>{self.person.name2}<br>' \
                f'таб. № {self.person.personnel_number}<br>тел. {self.person.department.tel_number}<br></div>' \
                f'<div class="report-title"><br>Заявление<br></div>' \
                f'<div class="report-body">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{self.reason}</div>' \
                f'</body></html>'
        return html

    def alert(self):
        if self.report_type == int(ID_HOSP):
            return 'Больничный учтён, будьте здоровы!'
        elif self.report_type == int(ID_KOMAND):
            return 'Командировка учтена'
        else:
            return ''


class TimeData:
    def __init__(self, request, department):
        self.date = self.get_date(request['date'])
        self.department = department
        self.half = True if 'submit-half' in request else False
        self.persons = self.get_persons()
        self.holidays, self.short_days, self.nd_days = self.get_exception_days()
        self.days_half1, self.days_half2 = self.get_work_days()
        self.work_start = timedelta(hours=self.department.work_start.hour, minutes=self.department.work_start.minute)
        self.work_end = timedelta(hours=self.department.work_end.hour, minutes=self.department.work_end.minute)
        self.work_end_short = timedelta(hours=self.department.work_end_short.hour,
                                        minutes=self.department.work_end_short.minute)
        self.lunch_start = timedelta(hours=self.department.lunch_start.hour, minutes=self.department.lunch_start.minute)
        self.lunch_end = timedelta(hours=self.department.lunch_end.hour, minutes=self.department.lunch_end.minute)

    def get_persons(self):

        persons = Person.objects.filter(department=self.department,
                                        hired_date__month__lte=self.date.month,
                                        hired_date__year__lte=self.date.year,
                                        )
        for person in persons:
            if person.fired_date is not None and datetime.combine(person.fired_date, time(0, 0)) < self.date:
                persons = persons.exclude(name=person.name)

        return persons.order_by('timesheet_pos')

    def get_date(self, date_):
        date_new = datetime.strptime(date_, '%Y-%m')
        return datetime(date_new.year, date_new.month, 1)

    def make_html(self):
        return '<div>This should be redefined</div>'

    def calc_days_hours_total(self, hours_list):
        days = 0
        hours = 0
        for string in hours_list:
            try:
                current_hours = float(string)
            except ValueError:
                pass
            else:
                days += 1
                hours += current_hours
        return str(days), str(hours)

    def get_exception_days(self):
        query = ExceptionDay.objects.filter(date__year=self.date.year, date__month=self.date.month)
        holidays = [datetime.combine(obj.date, time(0, 0)) for obj in query if obj.day_type == 'RED']
        short_days = [datetime.combine(obj.date, time(0, 0)) for obj in query if obj.day_type == 'BLUE']
        nd_days = [datetime.combine(obj.date, time(0, 0)) for obj in query if obj.day_type == 'НД']
        return holidays, short_days, nd_days

    def get_work_days(self):
        import calendar
        days_count = calendar.monthrange(self.date.year, self.date.month)[1] if not self.half else 16
        days_first_half = [day for day in range(1, 16)
                           if ((datetime(self.date.year, self.date.month, day).weekday() not in (5, 6)) and
                               (datetime(self.date.year, self.date.month, day) not in self.holidays)) or
                            datetime(self.date.year, self.date.month, day) in self.short_days]
        days_second_half = [day for day in range(16, days_count + 1)
                            if ((datetime(self.date.year, self.date.month, day).weekday() not in (5, 6)) and
                            (datetime(self.date.year, self.date.month, day) not in self.holidays)) or
                            datetime(self.date.year, self.date.month, day) in self.short_days]
        return days_first_half, days_second_half

    def format_hours(self, hours_string):
        try:
            h, m, s = hours_string.split(':')
        except ValueError:
            return hours_string
        else:
            result = float(h)
            if int(m) == 0:
                pass
            elif 0 < int(m) <= 15:
                result += 0.25
            elif 15 < int(m) <= 30:
                result += 0.5
            elif 30 < int(m) <= 45:
                result += 0.75
            else:
                result += 1
            if result.is_integer():
                result = int(result)
            return str(result)

    def calc_hours(self, day, person):
        this_day = datetime(self.date.year, self.date.month, day)
        this_day_utc = pytz.utc.localize(this_day)

        if datetime.combine(person.hired_date, time(0, 0)) > this_day:
            return '  '
        elif person.fired_date is not None and this_day > datetime.combine(person.fired_date, time(0, 0)):
            return '  '
        elif this_day in self.nd_days:
            return 'НД'
        elif this_day in self.short_days:
            hours = self.work_end_short - self.work_start - (self.lunch_end - self.lunch_start)
        else:
            hours = self.work_end - self.work_start - (self.lunch_end - self.lunch_start)

        records = Record.objects.filter(
            models.Q(date_from__year=self.date.year) | models.Q(date_to__year=self.date.year),
            models.Q(date_from__month=self.date.month) | models.Q(date_to__month=self.date.month),
            person=person)
        for record in records:

            if record.person.name == person.name:
                if record.type == TYPE_ADMIN:
                    if record.date_from.day == this_day.day:
                        delta = self.overlap(record.date_from, record.date_to, self.lunch_start, self.lunch_end)
                        hours -= delta
                    if hours == timedelta(hours=0):
                        return 'A'
                elif record.type == TYPE_OTPUSK:
                    if record.date_from <= this_day_utc <= record.date_to:
                        return 'O'
                elif record.type == TYPE_KOMAND:
                    if record.date_from <= this_day_utc <= record.date_to:
                        return 'K'
                elif record.type == TYPE_HOSP:
                    if record.date_from <= this_day_utc <= record.date_to:
                        return 'Б'
        return str(hours)

    def overlap(self, date_from, date_to, lunch_start, lunch_end):
        date_from_hour = self.department.work_start.hour if date_from.hour == 0 else date_from.hour
        date_to_hour = self.department.work_end.hour if date_to.hour == 0 else date_to.hour

        aw_start = timedelta(hours=date_from_hour, minutes=date_from.minute)
        aw_end = timedelta(hours=date_to_hour, minutes=date_to.minute)
        if aw_start <= lunch_end and aw_end >= lunch_start:
            return max(aw_end, lunch_end) - min(aw_start, lunch_start) - (lunch_end - lunch_start)
        else:
            return aw_end - aw_start


class Timesheet(TimeData):
    def __init__(self, request, department):
        super().__init__(request, department)

    def rows(self):
        rows = []
        for person in self.persons:
            hours_list_half1 = [self.format_hours(self.calc_hours(day, person)) for day in self.days_half1]
            days_half1, hours_half1 = self.calc_days_hours_total(hours_list_half1)

            hours_list_half1_html = ''.join([td(el, cls=f"w{len(el)}") for el in hours_list_half1])

            row = td(person.job) + td(person.name) + td(person.personnel_number) + hours_list_half1_html + \
                  td(days_half1) + td(hours_half1)
            if not self.half:
                hours_list_half2 = [self.format_hours(self.calc_hours(day, person)) for day in self.days_half2]
                days_half2, hours_half2 = self.calc_days_hours_total(hours_list_half2)

                hours_list_half2_html = ''.join([td(el) for el in hours_list_half2])

                row += hours_list_half2_html + td(days_half2) + td(hours_half2) + \
                       td(str(float(days_half1) + float(days_half2))) + \
                       td(str(float(hours_half1) + float(hours_half2)))
            rows.append(tr(row))
        return ''.join(rows)

    def header(self):
        days_first_half = ''.join([td(str(day), cls='min') for day in self.days_half1])

        table_header = td('Должность') + td('Фамилия<br>и инициалы') + td('Таб. №') + days_first_half + \
                       td('Кол.<br>отраб.<br>дней<br>за I п.') + td('Кол.<br>отраб.<br>часов<br>за I п.')

        if not self.half:
            days_second_half = ''.join([td(str(day), cls='min') for day in self.days_half2])
            table_header += days_second_half + td('Кол.<br>отраб.<br>дней<br>за II п.') + \
                            td('Кол.<br>отраб.<br>часов<br>за II п.') + td('Дней') + td('Часов')
        table_header = tr(table_header)
        return table_header

    def make_subtitle(self):
        records_hosp = Record.objects.filter(
            models.Q(date_from__year=self.date.year) | models.Q(date_to__year=self.date.year),
            models.Q(date_from__month=self.date.month) | models.Q(date_to__month=self.date.month),
            type=TYPE_HOSP)

        records_otp = Record.objects.filter(
            models.Q(date_from__year=self.date.year) | models.Q(date_to__year=self.date.year),
            models.Q(date_from__month=self.date.month) | models.Q(date_to__month=self.date.month),
            type=TYPE_OTPUSK)

        records_komm = Record.objects.filter(
            models.Q(date_from__year=self.date.year) | models.Q(date_to__year=self.date.year),
            models.Q(date_from__month=self.date.month) | models.Q(date_to__month=self.date.month),
            type=TYPE_KOMAND)

        s = ''
        for record in records_hosp:
            if record.person.department == self.department:
                s += f'Б - больничный - {record.person.name} {record.date_from.strftime("%d.%m.%Y")} -' \
                     f' {record.date_to.strftime("%d.%m.%Y")}<br>'
        for record in records_otp:
            if record.person.department == self.department:
                s += f'О - отпуск - {record.person.name} {record.date_from.strftime("%d.%m.%Y")} -' \
                     f'{record.date_to.strftime("%d.%m.%Y")}<br>'
        for record in records_komm:
            if record.person.department == self.department:
                s += f'К - командировка - {record.person.name} {record.date_from.strftime("%d.%m.%Y")} -' \
                     f' {record.date_to.strftime("%d.%m.%Y")}<br>'
        return s

    def context(self):
        pdf = {
            'dep_name': self.department.name2,
            'month': STR_MONTH[self.date.month],
            'year': self.date.year,
            'header': self.header(),
            'rows': self.rows(),
            'subtitle': self.make_subtitle(),
        }
        return pdf


class TimeTrack(TimeData):
    def __init__(self, request, department):
        super().__init__(request, department)

    def make_html(self):
        dep_boss = Person.objects.get(is_boss=True, department=self.department)
        strs = ['№ сектора', 'месяц', 'Начальник сектора', '№ подразделения',
                'Ведомость учёта времени и зарплаты по ордерам', f'{self.department.code}',
                f'{STR_MONTH[self.date.month]} {self.date.year}г.', f'{dep_boss.name}',
                f'{self.department.super_name}', '№ п/п.', 'Фамилия И.О.', 'Таб. №', 'Оклад',
                'Часов.<br>ставка', 'Всего', 'Ордера', 'Час', 'Зарпл.', 'час', 'з/пл.', 'Итого:',
                f'Начальник {self.department.name} {dep_boss.name}']
        html = tr(
            td(strs[0], cs=2) + td(strs[1], cs=2) + td(strs[2], cs=3) + td(strs[3], cs=3) + td(strs[4], rs=3, cs=14))
        html += tr(td(strs[5], cs=2) + td(strs[6], cs=2) + td(strs[7], cs=3) + td(strs[8], cs=3))
        html += tr(td('', td_id='e1', cs=10))
        html += tr(td(strs[9], rs=3) + td(strs[10], rs=3, cs=2) + td(strs[11], rs=3, cs=2) + td(strs[12], rs=3) +
                   td(strs[13], rs=3, cs=2) + td(strs[14], cs=2) + td(strs[15], cs=14))
        html += tr(td(strs[16], rs=2) + td(strs[17], rs=2) + td('', td_id='e1', cs=2) * 7)
        html += tr((td(strs[18]) + td(strs[19])) * 7)
        html += tr(td(td_id='e1') + td(cs=2) * 2 + td() + td(cs=2) + td() * 16)

        html += tr(td(td_id='e1') + td(cs=2) * 2 + td() + td(cs=2) + td() * 16)

        hours_total = 0
        # days, hours = self.calc_days_hours_total(self.days_first_half + self.days_second_half)
        for person in self.persons:
            hours_list = ''.join([td(self.format_hours(self.calc_hours(day, person))) for day in self.days_half1+self.days_half2])

            _, hours = self.calc_days_hours_total(hours_list)

            html += tr(td(td_id='e1') + td(person.name, cs=2) + td(f'{person.personnel_number}', cs=2) + td() +
                       td(cs=2) + td(f'{hours}') + td() * 15)
            hours_total += float(hours)

        html += tr(td(td_id='e1') + td(strs[20], cs=7) + td(f'{hours_total}') + td() * 15)
        html += tr(td(td_id='e1') + td(cs=2) * 2 + td() + td(cs=2) + td() * 16)
        html += tr(td(td_id='e1', cs=14) + td(strs[21], cs=10))

        html = '''<head>
                        <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
                    </head>
                    <body>''' + \
               table(html, cp=5) + \
               '''
               </body>
                <style>
                    @page { size: A3; size: landscape; margin: 1cm; }
                    @font-face {
                        font-family: Arial;
                        src: url("/home/alexey/python_projects/ldsp_env/ldsp_src/media/arial.ttf");
                        }
                    body {font-family: Arial; font-size: 16px; }
                    table {font: 20px Arial}
                    table, td, tr {border: 2px solid black; word-break: break-all;
                    border-collapse: collapse; text-align: center}
                    #e1 { height:28;}
                    @media print { @page {size: A4 landscape} }
                </style>'''
        return html