from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import GenerateStoryAPIView, UserStoryListAPIView, ContinueStoryAPIView
router = DefaultRouter()
router.register(r'stories', UserStoryListAPIView, basename='stories')

urlpatterns = [
    path('generate', GenerateStoryAPIView.as_view(), name='generate-story'),
    path('continue/<int:story_id>/', ContinueStoryAPIView.as_view(), name='continue-story'),
]

urlpatterns += router.urls