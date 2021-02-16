"""Permissions."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class GetOrAdmin(BasePermission):
	"""Default permissions."""

	def has_permission(self, request, _view):
		return request.method in SAFE_METHODS or request.user.is_staff
