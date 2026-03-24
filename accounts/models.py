from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with role support."""

    ADMIN = 'admin'
    SALESPERSON = 'salesperson'
    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (SALESPERSON, 'Vendedor'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=SALESPERSON,
        verbose_name='Rol',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def is_admin(self):
        return self.role == self.ADMIN

    def is_salesperson(self):
        return self.role == self.SALESPERSON

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
