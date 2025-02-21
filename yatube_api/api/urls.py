from django.urls import include, path
from rest_framework import routers

from api.views import GroupViewSet, CommentViewSet, PostViewSet, FollowViewSet

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'posts/(?P<post_id>[^/.]+)/comments',
                CommentViewSet,
                basename='comments',
                )
router.register(r'posts', PostViewSet)
router.register(r'follow', FollowViewSet, basename='follows')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls.jwt')),
]
