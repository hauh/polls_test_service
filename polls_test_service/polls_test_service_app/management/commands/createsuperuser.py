"""Customized `createsuper`."""

import os

from django.contrib.auth.management.commands import createsuperuser


class Command(createsuperuser.Command):
	"""Extended 'createsuperuser' to get credentials from ENV."""

	def add_arguments(self, parser):
		super().add_arguments(parser)
		parser.add_argument(
			'--from-env', action='store_true',
			help=(
				"Create superuser with password from environment variables "
				"DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD "
				"like in Django 3.0."
			)
		)

	def handle(self, *args, **options):
		if not options['from_env']:
			super().handle(*args, **options)
			return
		username = os.environ['DJANGO_SUPERUSER_USERNAME']
		password = os.environ['DJANGO_SUPERUSER_PASSWORD']
		options[self.UserModel.USERNAME_FIELD] = username
		options['password'] = password
		options['interactive'] = False
		super().handle(*args, **options)
		self.UserModel.objects.get(username=username).set_password(password)
