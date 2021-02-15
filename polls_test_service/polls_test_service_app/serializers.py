"""Serializers."""

from rest_framework.serializers import ModelSerializer, ValidationError
from polls_test_service_app import models

NO_ANSWERS_TYPE = models.QuestionType.ARBITRARY.value


class Answer(ModelSerializer):
	"""Answer serializer."""

	class Meta:
		model = models.Answer
		fields = ('id', 'text')


class Question(ModelSerializer):
	"""Question serializer."""

	answers = Answer(many=True, required=False)

	class Meta:
		model = models.Question
		fields = ('id', 'text', 'q_type', 'answers')

	def validate_q_type(self, value):
		question_types = models.QuestionType.choices()
		if value not in question_types:
			raise ValidationError(f"Value must be in {question_types}.")
		if value != NO_ANSWERS_TYPE and not self.initial_data.get('answers'):
			if not self.instance or not self.instance.answers:
				raise ValidationError("Answers are required for this question type.")
		return value

	def create(self, validated_data):
		answers = validated_data.pop('answers', ())
		question = super().create(validated_data)
		self._update_answers(question, answers)
		return question

	def update(self, instance, validated_data):
		answers = validated_data.pop('answers', ())
		question = super().update(instance, validated_data)
		if answers or validated_data.get('q_type') == NO_ANSWERS_TYPE:
			models.Answer.objects.filter(question=question).delete()
		self._update_answers(question, answers)
		return question

	def _update_answers(self, question, answers):
		if question.q_type != NO_ANSWERS_TYPE:
			for answer in answers:
				models.Answer.objects.create(question=question, **answer)


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
