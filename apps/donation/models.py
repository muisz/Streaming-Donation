from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.streaming.models import Streaming
from apps.utils.models import BaseModel
from apps.libs.midtrans import Midtrans, RequestPayment

User = get_user_model()


class ManualPayment:
    bank_name = None
    payment_file = None

    def __init__(self, bank_name, payment_file):
        self.bank_name = bank_name
        self.payment_file = payment_file


class Donation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='donations')
    streaming = models.ForeignKey(Streaming, on_delete=models.PROTECT, related_name='donations')
    amount = models.FloatField()

    INSTANT_PAYMENT = 1
    MANUAL_PAYMENT = 2
    PAYMENT_CHOICES = (
        (INSTANT_PAYMENT, 'Instant Payment'),
        (MANUAL_PAYMENT, 'Manual Payment'),
    )
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_CHOICES)

    PENDING_STATUS = 1
    NEED_CONFIRMATION_STATUS = 2
    SUCCESS_STATUS = 3
    FAILED_STATUS = 4
    STATUS_CHOICES = (
        (PENDING_STATUS, 'Pending'),
        (NEED_CONFIRMATION_STATUS, 'Need confirmation'),
        (SUCCESS_STATUS, 'Success'),
        (FAILED_STATUS, 'Failed'),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING_STATUS)
    success_at = models.DateTimeField(null=True)

    # instant payment
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    va_number = models.CharField(max_length=100, null=True, blank=True)
    bank_code = models.CharField(max_length=100, null=True, blank=True)

    # manual payment
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    payment_file = models.FileField(null=True, blank=True)

    @classmethod
    def create_manual_payment(cls, streaming, user, amount, payment: ManualPayment):
        donation = cls(
            user=user,
            streaming=streaming,
            amount=amount,
            payment_type=Donation.MANUAL_PAYMENT,
            status=Donation.NEED_CONFIRMATION_STATUS,
            bank_name=payment.bank_name,
            payment_file=payment.payment_file,
        )
        donation.save()
        return donation
    
    @classmethod
    def create_instant_payment(cls, streaming, user, amount, bank_code):
        donation = cls(
            user=user,
            streaming=streaming,
            amount=amount,
            payment_type=Donation.INSTANT_PAYMENT,
            status=Donation.PENDING_STATUS,
        )
        donation.save()

        midtrans_payment = RequestPayment(
            order_id=donation.id,
            gross_amount=amount,
            bank_code=bank_code,
        )
        midtrans_response = Midtrans().create_payment(midtrans_payment)
        donation.va_number = midtrans_response.va_number
        donation.payment_id = midtrans_response.transaction_id
        donation.bank_code = bank_code
        donation.save()

        return donation
    
    def confirm(self, by_user):
        if self.streaming.user != by_user:
            raise Exception('User is not a streamer')

        if self.status != self.NEED_CONFIRMATION_STATUS:
            raise Exception('Confirmation not needed')
        
        self.status = self.SUCCESS_STATUS
        self.success_at = timezone.now()
        self.save()

    def reject(self, by_user):
        if self.streaming.user != by_user:
            raise Exception('User is not a streamer')
        
        if self.status != self.NEED_CONFIRMATION_STATUS:
            raise Exception('Confirmation not needed')
        
        self.status = self.FAILED_STATUS
        self.save()

    def mark_as_success(self):
        self.status = self.SUCCESS_STATUS
        self.success_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        self.status = self.FAILED_STATUS
        self.save()
