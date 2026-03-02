from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account,Transaction
from decimal import Decimal

#User Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username','email','password','password2']

    def validate(self,data):
        if data['password']!= data['password2']:
            raise serializers.ValidationError("Password do not match")
        return data
    
    def create(self,validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  
        )
        return user
    
# User detail Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

# Account Serializer
class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Account
        fields=[
            'id',
            'user',
            'account_number',
            'balance',
            'is_active',
            'created_at',
        ]
        read_only_fields=['account_number','balance','created_at']

# Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Transaction
        fields=[
            'id',
            'account',
            'transaction_type',
            'amount',
            'balance_after',
            'description',
            'status',
            'timestamp'

        ]
        read_only_fields= ['balance_after','status','timestamp']

# Deposit Serializer
class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description=serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value
    
# Withdrawal Serializer
class WithdrawalSerializer(serializers.Serializer):
    amount =serializers.DecimalField(max_digits=12,decimal_places=2)
    description= serializers.CharField(required=False,allow_blank=True)

    def validate_amount(self,value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Withdrawal amount must be greater than zero.")
        return value
    
    
# Transfer Serializer
class TransferSerializer(serializers.Serializer):
    amount =serializers.DecimalField(max_digits=12, decimal_places=2)
    target_account_number = serializers.UUIDField()
    description = serializers.CharField(required=False,allow_blank=True)

    def validate_amount(self,value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Transfer amount must be greater than zero.")
        return value





