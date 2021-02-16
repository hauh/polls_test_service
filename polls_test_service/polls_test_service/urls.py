"""URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from polls_test_service_app.views import (
	Answer, Poll, PollsList, Question, QuestionsList, UserAnswers
)

router = DefaultRouter()

urlpatterns = router.urls + [
	path('polls/', include([
		path('', PollsList.as_view(), name='polls-list'),
		path('<pk>/', Poll.as_view(), name='poll-details'),
		path('<int:poll_id>/', include([
			path('answer/', Answer.as_view(), name='answer-create'),
			path('questions/', QuestionsList.as_view(), name='questions-list'),
			path('questions/<pk>/', Question.as_view(), name='question-details'),
		]))
	])),
	path('users/', include([
		path('<int:user_id>/', UserAnswers.as_view(), name='answers-list'),
		path('login/', obtain_auth_token, name='login'),
	]))
]
