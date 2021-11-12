from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins


class ListRetrieveViewSet(
    mixins.ListModelMixin,                      
    mixins.RetrieveModelMixin,
    GenericViewSet):
    pass


class ListCreateRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet):
    pass


class ListCRUDViewSet(ModelViewSet):
    pass