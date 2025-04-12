from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

def validate_first_name(value):
    RegexValidator(
        regex=r'^[a-zA-Zа-яА-Я-]+$',
        message='Имя должно содержать кириллические и латинские символы, а также знак нижнего подчёркивания. Длина минимум 2 символа.'
    )

def validate_last_name(value):
    RegexValidator(
        regex=r'^[a-zA-Zа-яА-Я-]+$',
        message='Фамилия должна содержать кириллические и латинские символы, а также знак нижнего подчёркивания. Длина минимум 2 символа.'
    )
