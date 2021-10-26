from rest_framework.filters import BaseFilterBackend


class URLRelatedFilter(BaseFilterBackend):
    related_field = 'url_related_field'
    related_kwarg = 'url_related_kwarg'

    def filter_queryset(self, request, queryset, view):
        assert hasattr(view, self.related_field), f'`{self.related_field}` should be provided'

        if hasattr(view, 'get_url_related_pk'):
            pk = view.get_url_related_pk()
        else:
            assert hasattr(view, self.related_kwarg), f'`{self.related_kwarg}` should be provided'
            pk = view.kwargs[getattr(view, self.related_kwarg)]

        filter_kwarg = {
            getattr(view, self.related_field): pk
        }
        return queryset.filter(**filter_kwarg)
