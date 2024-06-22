from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @classmethod
    def register(cls, name: str, email: str, password: str):
        user = cls(is_active=True)
        user.set_name(name)
        user.set_email(email)
        user.set_password(password)
        user.save()

        return user
    
    @classmethod
    def authenticate(cls, email: str, password: str):
        user = cls.objects.filter(email=email.lower()).first()
        if user is None or user.is_active is False or user.check_password(password) is False:
            raise Exception('User not found')
        return user

    def set_name(self, value: str):
        names = value.split(' ')
        first_name = names[0]
        last_name = ''
        if len(names) > 1:
            last_name = ' '.join(name for name in names[1:])
        self.first_name = first_name
        self.last_name = last_name
    
    def set_email(self, value: str):
        self.email = value.lower()
        self.username = self.email

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()
