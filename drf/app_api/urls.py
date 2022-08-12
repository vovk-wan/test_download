from django.urls import path
from app_api.api import (
    CsvProcessingView,
    CsvProcessingBoto3View,
    GetResultView,
    GetWorkingTasksView
)

urlpatterns = [
    path('add_task', CsvProcessingView.as_view()),
    path('add_task_boto', CsvProcessingBoto3View.as_view()),
    path('get_info', GetWorkingTasksView.as_view()),
    path('get_result', GetResultView.as_view())
]