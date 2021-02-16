"""Tests."""

from datetime import datetime, timedelta

from django.urls import reverse
from rest_framework.status import (
	HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
	HTTP_404_NOT_FOUND
)
from rest_framework.test import APITestCase


class BaseTest(APITestCase):
	"""For making reqests."""

	def request(self, method, url, expected_status_code, data=None):
		response = getattr(self.client, method)(url, data, format='json')
		self.assertEqual(response.status_code, expected_status_code, response.data)
		return response.data

	polls_url = reverse('polls-list')
	new_poll_url = reverse('poll-detail', args=(1,))
	q_list_url = reverse('questions-list', args=(1,))
	q_url = reverse('question-detail', args=(1, 1))
	answer_url = reverse('answer-create', args=(1,))
	list_answers_url = reverse('answers-list', args=(1,))

	poll = {
		'title': "Test Poll",
		'description': "Poll description.",
		'start_date': datetime.now(),
		'end_date': datetime.now()
	}
	question = {
		'text': "Test question",
		'q_type': 1,
		'choices': [
			{'text': "Choice 1"},
			{'text': "Choice 2"},
			{'text': "Choice 3"},
		]
	}


class PollsTest(BaseTest):
	"""Tests for Polls."""

	def test_create(self):
		data = self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)
		self.assertIn('id', data)
		data.pop('id')
		self.assertIn('questions', data)
		self.assertListEqual(data.pop('questions'), [])
		for date in ('start_date', 'end_date'):
			self.assertIn(date, data)
			data[date] = datetime.fromisoformat(data[date][:-1])
		self.assertDictEqual(self.poll, data)

	def test_create_invalid(self):
		for field, invalid in (
			('title', None),
			('title', ""),
			('description', None),
			('description', ""),
			('start_date', None),
			('start_date', ""),
			('start_date', datetime.now() + timedelta(hours=1)),
			('start_date', ""),
			('end_date', None),
			('end_date', datetime.now() - timedelta(hours=1)),
		):
			invalid_data = {**self.poll, field: invalid}
			self.request('post', self.polls_url, HTTP_400_BAD_REQUEST, invalid_data)
		for key in self.poll:
			invalid_data = {**self.poll}
			invalid_data.pop(key)
			self.request('post', self.polls_url, HTTP_400_BAD_REQUEST, invalid_data)

	def test_retrieve(self):
		for _ in range(10):
			self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)
		data = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertEqual(len(data), 10)
		for i, poll in enumerate(data, 1):
			self.assertIn('id', poll)
			self.assertEqual(poll['id'], i)

	def test_update(self):
		self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)
		for field, new in (
			('title', "New title"),
			('description', "New description"),
		):
			data = self.request('patch', self.new_poll_url, HTTP_200_OK, {field: new})
			self.assertIn(field, data)
			self.assertEqual(data[field], new)

		new_date = datetime.now() + timedelta(days=1)
		new_start = {'start_date': new_date}
		data = self.request('patch', self.new_poll_url, HTTP_200_OK, new_start)
		parsed_date = datetime.fromisoformat(data['start_date'][:-1])
		self.assertNotEqual(new_date, parsed_date)

		new_end = {'end_date': new_date}
		data = self.request('patch', self.new_poll_url, HTTP_200_OK, new_end)
		parsed_date = datetime.fromisoformat(data['end_date'][:-1])
		self.assertEqual(new_date, parsed_date)

	def test_delete(self):
		self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)
		data = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertEqual(len(data), 1)
		self.request('delete', self.new_poll_url, HTTP_204_NO_CONTENT)
		data = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertEqual(len(data), 0)
		self.request('get', self.new_poll_url, HTTP_404_NOT_FOUND)


