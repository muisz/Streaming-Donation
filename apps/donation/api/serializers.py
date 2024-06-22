from rest_framework import serializers

from apps.donation.models import Donation, ManualPayment
from apps.utils.file import get_content_file_from_base64


class ManualPaymentSerializer(serializers.Serializer):
    bank_name = serializers.CharField()
    payment_file = serializers.CharField()

    def validate_payment_file(self, value: str):
        if not value:
            return None
        return get_content_file_from_base64(value)


class CreateDonationSerializer(serializers.ModelSerializer):
    manual_payment = ManualPaymentSerializer(required=False, allow_null=True)

    def create(self, validated_data):
        manual_payment = validated_data.get('manual_payment')
        if manual_payment:
            return self.create_manual_payment(validated_data)
    
    def create_manual_payment(self, validated_data):
        user = self.context.get('request').user
        donation = Donation.create_manual_payment(
            streaming=validated_data.get('streaming'),
            user=user,
            amount=validated_data.get('amount'),
            payment=ManualPayment(**validated_data.get('manual_payment'))
        )
        return donation

    class Meta:
        model = Donation
        fields = (
            'streaming',
            'amount',
            'manual_payment',
        )
    
class DonationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    manual_payment = serializers.SerializerMethodField()

    def get_user(self, obj: Donation):
        user = obj.user
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        }
    
    def get_manual_payment(self, obj: Donation):
        request = self.context.get('request')
        payment_file = obj.payment_file
        if payment_file:
            payment_file = payment_file.url
        return {
            'bank_name': obj.bank_name,
            'payment_file': request.build_absolute_uri(payment_file),
        }

    class Meta:
        model = Donation
        fields = (
            'id',
            'user',
            'amount',
            'status',
            'payment_type',
            'manual_payment',
            'success_at',
            'date_created',
            'date_updated',
        )


class ConfirmDonationSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
