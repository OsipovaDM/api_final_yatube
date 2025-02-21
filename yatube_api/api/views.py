from django.shortcuts import get_object_or_404
from rest_framework import mixins, filters, serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Group, Comment, Post, Follow
from .permissions import AuthorOrReadOnly
from .serializers import (
    GroupSerializer, CommentSerializer, PostSerializer, FollowSerializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Обработка GET запросов для групп
    Возвращает информацию без возможности изменения или записи
    '''
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    '''
    Обработка всех видов запросов для публикаций
    Любые операции CRUD с моделью
    '''
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # Переопределение методова вывода списка элементов
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if 'limit' in request.query_params or 'offset' in request.query_params:
            # Одна страница списка
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        # Полный список
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    '''
    Обработка всех видов запросов для комментариев
    Любые операции CRUD с моделью
    '''
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    # Выделение публикации из запроса
    def get_post(self):
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, pk=post_id)
        return post

    # Извлечение параметров из запроса
    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def perform_create(self, serializer):
        post = self.get_post()
        serializer.save(author=self.request.user, post_id=post.id)


# CreateModelMixin — создать объект (для обработки запросов POST);
# ListModelMixin — вернуть список объектов (для обработки запросов GET);
# RetrieveModelMixin — вернуть объект (для обработки запросов GET);
# UpdateModelMixin — изменить объект (для обработки запросов PUT и PATCH);
# DestroyModelMixin — удалить объект (для обработки запросов DELETE).
class FollowViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin, viewsets.GenericViewSet):
    '''
    Обработка GET POST запросов для подписок
    '''
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        user = self.request.user
        return user.followings.all()

    def perform_create(self, serializer):
        user = self.request.user
        following = serializer.validated_data.get('following')
        if user == following:
            raise serializers.ValidationError(
                'Пользователь не может подписаться сам на себя.')
        elif Follow.objects.all().filter(
                user=user, following=following).exists():
            raise serializers.ValidationError(
                'Пользователь уже подписан на данного автора.')
        else:
            serializer.save(user=user)
