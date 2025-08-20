from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff") or not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Stock(models.Model):
    EXCHANGE_CHOICES = [
        ('NSE', 'NSE'),
        ('BSE', 'BSE'),
    ]

    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=3, choices=EXCHANGE_CHOICES, default='NSE')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.name} ({self.exchange})"

    @property
    def last_price(self):
        # Get the latest transaction price for this stock
        last_txn = self.transactions.order_by('-date').first()
        return last_txn.price if last_txn else self.current_price or 0


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    brokerage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sebi_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stamp_duty = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.stock.symbol}"

    @property
    def total_charges(self):
        return round(self.brokerage + self.stt + self.gst + self.sebi_charges + self.stamp_duty, 2)


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='portfolios')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_display = self.user.email if self.user else "No User"
        return f"{user_display} - {self.stock.symbol}"



class CapitalGains(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    realized_gain = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    short_term_gain = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    long_term_gain = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_liability = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='watchlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{getattr(self.user, 'email', 'Unknown')} - {self.stock.symbol}"

    
  
