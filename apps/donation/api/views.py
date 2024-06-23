from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from apps.donation.models import Donation
from apps.donation.api.serializers import (
    ConfirmDonationSerializer,
    CreateDonationSerializer,
    DonationSerializer,
)
from apps.libs.midtrans import Midtrans


class DonationView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        streaming_code = self.request.query_params.get('stream')
        return Donation.objects.filter(streaming=streaming_code, status__in=(Donation.NEED_CONFIRMATION_STATUS, Donation.SUCCESS_STATUS)).order_by('date_created')
    
    def get_object(self):
        donation = Donation.objects.filter(id=self.kwargs['pk']).first()
        if donation is None:
            raise NotFound()
        return donation

    def create(self, request):
        serializer = CreateDonationSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        donation = serializer.save()

        response_serializer = DonationSerializer(donation, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request):
        donations = self.paginate_queryset(self.get_queryset())
        serializer = DonationSerializer(donations, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)
    
    def retrieve(self, request, pk):
        donation = self.get_object()
        serializer = DonationSerializer(donation, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(methods=['post'], detail=True)
    def confirm(self, request, pk):
        serializer = ConfirmDonationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid = serializer.validated_data.get('valid')

        donation = self.get_object()
        if valid:
            donation.confirm(request.user)
        else:
            donation.reject(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MidtransCallbackView(GenericViewSet):
    permission_classes = ()
    authentication_classes = ()

    def create(self, request):
        midtrans = Midtrans()
        if not midtrans.validate_transaction_signature(request.data):
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = request.data.get("transaction_id")
        payment = midtrans.get_transaction_detail(transaction_id)
        donation = Donation.objects.filter(payment_id=transaction_id).first()
        if donation is None:
            return Response()
        
        if payment.is_success:
            donation.mark_as_success()
        elif payment.is_failed:
            donation.mark_as_failed()

        return Response()


donation_view = DonationView
midtrans_callback_view = MidtransCallbackView
