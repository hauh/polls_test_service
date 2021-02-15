"""Views."""

from rest_framework.generics import (
	ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from polls_test_service_app import models, serializers


class PollsList(ListCreateAPIView):
	"""GET, POST Polls."""

	queryset = models.Poll.objects.all()
	serializer_class = serializers.Poll


class Poll(RetrieveUpdateDestroyAPIView):
	"""GET, PUT, PATCH, DELETE Poll."""

	queryset = models.Poll.objects.all()
	serializer_class = serializers.Poll


class QuestionsList(ListCreateAPIView):
	"""GET, POST Questions."""

	serializer_class = serializers.Question

	def get_queryset(self):
		return models.Question.objects.filter(poll=self.kwargs['poll_id'])

	def perform_create(self, serializer):
		serializer.validated_data['poll_id'] = self.kwargs['poll_id']
		serializer.save()


class Question(RetrieveUpdateDestroyAPIView):
	"""GET, PUT, PATCH, DELETE Question."""

	serializer_class = serializers.Question

	def get_queryset(self):
		return models.Question.objects.filter(poll=self.kwargs['poll_id'])
