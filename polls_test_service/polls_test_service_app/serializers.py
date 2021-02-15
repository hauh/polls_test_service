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
		return value

	def validate(self, attrs):
		if attrs['q_type'] == NO_ANSWERS_TYPE:
			attrs.pop('answers', None)
		elif not attrs.get('answers'):
			raise ValidationError("Answers are required for this type of question.")
		return attrs

	def create(self, validated_data):
		answers = validated_data.pop('answers', ())
		question = super().create(validated_data)
		for answer in answers:
			models.Answer.objects.create(question=question, **answer)
		return question

	def update(self, instance, validated_data):
		answers = validated_data.pop('answers', ())
		question = super().update(instance, validated_data)
		if answers or validated_data.get('q_type') == NO_ANSWERS_TYPE:
			models.Answer.objects.filter(question=question).delete()
		for answer in answers:
			models.Answer.objects.create(question=question, **answer)
		return question


class Poll(ModelSerializer):
	"""Poll serializer."""

	questions = Question(many=True, read_only=True)

	class Meta:
		model = models.Poll
		fields = '__all__'

	def update(self, instance, validated_data):
		validated_data.pop('start_date', None)
		return super().update(instance, validated_data)
