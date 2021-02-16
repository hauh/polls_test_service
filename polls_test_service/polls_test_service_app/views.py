"""Views."""

from django.utils import timezone
from rest_framework.generics import (
	CreateAPIView, GenericAPIView, ListCreateAPIView,
	RetrieveUpdateDestroyAPIView, get_object_or_404
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from polls_test_service_app import models, serializers


class PollsList(ListCreateAPIView):
	"""GET, POST Polls."""

	serializer_class = serializers.Poll

	def get_queryset(self):
		if self.request.user.is_staff:
			return models.Poll.objects.all()
		return models.Poll.objects.filter(end_date__lt=timezone.now())


class Poll(RetrieveUpdateDestroyAPIView):
	"""GET, PUT, PATCH, DELETE Poll."""

	queryset = models.Poll.objects.all()
	serializer_class = serializers.Poll


class QuestionsList(ListCreateAPIView):
	"""GET, POST Questions."""

	serializer_class = serializers.Question

	def get_queryset(self):
		return models.Question.objects.filter(poll_id=self.kwargs['poll_id'])

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['poll'] = get_object_or_404(models.Poll, id=self.kwargs['poll_id'])
		return context


class Question(RetrieveUpdateDestroyAPIView):
	"""GET, PUT, PATCH, DELETE Question."""

	serializer_class = serializers.Question

	def get_queryset(self):
		return models.Question.objects.filter(poll_id=self.kwargs['poll_id'])


class Answer(CreateAPIView):
	"""POST Answer to Poll."""

	queryset = models.Answer.objects.all()
	serializer_class = serializers.Answer
	permission_classes = (AllowAny,)

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['poll'] = get_object_or_404(models.Poll, id=self.kwargs['poll_id'])
		return context


class UserAnswers(GenericAPIView):
	"""GET user's Answers."""

	def get_queryset(self):
		return (
			models.Answer.objects
			.select_related('poll').select_related('question').select_related('choice')
			.filter(user_id=self.kwargs['user_id'])
		)

	def get(self, *args, **kwargs):
		grouped = {}
		for answer in self.get_queryset():
			grouped.setdefault(answer.poll, {}).setdefault(answer.question, [])\
				.append(answer.arbitrary or answer.choice.text)
		user_answers = []
		for poll, question in grouped.items():
			user_answers.append({
				'id': poll.id,
				'title': poll.title,
				'description': poll.description,
				'questions': [{
					'id': q.id,
					'text': q.text,
					'choices': [c for c in choices]
				} for q, choices in question.items()]
			})
		return Response(user_answers)
