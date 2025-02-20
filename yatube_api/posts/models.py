from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    '''
    Группа публикаций, объединенных общей тематикой
    '''
    title = models.CharField(max_length=32)
    slug = models.CharField(max_length=32)
    description = models.TextField()

    def __str__(self):
        return self.description


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(
        upload_to='posts/', null=True, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        related_name='posts', null=True, blank=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)


class Follow(models.Model):
    '''
    Связывает подписчиков с пользователями, на которых они подписаны
    '''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows_user')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows_following')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'following'), name='uk1'),
        )
