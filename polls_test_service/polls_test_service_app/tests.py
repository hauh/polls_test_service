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

	poll = {
		'title': "Test Poll",
		'description': "Poll description.",
		'start_date': datetime.now(),
		'end_date': datetime.now()
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
	"""Tests for Questions and Answers."""

	q_list_url = reverse('questions-list', args=(1,))
	q_url = reverse('question-detail', args=(1, 1))
	question = {
		'text': "Test question",
		'q_type': 1,
		'answers': [
			{'text': "Answer 1"},
			{'text': "Answer 2"},
			{'text': "Answer 3"},
		]
	}

	def setUp(self):
		self.request('post', self.polls_url, HTTP_201_CREATED, self.poll)

	def test_create(self):
		data = self.request('post', self.q_list_url, HTTP_201_CREATED, self.question)
		self.assertIn('id', data)
		self.assertIn('q_type', data)
		self.assertIn('answers', data)
		polls = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertDictEqual(polls[0]['questions'][0], data)

		no_answers_q = {**self.question, 'q_type': 0}
		data = self.request('post', self.q_list_url, HTTP_201_CREATED, no_answers_q)
		self.assertListEqual(data['answers'], [])
		polls = self.request('get', self.polls_url, HTTP_200_OK)
		self.assertDictEqual(polls[0]['questions'][1], data)

	def test_invalid_create(self):
		for field, invalid in (
			('text', ""),
			('text', None),
			('q_type', 111),
			('q_type', "err"),
			('q_type', None),
			('answers', None),
			('answers', "err"),
			('answers', []),
			('answers', ["err"]),
			('answers', [{'not_text': "Text"}]),
			('answers', [{'text': None}]),
			('answers', [{'text': ""}]),
		):
			invalid_data = {**self.question, field: invalid}
			self.request('post', self.q_list_url, HTTP_400_BAD_REQUEST, invalid_data)

	def test_update(self):
		self.request('post', self.q_list_url, HTTP_201_CREATED, self.question)
		for field, new in (
			('text', "New question text"),
			('q_type', 2),
			('answers', []),
			('answers', [{'text': "New answer 1"}]),
			('answers', [{'text': "New answer 2"}, {'text': "New answer 3"}]),
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
