"""URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from polls_test_service_app.views import (
	Poll, PollsList, Question, QuestionsList
)

router = DefaultRouter()

urlpatterns = router.urls + [
	path('polls/', include([
		path('', PollsList.as_view(), name='polls-list'),
		path('<pk>/', Poll.as_view(), name='poll-detail'),
		path('<int:poll_id>/', include([
			path('questions/', QuestionsList.as_view(), name='questions-list'),
			path('questions/<pk>/', Question.as_view(), name='question-detail'),
		]))
	])),
]
