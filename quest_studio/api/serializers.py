from rest_framework import serializers
from .models import Profile, Quest, Booking, Rating, Comment

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        # Если нужны все поля, можно так:
        fields = '__all__'
        # Или перечислить вручную, чтобы точно контролировать порядок/наличие:
        # fields = ['user_id', 'nickname', 'avatar_url', 'created_at', 'updated_at']


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = '__all__'
        # fields = ['id', 'title', 'description', 'date', 'difficulty', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    # Показываем информацию о квесте
    quest = QuestSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user_id', 'quest', 'created_at']
        # Или можно '__all__', но тогда будут и служебные поля:
        # fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    # Если нужно показывать сам квест в ответе, можно раскомментировать:
    # quest = QuestSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user_id', 'quest', 'rating', 'created_at']
        # fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    # Аналогично, если хотим видеть данные квеста:
    # quest = QuestSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'quest', 'text', 'created_at']
        # fields = '__all__'
