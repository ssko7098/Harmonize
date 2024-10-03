from django.db import models
from users.models import User, Profile

# Create your models here.
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    report_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Comment by {self.user.username}'