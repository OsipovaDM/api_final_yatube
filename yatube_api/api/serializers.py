import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from posts.models import Group, Comment, Post, Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    '''
    Декодировать изображение из base64
    '''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class GroupSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные групп в "удобочитаемый вид"
    '''

    class Meta:
        fields = ('title', 'slug', 'description')
        model = Group


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('text', 'pub_date', 'author', 'image', 'group')
        model = Post
        read_only_fields = ('pub_date', 'author')


class CommentSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные комментариев в "удобочитаемый вид"
    '''
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ('author', 'post', 'text', 'created')
        model = Comment
        read_only_fields = ('author', 'post', 'created')


class FollowSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные подписок в "удобочитаемый вид"
    '''
    user = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow
