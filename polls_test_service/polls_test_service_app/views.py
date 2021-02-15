"""Views."""

from rest_framework.generics import (
	ListCreateAPIView, RetrieveUpdateDestroyAPIView
)

from polls_test_service_app import models, serializers


class Polls(ListCreateAPIView):
	"""GET, POST Polls."""

	queryset = models.Poll.objects.all()
	serializer_class = serializers.Poll


class PollConcrete(RetrieveUpdateDestroyAPIView):
	"""GET, PATCH, DELETE Polls."""

	queryset = models.Poll.objects.all()
	serializer_class = serializers.Poll
