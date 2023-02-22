from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from user.api.serializers import (
    # EmployeeRegistrationSerializer,
    UserRegSerializer,
    AuthCustomTokenSerializer,
)


@api_view(['POST'],)
def logout_view(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'],)
def login_view(request):
    serializer = AuthCustomTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token, created = Token.objects.get_or_create(user=user)

    user_info = {
        'username': user.username,
        'email': user.email,
        'token': token.key,
    }

    return Response(user_info, status=status.HTTP_201_CREATED)



@api_view(['POST'],)
def registration_view(request):
    if request.method == 'POST':
        # dept_id = request.data.pop('dept')
        user_serializer = UserRegSerializer(data=request.data)
        user_info = {}

        if user_serializer.is_valid():
            acc = user_serializer.save()
            user_info['response'] = "User registered successfully!"
            user_info['username'] = acc.username
            user_info['email'] = acc.email

            # # Auto-generating token while registration
            # token = Token.objects.get(user=acc).key
            # user_info['token'] = token

            # employee_serializer = EmployeeRegistrationSerializer(
            #     data={
            #         'dept': dept_id,
            #         'user': acc.id,
            #     }
            # )

            # if employee_serializer.is_valid():
            #     employee_serializer.save()
            #     user_info['response'] = "Employee registered successfully!"
            #     user_info['employee'] = employee_serializer.data
            #     return Response(
            #         user_info,
            #         status=status.HTTP_201_CREATED,
            #     )
            # else:
            #     get_user_model().objects.get(pk=acc.id).delete()
            #     user_info = {'Error': 'Invalid department id, registration failed!'}
        else:
            user_info = user_serializer.errors

        return Response(user_info, status=status.HTTP_400_BAD_REQUEST)
