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

    def disease_info(self, disease): 
        disease_about = {
            "leafblast": ["Symptoms of rice blast are caused by the fungus Magnaporthe grisea, which is one of the most destructive diseases of rice. The fungus can survive on the straw after harvest and thus be carried over to the next season. The disease is favored by cool temperatures, frequent rainfalls, and low soil moisture. A prolonged period of leaf moisture is also required for infection. Finally, plants sown in soils with high nitrogen or low silicon levels are more likely to develop the disease.",
                            "Chemical treatment is the most effective way to solve eradicate the blast disease. Seed treatment with thiram is effective against the disease. Fungicides containing azoxystrobin, or active ingredients of the family of triazoles or strobilurins can also be sprayed at nursery, tillering and panicle emergence stages to control rice blast. One or two fungicide applications at heading can be effective in controlling the disease.", ],
            "brownspot": ["The symptoms are caused by the fungus, Cochliobolus miyabeanus. It can survive in seeds for more than four years and spread from plant to plant through airborne spores. Infected plant debris left in the field and weeds are other common ways to spread the disease. High humidity (86-100%), prolonged periods of leaf moisture and high temperatures (16-36°C) are very favorable for the fungi. The disease often occurs in fields with mismanagement of soil fertility, mainly in terms of micronutrients.",
                            "Before planting treat seed with hot water: 53-54°C for 10-12 minutes. During growth ensure that plants have correct nutrition: apply fertilizer at recommended rates. After harvest collect straw and other debris after harvest and burn it with the stubble, or plough everything into the soil. For chemical control IRRI recommends seed treatments with iprodione, stilburins (azoxystrobin or trifloxystrobin), azole (propiconazole), or carbendazin fungicides.", ],
            # Replace hispa with the blight's info
            "blight": ["Damage is caused by the adults and larvae of the rice hispa, Dicladispa armigera. Adult beetles scrape the upper surface of leaf blades leaving only the lower layer. It feeds inside the leaf tissue by mining along the leaf axis, and subsequently pupates internally. Grassy weeds, heavy fertilization, heavy rains and high relative humidity favor rice hispa infestation. Rice field appears burnt when severely infested.",
                        "A cultural control method that is recommended for the rice hispa is to avoid over fertilizing the field. Close plant spacing results in greater leaf densities that can tolerate higher hispa numbers. To prevent egg laying of the pests, the shoot tips can be cut. Among the biological control agents, there are small wasps that attack the eggs and larvae. A reduviid bug eats upon the adults. There are three fungal pathogens that attack the adults. For chmeical control following ingredients is recommended: chlorpyriphos, malathion, cypermethrin, fenthoate.", ],
            "healthy": ["Ey yo! your leaf healthy.",
                        "Just continue doing what you are doing.", ],
        }
        return disease_about.get(disease, ["NA", "NA"])

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

        index = np.argmax(predictions[0])
        predicted_class = class_names[index]
        confidence = str(round(100*np.max(predictions[0]), 2))

        context = {'predictedLabel':predicted_class, 'index': str(index), 'confidence':confidence}
        return context


    @swagger_auto_schema(operation_description='Upload file...',)
    # @action(detail=False, methods=['POST'])
    def create(self, request, *args, **kwargs):
        # image =  request.FILES['image']
        request.data['owner'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payload = {}
            predict = serializer.save()
            res = self.predictImage(predict.image)
            res['owner'] = predict.owner.id
            _serializer = PredictSerializer(predict, data=res)
            if _serializer.is_valid():
                _serializer.save()
            else:
                predict.delete()
                return Response(_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            disease = res.get('predictedLabel', 'NA')
            payload = {
                'filePathName': serializer.data.get('image', 'NA'),
                'predictedLabel': res.get('predictedLabel', 'NA'),
                'index': res.get('index', 'NA'),
                'about': self.disease_info(disease),
                'confidence': res.get('confidence', 'NA')
            }
            return Response(payload, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
