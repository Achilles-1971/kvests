from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
import uuid

from .models import Profile, Quest, Booking, Rating, Comment
from .serializers import (
    ProfileSerializer,
    QuestSerializer,
    BookingSerializer,
    RatingSerializer,
    CommentSerializer
)


def get_user_id_from_request(request):

    auth_header = request.headers.get("Authorization", "")
    if not auth_header or "Bearer " not in auth_header:
        return None, Response(
            {"error": "Authorization token missing or invalid"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token = auth_header.split("Bearer ")[-1]
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        # Предполагаем, что в токене есть поле "sub" = user_id (UUID)
        user_id_str = decoded.get("sub")
        if not user_id_str:
            return None, Response(
                {"error": "'sub' not found in token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # Преобразуем строку в UUID (на случай, если нужно проверить формат)
        user_id = uuid.UUID(user_id_str)
        return user_id, None
    except (jwt.DecodeError, ValueError):
        return None, Response(
            {"error": "Invalid token or cannot parse user_id as UUID"},
            status=status.HTTP_401_UNAUTHORIZED
        )


class ProfileView(APIView):

    def get(self, request):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        # Находим или создаём профиль
        profile, created = Profile.objects.get_or_create(
            user_id=user_id,
            defaults={"nickname": "User", "avatar_url": ""}
        )

        bookings = Booking.objects.filter(user_id=user_id).select_related("quest")

        # Сериализуем
        profile_serializer = ProfileSerializer(profile)
        bookings_serializer = BookingSerializer(bookings, many=True)

        return Response({
            "profile": profile_serializer.data,
            "booked_quests": bookings_serializer.data
        })


class QuestListView(APIView):

    def get(self, request):
        difficulty = request.query_params.get("difficulty")
        if difficulty:
            quests = Quest.objects.filter(difficulty=difficulty)
        else:
            quests = Quest.objects.all()

        serializer = QuestSerializer(quests, many=True)
        return Response(serializer.data)


class BookQuestView(APIView):
    def post(self, request):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        quest_id = request.data.get("quest_id")
        if not quest_id:
            return Response({"error": "quest_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем квест (404, если не найден)
        quest = get_object_or_404(Quest, pk=quest_id)

        # Проверка, не забронировал ли уже
        if Booking.objects.filter(user_id=user_id, quest=quest).exists():
            return Response({"error": "You have already booked this quest."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Создаём новое бронирование
        booking = Booking.objects.create(user_id=user_id, quest=quest)

        user_profile = Profile.objects.filter(user_id=user_id).first()
        user_email = None
        if user_profile and hasattr(user_profile, 'email'):
            user_email = user_profile.email  # Если бы было поле .email
        # На учебном уровне можно просто пропустить
        if user_email:
            subject = "Успешная запись на квест"
            message = f"Вы записаны на квест: {quest.title}\nДата: {quest.date}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

        booking_serializer = BookingSerializer(booking)
        return Response({
            "message": "Booked successfully",
            "booking": booking_serializer.data
        })


class RateQuestView(APIView):
    def post(self, request):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        quest_id = request.data.get("quest_id")
        rating_value = request.data.get("rating")
        if not quest_id or not rating_value:
            return Response({"error": "quest_id and rating are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Проверяем корректность рейтинга
        try:
            rating_int = int(rating_value)
            if rating_int < 1 or rating_int > 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем квест
        quest = get_object_or_404(Quest, pk=quest_id)

        # Обновляем или создаём
        # (unique_together обеспечивает, что user_id+quest уникальны)
        rating_obj, created = Rating.objects.update_or_create(
            user_id=user_id,
            quest=quest,
            defaults={"rating": rating_int}
        )

        serializer = RatingSerializer(rating_obj)
        return Response({
            "message": "Rating created" if created else "Rating updated",
            "rating": serializer.data
        })


class CommentView(APIView):
    def get(self, request):
        quest_id = request.query_params.get("quest_id")
        if not quest_id:
            return Response({"error": "quest_id is required for GET"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        quest = get_object_or_404(Quest, pk=quest_id)

        comments = Comment.objects.filter(quest=quest).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        quest_id = request.data.get("quest_id")
        text = request.data.get("text")
        if not quest_id or not text:
            return Response({"error": "quest_id and text are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        quest = get_object_or_404(Quest, pk=quest_id)

        comment = Comment.objects.create(
            user_id=user_id,
            quest=quest,
            text=text
        )

        serializer = CommentSerializer(comment)
        return Response({
            "message": "Comment added",
            "comment": serializer.data
        }, status=status.HTTP_201_CREATED)
