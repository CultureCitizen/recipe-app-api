from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        else:
            # raises ValidationError
            validate_email(email)

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username """
    email = models.EmailField(max_length=250, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

# ------------------------------------------------------------
# We define the Tag object as a name and a User
# the  tag is part of the user, so if the user is deleted, all its tags will be deleted
# we also define the string representation of the tag, wich contains only the name
# ------------------------------------------------------------


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
