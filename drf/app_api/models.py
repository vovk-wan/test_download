from django.db import models
from django.contrib.auth.admin import User


class Task(models.Model):
    user = models.ForeignKey(
        User, related_name='tasks',
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    status = models.CharField(max_length=50, default='work', verbose_name='Status')

    class Meta:
        db_table = 'tasks'
