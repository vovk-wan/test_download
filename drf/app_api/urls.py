from django.urls import path
from app_api.api import CsvProcessingView, GetResultView

urlpatterns = [
    path('add_task', CsvProcessingView.as_view()),
    path('get_result', GetResultView.as_view())
]