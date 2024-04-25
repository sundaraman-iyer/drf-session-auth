#serializer is used to create Users

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email','password']
        extra_kwargs = {
            'password' : {'write_only': True} # this makes sure the password is not returned in the API response
        }
    

    # hashing the password #sits between the view and model creation
    def create(self, validated_data):
        password = validated_data.pop('password', None) #extracting the data from serializer
        instance = self.Meta.model(**validated_data) # creating the user for the validated_data
        if password is not None:
            instance.set_password(password) #hashing
        instance.save()
        return instance
