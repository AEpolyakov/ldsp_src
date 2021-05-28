from django.db import models
from django.contrib.auth.models import User
import hashlib
from django.utils.timezone import now


class Department(models.Model):
    name = models.CharField(max_length=64, verbose_name='название подраделения')
    name2 = models.CharField(max_length=64, default='', verbose_name='Название в родительном падеже')
    tel_number = models.CharField(max_length=32, blank=True, verbose_name='номер телефона')
    code = models.IntegerField(blank=True, verbose_name='код подразделения')
    boss_name = models.CharField(max_length=64, default='Воронцову В.А.', verbose_name='Служебки кому:')

    work_start = models.TimeField(default='8:00', verbose_name='Начало рабочего дня')
    work_end = models.TimeField(default='17:00', verbose_name='Окончание рабочего дня')
    work_end_short = models.TimeField(default='16:00', verbose_name='Окончание сокращенного рабочего дня')
    lunch_start = models.TimeField(default='11:45', verbose_name='Начало обеденного перерыва')
    lunch_end = models.TimeField(default='12:45', verbose_name='Окончание обеденного перерыва')
    super_name = models.CharField(max_length=16, default='ОКБ', verbose_name='Вышестоящее подразделение')
    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'


class Person(models.Model):
    name = models.CharField(max_length=64, verbose_name="Имя в им. падеже")
    name2 = models.CharField(max_length=64, verbose_name="Имя в род. падеже")
    job = models.CharField(max_length=64, verbose_name="Должность в им. падеже")
    job2 = models.CharField(max_length=64, verbose_name="Должность в им. падеже")
    personnel_number = models.IntegerField(unique=True, verbose_name="Табельный номер")
    pass_number = models.IntegerField(unique=True, verbose_name="Номер пропуска")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Подразделение")
    is_boss = models.BooleanField(default=False, verbose_name="Начальник")
    objects = models.Manager()
    timesheet_pos = models.IntegerField(default=0, verbose_name="Позиция в графике выходов")
    hired_date = models.DateField(default=now(), verbose_name="Дата поступления на работу")
    fired_date = models.DateField(blank=True, null=True, verbose_name="Дата увольнения")

    def __str__(self):
        return f'{self.name} {self.personnel_number}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="сотрудник")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=None, verbose_name="Подразделение")
    logo = models.ImageField(upload_to='avatars', default='no_foto.png', verbose_name="Фото")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)
    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username} {self.department.name}'


def generate_hash(*args):
    string = ''
    for arg in args:
        string += str(arg)

    hash_obj = hashlib.md5(string.encode('ascii'))
    return hash_obj.hexdigest()


class Record(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    type = models.CharField(max_length=16)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    date_created = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=64, default='')
    objects = models.Manager()
    hash_object = models.CharField(max_length=32, default=None, unique=True)

    def __str__(self):
        return f'{self.person.name} {self.type} {self.date_from.strftime("%d.%m.%Y")}-{self.date_to.strftime("%d.%m.%Y")}'

    def save(self, *args, **kwargs):
        hash_object = generate_hash(str(self.person.name).encode(),
                                    str(self.type).encode(),
                                    str(self.date_from).encode(),
                                    str(self.date_to).encode())
        records = Record.objects.filter(hash_object=hash_object)
        print(f'before making record {records} {len(records)}')
        if len(records) == 0:
            print(f'MAKING RECORD!!!')
            self.hash_object = hash_object
            super().save(*args, **kwargs)


class ExceptionDay(models.Model):
    date = models.DateField()
    day_type = models.CharField(max_length=16)
    objects = models.Manager()

    def __str__(self):
        return f'{self.date} {self.day_type}'
