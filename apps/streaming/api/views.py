from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from apps.streaming.models import Streaming, Comment
from apps.streaming.api.serializers import (
    CommentSerializer,
    CreateCommentSerializer,
    CreateStreamingSerializer,
    StreamingSerializer,
)


class StreamingView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self):
        streaming = Streaming.objects.filter(code=self.kwargs['pk']).first()
        if streaming is None:
            raise NotFound()
        return streaming

    def create(self, request):
        serializer = CreateStreamingSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        streaming = serializer.save()

        response_serializer = StreamingSerializer(streaming, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk):
        streaming = self.get_object()
        serializer = StreamingSerializer(streaming, context=self.get_serializer_context())
        
        return Response(serializer.data)
    
    @action(methods=['post'], detail=True)
    def start(self, request, pk):
        streaming = self.get_object()
        streaming.start()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True)
    def stop(self, request, pk):
        streaming = self.get_object()
        streaming.stop()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        query_params = self.request.query_params
        streaming_code = query_params.get('stream')
        return Comment.objects.filter(streaming=streaming_code).order_by('-date_created')

    def create(self, request):
        serializer = CreateCommentSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        response_serializer = CommentSerializer(comment, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request):
        streaming = self.paginate_queryset(self.get_queryset())
        serializer = CommentSerializer(streaming, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)


streaming_view = StreamingView
comment_view = CommentView
