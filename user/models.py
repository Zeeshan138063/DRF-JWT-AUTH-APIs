# Create your models here.

# from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, first_name, last_name, username):
        '''
        Creates and saves a User with the given email and password.
        :param email:
        :param password:
        :param extra_fields:
        :return:
        '''
        if not email:
            raise ValueError('User may have an email')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, first_name=first_name,
                          last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name, username):
        return self._create_user(email, password, first_name, last_name, username)

    def create_superuser(self, email, password, first_name, last_name, username):
        user = self._create_user(email, password, first_name, last_name, username)
        user.is_admin = True
        user.save()
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=255)
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=5, null=True, blank=True)
    photo = models.ImageField(upload_to='profile-logo/%Y/%m/%d',
                              blank=True,
                              null=True
                              )

    objects = UserManager()
    # USERNAME_FIELD = 'username'
    '''
    The name of the field on the User model that is used as the unique identifier.
    The field must be unique (i.e., have unique=True set in its definition);
    '''
    USERNAME_FIELD = 'email'
    '''
    A list of the field names that will be prompted for when 
    creating a user via the createsuperuser management command
    '''
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        '''
        :return:Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
        # return self.first_name + " " + self.last_name

    def get_short_name(self):
        '''
        :return:Returns the short name for the user.
        '''
        return self.first_name

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
