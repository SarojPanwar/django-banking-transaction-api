from rest_framework import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Account, Transaction
from .serializers import(
    RegisterSerializer,
    AccountSerializer,
    TransactionSerializer,
    DepositSerializer,
    WithdrawalSerializer,
    TransferSerializer,
   
)

# Create your views here.
# ---------------------------
# Register View
# ---------------------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create account for this user automatically
            Account.objects.create(user=user)
            # Create token for this user
            token = Token.objects.create(user=user)
        
            return Response({
                'message':'Registration successful',
                'token': token.key,
                'user':{
                    'id':user.id,
                    'username':user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# Login VIEW
# ---------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username,password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message':'Login successful',
                'token': token.key,
                'user':{
                    'id':user.id,
                    'username':user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)
        return Response({'error':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
# ---------------------------
# ACCOUNT  DETAIL VIEW 
# ---------------------------
class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            account = Account.objects.get(user=request.user)
            serializer = AccountSerializer(account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({
                'error':'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
# ---------------------------
# DEPOSTI VIEW
# ---------------------------
class CEpostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            description = serializer.validated_data.get('description','')
            try:
                with transaction.atomic():
                    account = Account.objects.select_for_update().get(user=request.user)

                    # Update balance 
                    account.balance += amount
                    account.save()

                    #create transaction record 
                    Transaction.objects.create(
                        account=account,
                        transaction_type='deposit',
                        amount=amount,
                        balance_after=account.balance,
                        description=description,
                        status='success'
                    )
                return Response({
                    'message':'Deposit successful',
                    'amount':str(amount),
                    'new_balance':str(account.balance) 
                }, status=status.HTTP_200_OK)
            except Account.DoesNotExist:
                return Response({
                    'error':'Account not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# WITHDRAWAL VIEW
# ---------------------------
class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = WithdrawalSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            description = serializer.validated_data.get('description','')
            try:
                with transaction.atomic():
                    account = Account.objects.select_for_update().get(user=request.user)
                    # Check sufficient balance
                    if account.balance < amount:
                        return Response({
                            'error':'Insufficient funds',
                            'current_balance':str(account.balance)
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Update balance 
                    account.balance -= amount
                    account.save()

                    #create transaction record 
                    Transaction.objects.create(
                        account=account,
                        transaction_type='withdrawal',
                        amount=amount,
                        balance_after=account.balance,
                        description=description,
                        status='success'
                    )
                return Response({
                    'message':'Withdrawal successful',
                    'amount':str(amount),
                    'new_balance':str(account.balance) 
                }, status=status.HTTP_200_OK)
            except Account.DoesNotExist:
                return Response({
                    'error':'Account not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# TRANSFER VIEW
# ---------------------------
class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = TransferSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data['amount'],
            target_account_number = serializer.validated_data['target_account_number'],
            description = serializer.validated_data.get('description','')

            try:
                with transaction.atomic():
                    # Get sender account
                    sender_account = Account.objects.select_for_update().get(user=request.user)

                    # Get receiver account
                    try:
                        receiver_account = Account.objects.select_for_update().get(account_number=target_account_number)
                    except Account.DoesNotExixt:
                        return Response({
                            'error':'Target ccount not found'
                        },status=status.HTTP_404_NOT_FOUND)
                    
                    # Can not tnansfer to own account
                    if sender_account==receiver_account:
                        return Response({
                            'error':'Cannot transfer to your own account'
                        },status=status.HTTP_400_BAD_REQUEST)
                    # Check sufficient balance
                    if sender_account.balance<amount:
                        return Response({
                            'error':'Insufficient balance',
                            'current_balance':str(sender_account.balance)
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Deduct from sender
                    sender_account.balance -= amount
                    sender_account.save()
                    # Add to receiver
                    receiver_account.balance+=amount
                    receiver_account.save()

                    # Create transaction records for sender
                    Transaction.objects.create(
                        account=sender_account,
                        transaction_type='transfer',
                        amount=amount,
                        balance_after=sender_account.balance,
                        description=f"Transfer to {receiver_account.account_number}.{description}",
                        status='success'
                    )
                    # Create transaction record for receiver
                    Transaction.objects.create(
                        account=receiver_account,
                        transaction_type='transfer',
                        amount=amount,
                        balance_after=receiver_account.balance,
                        description=f"Transfer from {sender_account.account_number}.{description}",
                        status='success'
                    )
                    return Response({
                        'message':'Transfer successful',
                        'amount':str(amount),
                        'new_balance':str(sender_account.balance)

                    },status = status.HTTP_200_OK)
            except Account.DoesNotExist:
                return Response({
                    'error':'Account not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# Transaction History View
# ---------------------------
class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            account = Account.objects.get(user=request.user)
            transactions = Transaction.objects.filter(account=account)

            # Manual filtering by type
            transaction_type = request.query_params.get('type',None)
            if transaction_type:
                transactions = transactions.filter(transaction_type=transaction_type)
                
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({
                'error':'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)