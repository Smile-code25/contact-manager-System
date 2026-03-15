from django.db import models


class AppUser(models.Model):
    """
    Custom user model (not Django's auth system) — matches the original
    Flask project which stores username + plain password in a `users` table.
    """
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Contact(models.Model):
    """
    Contact record — belongs to a user.
    Original project used per-user tables (contacts_<username>).
    In Django we use a single table with a ForeignKey, which is cleaner
    and equivalent in functionality.
    """
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contacts'
        ordering = ['-date_added']
        # Unique phone/email per user (equivalent to original unique constraints)
        constraints = [
            models.UniqueConstraint(fields=['user', 'phone'], name='unique_user_phone'),
            models.UniqueConstraint(fields=['user', 'email'], name='unique_user_email'),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email or '',
            'date_added': self.date_added.strftime('%Y-%m-%d %H:%M:%S'),
        }
