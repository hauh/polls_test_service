"""URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from polls_test_service_app.views import PollConcrete, Polls


router = DefaultRouter()

urlpatterns = router.urls + [
	path('polls/', include([
		path('', Polls.as_view(), name='polls'),
		path('<pk>/', PollConcrete.as_view(), name='poll-detail'),
	])),
]
