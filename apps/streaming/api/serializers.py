from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.streaming.models import Streaming, BankInfo, Comment



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


class CreateCommentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context.get('request').user
        return Comment.create(
            comment=validated_data.get('comment'),
            user=user,
            streaming=validated_data.get('streaming'),
        )

    class Meta:
        model = Comment
        fields = ('streaming', 'comment')


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj: Comment):
        user = obj.user
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }

    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'date_created')
