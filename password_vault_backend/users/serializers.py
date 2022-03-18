from multiprocessing import context
import re
import random

from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import serializers

from users.models import Verification


class SignUpSerializer(serializers.Serializer):
    """
    Serializer for signup body

    @author: Deep Adeshra <dp974154@dal.ca>
    """

    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        """
        This method validates entire JSON body.
        """

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "This should be same as password"
            })

        return data

    def validate_name(self, value):
        """
        validates name of user. Name should be alpha-numaric only.
        """

        regex = "\b([A-ZÀ-ÿ][-,a-z. ']+[ ]*)+"

        if re.fullmatch(re.compile(regex), value):
            raise serializers.ValidationError("Please enter only alpha "
                                              "numerical names")

        return value

    def validate_first_name(self, value):
        return self.validate_name(value)

    def validate_last_name(self, value):
        return self.validate_name(value)

    def validate_email(self, email):
        """
        validates if there is any existing account with the passed email or not.
        """

        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            raise serializers.ValidationError("Account with this email "
                                              "already exists")

        return email

    @transaction.atomic()
    def create(self, validated_data):
        """
        Creates the User instance based on passed data.
        """

        # TODO: by default create the users inactive and send the email to
        #  verify them

        user = User()
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.username = validated_data['email']
        user.email = validated_data['email']
        user.set_password(validated_data['password'])
        # user.is_active = False
        user.save()
        token = Token.objects.create(user=user)

        return token


class LoginSerializer(serializers.Serializer):
    """
    Serializer for signin body

    @author: Pooja Anandani <pooja.anandani@dal.ca>
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User,
        fields = ('email', 'password')
        read_only_fields = ['token']

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({
                "email": "this account does not exists"
            })

        is_valid = user.check_password(password)

        if not is_valid:
            raise serializers.ValidationError({
                "password": "Please check your password."
            })

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for Forgot Password

    @author: Pooja Anandani <pooja.anandani@dal.ca>
    """

    email = serializers.EmailField()

    def validate_email(self, email):
        """
        validates if there is any existing account with the passed email or not.
        """

        user = User.objects.filter(email=email).last()

        if user:
            one_time_verification = random.randint(0, 999999)
            data = Verification(user=user, verification_code=one_time_verification)
            data.save()
        else:
            raise serializers.ValidationError("Account with this email "
                                              "does not exists")

        return email


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for Resetting the password

    @author: Pooja Anandani <pooja.anandani@dal.ca>
    """

    email = serializers.EmailField()
    otp = serializers.IntegerField()
    password = serializers.CharField()

    def validate(self, data):
        """
        validates if there is any existing account with the passed email or not.
        """

        try:
            user_otp = Verification.objects.filter(user__email=data.get('email'))\
                .order_by('-created_at').first()

            if user_otp.verification_code == data.get('otp'):
                user = User.objects.get(email=data.get('email'))
                user.set_password(data.get('password'))
                user.save()
                user_otp.delete()
            else:
                raise serializers.ValidationError({"otp": "No record found"})
        except:
            raise serializers.ValidationError({"otp": "No record found"})

        return data