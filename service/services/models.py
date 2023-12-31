import logging
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete

from clients.models import Client
from services.receivers import delete_cache_total_sum
from services.tasks import set_price, set_comment

logger = logging.getLogger(__name__)


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def __str__(self):
        return f'Service: {self.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.__full_price != self.full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def __str__(self):
        return f'Plan: {self.plan_type}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.__discount_percent != self.discount_percent:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=50, default='', db_index=True, blank=True)

    field_a = models.CharField(max_length=50, default='', blank=True)
    field_b = models.CharField(max_length=50, default='', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['field_a', 'field_b'])
        ]

    def __str__(self):
        return f'{self.client} | {self.service} | {self.plan}'

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        if creating:
            set_price.delay(self.pk)


post_delete.connect(delete_cache_total_sum, sender=Subscription)
