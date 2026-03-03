from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    AccountDetailView,
    DepositView,
    WithdrawalView,
    TransferView,
    TransactionHistoryView,
    
)
urlpatterns =[
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('account/', AccountDetailView.as_view(), name='account-detail'),
    path('account/deposit/', DepositView.as_view(), name='deposit'),
    path('account/withdraw/', WithdrawalView.as_view(), name='withdraw'),
    path('account/transfer/', TransferView.as_view(), name='transfer'),
    path('account/transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    
] 