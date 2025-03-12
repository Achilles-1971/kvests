from django.db import models
import uuid

class Profile(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    avatar_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Указываем, что Django не управляет этой таблицей
        db_table = 'profiles'

class Quest(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quests'

class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField()
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'bookings'

class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField()
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'ratings'

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField()
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'comments'