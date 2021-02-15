"""Models."""

from django.db.models import CharField, DateTimeField, Model, TextField


class Poll(Model):
	"""Poll model."""

	title = CharField(max_length=128)
	description = TextField(max_length=4098)
	start_date = DateTimeField()
	end_date = DateTimeField()
