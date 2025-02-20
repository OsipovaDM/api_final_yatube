import base64  # Перевод картинок в строку base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from posts.models import Group, Comment, Post, Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    '''
    Перевод файла в код
    '''
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class GroupSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные групп в "удобочитаемый вид"
    '''

    class Meta:
        fields = '__all__'
        model = Group


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    # group = serializers.PrimaryKeyRelatedField(required=False)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('post',)


class FollowSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные подписок в "удобочитаемый вид"
    '''
    # передать вместо id строковые представления связанных объектов
    user = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    following = SlugRelatedField(
        slug_field='username', queryset=User.objects.all())

    class Meta:
        fields = '__all__'
        model = Follow
