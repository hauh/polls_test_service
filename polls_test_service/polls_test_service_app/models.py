"""Models."""

from enum import Enum

from django.db.models import Model, ForeignKey
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
	CharField, DateTimeField, SmallIntegerField, TextField
)


class Poll(Model):
	"""Poll model."""

	title = CharField(max_length=128)
	description = TextField(max_length=4098)
	start_date = DateTimeField()
	end_date = DateTimeField()


class QuestionType(Enum):
	"""Question type."""

	ARBITRARY = 0
	SINGlE = 1
	MANY = 2

	@classmethod
	def choices(cls):
		return {i.value: i for i in cls}


class Question(Model):
	"""Poll's Question."""

	text = TextField(max_length=4098)
	q_type = SmallIntegerField(default=QuestionType.ARBITRARY)
	poll = ForeignKey('Poll', related_name='questions', on_delete=CASCADE)


class Answer(Model):
	"""Answer to Poll's Question."""

	text = CharField(max_length=255)
	question = ForeignKey('Question', related_name='answers', on_delete=CASCADE)
