from rest_framework.filters import BaseFilterBackend


class URLRelatedFilter(BaseFilterBackend):
    related_field = 'url_related_field'
    related_kwarg = 'url_related_kwarg'

    def filter_queryset(self, request, queryset, view):
        assert hasattr(view, self.related_field), f'`{self.related_field}` should be provided'
        assert hasattr(view, self.related_kwarg), f'`{self.related_kwarg}` should be provided'

        filter_kwarg = {
            getattr(view, self.related_field): view.kwargs[getattr(view, self.related_kwarg)]
        }
        return queryset.filter(**filter_kwarg)


class UserRelatedFilter(BaseFilterBackend):
    """ add `user_field:str` in your view which
    is field that is related to user
    """
    def filter_queryset(self, request, queryset, view):
        assert hasattr(view, 'user_field'), '`user_field` should be added in view'

        return queryset.filter(**{view.user_field: request.user})
