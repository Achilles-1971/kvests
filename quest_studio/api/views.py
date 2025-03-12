from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client
from django.conf import settings
from django.core.mail import send_mail
import jwt
from .serializers import ProfileSerializer, QuestSerializer, BookingSerializer, RatingSerializer

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Профиль пользователя
class ProfileView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or "Bearer " not in auth_header:
            return Response({"error": "Authorization token missing or invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split("Bearer ")[-1]
        try:
            user = jwt.decode(token, options={"verify_signature": False})
            user_id = user["sub"]
        except jwt.DecodeError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = supabase.table("profiles").select("*").eq("user_id", user_id).execute().data
        if not profile:  # Если профиля нет, создаем пустой
            supabase.table("profiles").insert({"user_id": user_id, "nickname": "User", "avatar_url": ""}).execute()
            profile = supabase.table("profiles").select("*").eq("user_id", user_id).execute().data
        
        bookings = supabase.table("bookings").select("*, quests(*)").eq("user_id", user_id).execute().data
        
        profile_serializer = ProfileSerializer(profile, many=True)
        bookings_serializer = BookingSerializer(bookings, many=True)
        
        return Response({
            "profile": profile_serializer.data[0],
            "booked_quests": bookings_serializer.data
        })

# Список квестов
class QuestListView(APIView):
    def get(self, request):
        difficulty = request.query_params.get("difficulty")
        if difficulty:
            quests = supabase.table("quests").select("*").eq("difficulty", difficulty).execute().data
        else:
            quests = supabase.table("quests").select("*").execute().data
        
        serializer = QuestSerializer(quests, many=True)
        return Response(serializer.data)

# Запись на квест
class BookQuestView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or "Bearer " not in auth_header:
            return Response({"error": "Authorization token missing or invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split("Bearer ")[-1]
        try:
            user = jwt.decode(token, options={"verify_signature": False})
            user_id = user["sub"]
        except jwt.DecodeError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        quest_id = request.data.get("quest_id")
        if not quest_id:
            return Response({"error": "quest_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        booking = supabase.table("bookings").insert({"user_id": user_id, "quest_id": quest_id}).execute().data[0]
        quest = supabase.table("quests").select("*").eq("id", quest_id).execute().data[0]

        # Отправка email
        user_email = supabase.auth.get_user(token).user.email
        subject = "Успешная запись на квест"
        message = f"Вы записаны на квест: {quest['title']}\nДата: {quest['date']}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

        serializer = BookingSerializer(booking)
        return Response({"message": "Booked successfully", "booking": serializer.data})

# Добавление рейтинга
class RateQuestView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or "Bearer " not in auth_header:
            return Response({"error": "Authorization token missing or invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split("Bearer ")[-1]
        try:
            user = jwt.decode(token, options={"verify_signature": False})
            user_id = user["sub"]
        except jwt.DecodeError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        quest_id = request.data.get("quest_id")
        rating = request.data.get("rating")
        if not quest_id or not rating:
            return Response({"error": "quest_id and rating are required"}, status=status.HTTP_400_BAD_REQUEST)

        rating_data = supabase.table("ratings").insert({"user_id": user_id, "quest_id": quest_id, "rating": rating}).execute().data[0]
        serializer = RatingSerializer(rating_data)
        return Response({"message": "Rating added", "rating": serializer.data})