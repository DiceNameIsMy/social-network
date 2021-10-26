from rest_framework.permissions import BasePermission


class IsRelated(BasePermission):
    """ Provide `related_field: str` in your view 
    which is field to be checked
    """
    message = 'user have to be related to the object'

    def has_object_permission(self, request, view, obj):
        related_user = getattr(obj, view.related_field)
        return related_user == request.user


class IsManyRelated(BasePermission):
    """ Provide `related_field: str` in your view 
    which is field to be checked
    """
    message = 'user have to be related to the object'

    def has_object_permission(self, request, view, obj):
        related_users = getattr(obj, view.related_field).all()
        return request.user in related_users

