from rest_framework import serializers
from django.core.exceptions import ValidationError


def validate_avatar(value):
    max_size = 4194304
    if value.size > max_size:
        raise ValidationError("Размер файла не должен превышать 4 МБ.")


def validate_avatar_small(value):
    max_size = 2097152
    if value.size > max_size:
        raise ValidationError("Размер файла не должен превышать 2 МБ.")
