"""Models."""

from enum import Enum
from functools import partial

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import ForeignKey, Manager, Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
	CharField, DateTimeField, IntegerField, SmallIntegerField, TextField
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
	SINGLE = 1
	MANY = 2

	@classmethod
	def choices(cls):
		return {i.value: i for i in cls}


class Question(Model):
	"""Poll Question model."""

	text = TextField(max_length=4098)
	q_type = SmallIntegerField(default=QuestionType.ARBITRARY)
	poll = ForeignKey(Poll, related_name='questions', on_delete=CASCADE)


class Choice(Model):
	"""Question Choice model."""

	text = CharField(max_length=255)
	question = ForeignKey(Question, related_name='choices', on_delete=CASCADE)


answer_foreign_key = partial(ForeignKey, related_name='+', on_delete=CASCADE)


class Answer(Model):
	"""User's Choice for Poll Question model."""

	user_id = IntegerField()
	arbitrary = CharField(max_length=255, default=None, null=True)
	choice = answer_foreign_key(Choice, default=None, null=True)
	question = answer_foreign_key(Question)
	poll = answer_foreign_key(Poll)


class UserManager(BaseUserManager):
	"""For creating users with hashed password."""

	def create_user(self, password, **fields):
		if not password:
			raise ValueError("Password required.")
		user = self.model(**fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, password, **fields):
		user = self.create_user(password, **fields)
		user.is_staff = True
		user.is_superuser = True
		user.save()
		return user


class User(AbstractUser):
	"""Customized user."""

	objects = UserManager()
	REQUIRED_FIELDS = ('password',)
