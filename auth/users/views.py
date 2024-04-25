from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response # for returning the response of the request
from .models import User
import jwt, datetime


# Create your views here.

#class to create a user using the serializer and the data from request 
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first() #ORM query

        if user is None:
            raise AuthenticationFailed('User not Found') #checking for user email present in register table
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Passeword')
        
        # creating JWT token payload

        payload = {
            'id':user.id,
            'exp': datetime.datetime.now() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.now()   
            }
        

        #creating the token using payload
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        # after request from user, the response is below
        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt':token
        }

        return response
    
class UserView(APIView): # raise ImmatureSignatureError("The token is not yet valid (iat)")    
    def get(self, request):
        token = request.COOKIES.get('jwt')
        
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        
        user = User.objects.filter(id=payload['id']).first()
        seraializer = UserSerializer(user) #since we want to return the data in json and before this is a query set

        return Response(seraializer.data)
    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message':'success'
        }
        return response