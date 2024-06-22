from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.streaming.models import Streaming, BankInfo



class BankSerializer(serializers.Serializer):
    name = serializers.CharField()
    holder_name = serializers.CharField()
    account_number = serializers.CharField()


class CreateStreamingSerializer(serializers.ModelSerializer):
    bank = BankSerializer()

    def validate(self, attrs):
        self.validate_date(attrs.get('date_start'), attrs.get('date_end'))
        return super().validate(attrs)
    
    def validate_date(self, start, end):
        if start > end:
            raise ValidationError("Date start cannot greater than end")

    def create(self, validated_data):
        user = self.context.get('request').user
        streaming = Streaming.create_streaming(
            user=user,
            start=validated_data.get('date_start'),
            end=validated_data.get('date_end'),
            bank=BankInfo(**validated_data.get('bank')),
        )
        return streaming

    class Meta:
        model = Streaming
        fields = ('date_start', 'date_end', 'bank')


class StreamingSerializer(serializers.ModelSerializer):
    bank = serializers.SerializerMethodField()

    def get_bank(self, obj: Streaming):
        return {
            "name": obj.bank_name,
            "holder_name": obj.bank_holder_name,
            "account_number": obj.bank_account_number,
        }

    class Meta:
        model = Streaming
        fields = (
            'code',
            'date_start',
            'date_end',
            'status',
            'user',
            'date_created',
            'date_updated',
            'donation_total',
            'bank',
        )
