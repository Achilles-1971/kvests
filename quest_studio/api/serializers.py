from rest_framework import serializers
from .models import Profile, Quest, Booking, Rating, Comment

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_id', 'nickname', 'avatar_url']

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ['id', 'title', 'description', 'date', 'difficulty']

class BookingSerializer(serializers.ModelSerializer):
    quest = QuestSerializer()  # Вложенный сериализатор для квеста

    class Meta:
        model = Booking
        fields = ['id', 'user_id', 'quest', 'created_at']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user_id', 'quest', 'rating', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'quest', 'text', 'created_at']