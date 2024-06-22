import random
import string
from django.contrib.auth import get_user_model
from django.db import models

from apps.utils.models import BaseModel

User = get_user_model()


class BankInfo:
    name = None
    holder_name = None
    account_number = None

    def __init__(self, name, holder_name, account_number):
        self.name = name
        self.holder_name = holder_name
        self.account_number = account_number


class Streaming(BaseModel):
    code = models.CharField(max_length=8, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='streaming')
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    PENDING = 1
    LIVE = 2
    ENDED =3
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (LIVE, "Live"),
        (ENDED, "Ended"),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    
    # bank info for manual donation
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_holder_name = models.CharField(max_length=100, null=True, blank=True)
    bank_account_number = models.CharField(max_length=20, null=True, blank=True)

    donation_total = models.FloatField(default=0)

    @classmethod
    def create_streaming(cls, user, start, end, bank: BankInfo):
        streaming = cls(
            user=user,
            date_start=start,
            date_end=end,
            bank_name=bank.name,
            bank_holder_name=bank.holder_name,
            bank_account_number=bank.account_number,
        )
        streaming.set_code()
        streaming.save()

        return streaming
    
    def set_code(self):
        code = ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(8))
        self.code = code
    
    def start(self):
        self.status = self.LIVE
        self.save()
    
    def stop(self):
        self.status = self.ENDED
        self.save()


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comments')
    streaming = models.ForeignKey(Streaming, on_delete=models.PROTECT, related_name='streamings')
    comment = models.TextField()

    @classmethod
    def create(cls, comment, user, streaming):
        return cls.objects.create(
            comment=comment,
            user=user,
            streaming=streaming
        )
