import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom manager where email is the unique identifier for authentication
    instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email address is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'OWNER')
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CUSTOMER = 'CUSTOMER'
    ROLE_ORDER_STAFF = 'ORDER_STAFF'
    ROLE_MANAGER = 'MANAGER'
    ROLE_OWNER = 'OWNER'

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_ORDER_STAFF, 'Order Staff'),
        (ROLE_MANAGER, 'Operations Manager'),
        (ROLE_OWNER, 'Business Owner'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    
    # Account status & Security
    is_email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email

    @property
    def is_owner(self):
        return self.role == self.ROLE_OWNER or self.is_superuser

    @property
    def is_manager_or_above(self):
        return self.role in [self.ROLE_OWNER, self.ROLE_MANAGER] or self.is_superuser

    @property
    def is_staff_member(self):
        return self.role in [self.ROLE_OWNER, self.ROLE_MANAGER, self.ROLE_ORDER_STAFF] or self.is_staff or self.is_superuser


class Address(models.Model):
    """
    Saved customer delivery addresses with strict ownership constraints.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    street_address = models.CharField(max_length=255)
    city_district = models.CharField(max_length=100, help_text="e.g. Kigali - Nyarugenge, Gasabo, Kicukiro, Rubavu, etc.")
    province = models.CharField(max_length=100, default="Kigali City")
    country = models.CharField(max_length=100, default="Rwanda")
    delivery_instructions = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Address'
        verbose_name_plural = 'Delivery Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city_district}, {self.country}"

    def save(self, *args, **kwargs):
        # If this address is set to default, ensure all other addresses for this customer are not default
        if self.is_default:
            Address.objects.filter(customer=self.customer).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
