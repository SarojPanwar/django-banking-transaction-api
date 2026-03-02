from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Account(models.Model):

    ACCOUNT_TYPE =[
        ('savings', 'Savings'),
        ('current', 'Current'),
    ]

    user =models.OneToOneField(User, on_delete=models.CASCADE,related_name='account')
    account_number = models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    account_type = models.CharField(max_length=10,choices=ACCOUNT_TYPE,default='savings')
    balance = models.DecimalField(max_digits=12, decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES =[
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    STATUS_CHOICES =[
        ('succes', 'Success'),
        ('failed', 'Failed'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12,decimal_places=2)
    description = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='success')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.account.user.username}" 
    
    class Meta:
        ordering =['-timestamp']
    
