"""Views."""

from rest_framework.generics import (
	CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView,
	get_object_or_404
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

	queryset = models.Question.objects.all()
	serializer_class = serializers.Question

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['poll'] = get_object_or_404(models.Poll, id=self.kwargs['poll_id'])
		return context


class Question(RetrieveUpdateDestroyAPIView):
	"""GET, PUT, PATCH, DELETE Question."""

	queryset = models.Question.objects.all()
	serializer_class = serializers.Question


class Answer(CreateAPIView):
	"""POST Answer to Poll."""

	queryset = models.Answer.objects.all()
	serializer_class = serializers.Answer

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['poll'] = get_object_or_404(models.Poll, id=self.kwargs['poll_id'])
		return context