class QuestionsTest(BaseTest):
	"""Tests for Questions and Choices."""

	def setUp(self):
		self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)

	def test_create(self):
		data = self.request('post', self.q_list_url, HTTP_201_CREATED, self.question)
		self.assertIn('id', data)
		self.assertIn('q_type', data)
		self.assertIn('choices', data)
		polls = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertDictEqual(polls[0]['questions'][0], data)

		no_choices_q = {**self.question, 'q_type': 0}
		data = self.request('post', self.q_list_url, HTTP_201_CREATED, no_choices_q)
		self.assertListEqual(data['choices'], [])
		polls = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertDictEqual(polls[0]['questions'][1], data)

	def test_invalid_create(self):
		for field, invalid in (
			('text', ""),
			('text', None),
			('q_type', 111),
			('q_type', "err"),
			('q_type', None),
			('choices', None),
			('choices', "err"),
			('choices', []),
			('choices', ["err"]),
			('choices', [{'not_text': "Text"}]),
			('choices', [{'text': None}]),
			('choices', [{'text': ""}]),
		):
			invalid_data = {**self.question, field: invalid}
			self.request('post', self.q_list_url, HTTP_400_BAD_REQUEST, invalid_data)

	def test_update(self):
		self.request('post', self.q_list_url, HTTP_201_CREATED, self.question)
		for field, new in (
			('text', "New question text"),
			('q_type', 2),
			('choices', []),
			('choices', [{'text': "New choice 1"}]),
			('choices', [{'text': "New choice 2"}, {'text': "New choice 3"}]),
		):
			question = self.request('patch', self.q_url, HTTP_200_OK, {field: new})
			polls = self.request('get', self.polls_url, HTTP_200_OK)
			self.assertEqual(polls[0]['questions'][0], question)

	def test_delete(self):
		self.request('post', self.q_list_url, HTTP_201_CREATED, self.question)
		data = self.request('get', self.new_poll_url, HTTP_200_OK)
		self.assertEqual(len(data['questions']), 1)
		self.request('delete', self.q_url, HTTP_204_NO_CONTENT)
		data = self.request('get', self.new_poll_url, HTTP_200_OK)
		self.assertEqual(len(data['questions']), 0)


class AnswersTest(BaseTest):
	"""Tests for user's Answers."""

	def setUp(self):
		self.answer = {
			'user_id': 1,
			'answers': [
				{'question_id': 1, 'choice': "arbitrary"},
				{'question_id': 2, 'choice': 1},
				{'question_id': 3, 'choice': 4},
				{'question_id': 3, 'choice': 5},
			]
		}
		self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)
		arbitrary_answer_q = {**self.question, 'q_type': 0}
		self.request('post', self.q_list_url, HTTP_201_CREATED, arbitrary_answer_q)
		self.request('post', self.q_list_url, HTTP_201_CREATED, self.question)
		multiple_answers_q = {**self.question, 'q_type': 2}
		self.request('post', self.q_list_url, HTTP_201_CREATED, multiple_answers_q)

	def test_create(self):
		d = self.request('post', self.answer_url, HTTP_201_CREATED, self.answer)
		self.assertIn('result', d)
		self.assertEqual(d['result'], "Answers saved: 4.")

	def test_duplicate_answer(self):
		self.request('post', self.answer_url, HTTP_201_CREATED, self.answer)
		self.request('post', self.answer_url, HTTP_400_BAD_REQUEST, self.answer)

	def test_not_enough_answers(self):
		del self.answer['answers'][0]
		self.request('post', self.answer_url, HTTP_400_BAD_REQUEST, self.answer)

	def test_not_a_string(self):
		self.answer['answers'][0]['choice'] = 1
		self.request('post', self.answer_url, HTTP_400_BAD_REQUEST, self.answer)

	def test_not_an_int(self):
		self.answer['answers'][1]['choice'] = "must be an id"
		self.request('post', self.answer_url, HTTP_400_BAD_REQUEST, self.answer)

	def test_multiple_choice(self):
		self.answer['answers'].append({'question_id': 2, 'choice': 2})
		self.request('post', self.answer_url, HTTP_400_BAD_REQUEST, self.answer)

	def test_non_existing_choice(self):
		self.answer['answers'].append({'question_id': 3, 'choice': 999})
		self.request('post', self.answer_url, HTTP_400_BAD_REQUEST, self.answer)

	def test_user_answers(self):
		self.request('post', self.answer_url, HTTP_201_CREATED, self.answer)
		data = self.request('get', self.list_answers_url, HTTP_200_OK)
		self.assertEqual(len(data), 1)
		expected = {
			'id': 1,
			'title': "Test Poll",
			'description': "Poll description.",
			'questions': [
				{
					'id': 1,
					'text': "Test question",
					'choices': ["arbitrary"]
				},
				{
					'id': 2,
					'text': "Test question",
					'choices': ["Choice 1"]
				},
				{
					'id': 3,
					'text': "Test question",
					'choices': ["Choice 1", "Choice 2"]
				},
			]
		}
		self.assertDictEqual(expected, data[0])
