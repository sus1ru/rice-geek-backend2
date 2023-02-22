from rest_framework import serializers
from core.models import UserProfile
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model, authenticate


#Using serializer.ModelSerializer
class EmployeeSerializer(serializers.ModelSerializer):
    # len_name = serializers.SerializerMethodField()

    # Serializer Relations: All Details
    # project = ProjectSerializer(many=True, read_only=True)
    
    # # Serializer Relations: StringRelatedField
    # project = serializers.StringRelatedField(many=True)

    # Serializer Relations: SlugRelatedField
    # project = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name'
    # )
    is_active = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True, },
        }

    def get_is_active(self, obj):
        status = obj.user.is_active
        return status

    def get_username(self, obj):
        username = obj.user.username
        return username


class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password',]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
        }
    
        # super().save()

    def save(self):
        username = self.validated_data.get('username')
        password = self.validated_data.get('password')
        email = self.validated_data.get('email')
        
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError({'Error': 'Email already registered!'})

        account = get_user_model()(email=email, password=password, username=username,)
        account.set_password(password)
        account.save()
        return account


# class EmployeeRegistrationSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Employee
#         fields = '__all__'
    
    # def create(self, validated_data):
    #     user_data = validated_data.pop('user')
    #     # password = user_data.get('password')
    #     # password2 = user_data.get('password2')
    #     # email = user_data.get('email')

    #     # if password != password2:
    #     #     raise serializers.ValidationError({'Error': 'Passwords dont match!'})
        
    #     # if get_user_model().objects.filter(email=email).exists():
    #     #     raise serializers.ValidationError({'Error': 'Email already registered!'})

    #     tmp_user = get_user_model().objects.create(**user_data)
    #     employee = Employee.objects.create(**validated_data, user=tmp_user)
    #     return employee


class AuthCustomTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        return attrs
