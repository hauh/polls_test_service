"""Serializers."""

from rest_framework.serializers import ModelSerializer
from polls_test_service_app import models


class Poll(ModelSerializer):
	"""Poll serializer."""

	class Meta:
		model = models.Poll
		fields = '__all__'

	def update(self, instance, data):
		data.pop('start_date', None)
		return super().update(instance, data)
