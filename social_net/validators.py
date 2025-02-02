from django.db.models import SlugField, TextField
from rest_framework.fields import CharField
from rest_framework.validators import UniqueValidator


slug = SlugField(
    max_length=25,
    validators=[],
)

title = CharField(
    max_length=100,

)

description = TextField