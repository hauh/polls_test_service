"""Serializers."""

from functools import partial

from django.db import transaction
from rest_framework.fields import IntegerField, JSONField
from rest_framework.serializers import (
	ListSerializer, ModelSerializer, Serializer, ValidationError
)

from polls_test_service_app import models
from polls_test_service_app.models import QuestionType as QType


class Choice(ModelSerializer):
	"""Question Choice serializer."""

	class Meta:
		model = models.Choice
		fields = 'id', 'text'


class Question(ModelSerializer):
	"""Poll Question serializer."""

	choices = Choice(many=True, required=False)

	class Meta:
		model = models.Question
		fields = 'id', 'text', 'q_type', 'choices'

	def validate_q_type(self, value):
		try:
			q_type = QType(value)
		except ValueError as e:
			raise ValidationError(f"Value must be in {QType.choices()}.") from e
		if q_type is not QType.ARBITRARY and not self.initial_data.get('choices'):
			if not self.instance or not self.instance.choices:
				raise ValidationError("Choices are required for this question type.")
		return value

	def create(self, validated_data):
		choices = validated_data.pop('choices', ())
		validated_data['poll'] = self.context['poll']
		with transaction.atomic():
			question = super().create(validated_data)
			self._update_choices(question, choices)
		return question

	def update(self, instance, validated_data):
		choices = validated_data.pop('choices', ())
		with transaction.atomic():
			question = super().update(instance, validated_data)
			if choices or QType(question.q_type) is QType.ARBITRARY:
				models.Choice.objects.filter(question=question).delete()
			self._update_choices(question, choices)
		return question

	def _update_choices(self, question, choices):
		if QType(question.q_type) is not QType.ARBITRARY:
			for choice in choices:
				models.Choice.objects.create(question=question, **choice)


class Poll(ModelSerializer):
	"""Poll serializer."""

	questions = Question(many=True, read_only=True)

	class Meta:
		model = models.Poll
		fields = '__all__'

	def validate(self, attrs):
		if end_date := attrs.get('end_date'):
			if end_date < (attrs.get('start_date') or self.instance.start_date):
				raise ValidationError("End date must be after start date.")
		return attrs

	def update(self, instance, validated_data):
		validated_data.pop('start_date', None)
		return super().update(instance, validated_data)


class Answer(Serializer):
	"""User's Choice serializer."""

	user_id = IntegerField()
	answers = ListSerializer(child=JSONField(), allow_empty=False)

	class Meta:
		fields = 'user_id', 'answers'

	def validate_user_id(self, value):
		poll = self.context['poll']
		if models.Answer.objects.filter(user_id=value, poll=poll).exists():
			raise ValidationError("You've already answered this poll.")
		return value

	def validate_answers(self, value):
		if not value:
			raise ValidationError("Please, provide some answers.")
		poll = self.context['poll']
		questions = {q.id: q for q in poll.questions.all()}
		valid_answers = []
		found_answers = set()
		for raw_answer in value:
			if not (question := questions.get(raw_answer.get('question_id'), None)):
				continue

			choice = raw_answer.get('choice')
			question_type = QType(question.q_type)

			if question_type != QType.MANY and question.id in found_answers:
				raise ValidationError(
					f"Only single choice allowed for question id {question.id}"
				)
			found_answers.add(question.id)

			if question_type == QType.ARBITRARY:
				if not isinstance(choice, str):
					raise ValidationError(
						"Answer to question of this type must be a string."
					)
				valid_answers.append(raw_answer)
				continue

			if not isinstance(choice, int):
				raise ValidationError(
					f"Answer to question id {question.id} must be an integer id of a choice."
				)

			try:
				existing_choice = models.Choice.objects.get(id=choice)
			except models.Choice.DoesNotExist as e:
				raise ValidationError(f"Choice id {choice} not found.") from e
			if existing_choice.question != question:
				raise ValidationError(f"Choice id {choice} is for anoher question.")
			valid_answers.append(raw_answer)

		if len(found_answers) != len(questions):
			raise ValidationError(
				f"Please, provide answers to questions: {list(questions)}."
			)
		return valid_answers

	def create(self, validated_data):
		create_object = partial(
			models.Answer.objects.create,
			user_id=validated_data['user_id'], poll=self.context['poll']
		)
		created = []
		with transaction.atomic():
			for answer in validated_data['answers']:
				choice = answer['choice']
				if isinstance(choice, str):
					o = create_object(question_id=answer['question_id'], arbitrary=choice)
				elif isinstance(choice, int):
					o = create_object(question_id=answer['question_id'], choice_id=choice)
				created.append(o)
		return created

	def to_representation(self, instance):
		return {'result': f"Answers saved: {len(instance)}."}
