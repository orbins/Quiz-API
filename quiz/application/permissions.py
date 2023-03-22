from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Ограничение, определяющее, что только автор записи может
    её изменять, другие пользователи - лишь читать
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user