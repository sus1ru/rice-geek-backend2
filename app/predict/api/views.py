from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema

from core.models import Predict
from predict.api.serializers import PredictImageSerializer, PredictSerializer

from PIL import Image
import tensorflow as tf
import numpy as np
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


# Create your views here.
class PredictViewSet(viewsets.ModelViewSet):
    """View to manage Prediction APIs."""
    serializer_class = PredictSerializer
    queryset = Predict.objects.all()
    parser_classes = (MultiPartParser,)

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     """Retrieve atendance for authenticated users."""
    #     return self.queryset.filter(
    #         user=self.request.user
    #     ).order_by('-attended_at')

    # def get_serializer_class(self):
    #     if self.action == 'upload_image':
    #         return PredictImageSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PredictImageSerializer

        return self.serializer_class


    def predictImage(self, image_path):
        class_names = ["brownspot", "healthy", "leafblast", "blight"]
        model = tf.keras.models.load_model("/app/predict/models/rice2.h5")

        image = np.array(
            Image.open(image_path).convert("RGB").resize((256, 256))
        )
        image = image / 255
        img_array = tf.expand_dims(image, 0)
        predictions = model.predict(img_array)

        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = str(round(100*np.max(predictions[0]), 2))

        context = {'prediction':predicted_class, 'confidence':confidence}
        return context


    @swagger_auto_schema(operation_description='Upload file...',)
    # @action(detail=False, methods=['POST'])
    def create(self, request, *args, **kwargs):
        # image =  request.FILES['image']
        request.data['owner'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            predict = serializer.save()
            res = self.predictImage(predict.image)
            res['owner'] = predict.owner.id
            _serializer = PredictSerializer(predict, data=res)
            if _serializer.is_valid():
                _serializer.save()
            else:
                predict.delete()
                return Response(_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
