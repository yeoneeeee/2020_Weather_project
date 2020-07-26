from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, # <- 특정 사용자 모델에 종속적이지 않다.
        on_delete=models.CASCADE
    )
    phone = models.CharField(
        max_length=100
    )

    class Meta:
        db_table = 'account_profile'
        app_label = 'account'