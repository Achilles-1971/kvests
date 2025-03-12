from rest_framework.views import APIView
from rest_framework.response import Response
from supabase import create_client
from django.conf import settings
from django.core.mail import send_mail
import jwt
from .serializers import ProfileSerializer, QuestSerializer, BookingSerializer, RatingSerializer

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Профиль пользователя
class ProfileView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization", "").split("Bearer ")[-1]
        user = jwt.decode(auth_header, options={"verify_signature": False})
        user_id = user["sub"]

        profile = supabase.table("profiles").select("*").eq("user_id", user_id).execute().data
        if not profile:  # Если профиля нет, создаем пустой
            supabase.table("profiles").insert({"user_id": user_id, "nickname": "User", "avatar_url": ""}).execute()
            profile = supabase.table("profiles").select("*").eq("user_id", user_id).execute().data
        
        bookings = supabase.table("bookings").select("*, quests(*)").eq("user_id", user_id).execute().data
        
        profile_serializer = ProfileSerializer(profile, many=True)
        bookings_serializer = BookingSerializer(bookings, many=True)
        
        return Response({
            "profile": profile_serializer.data[0],  # Берем первый элемент, так как user_id уникален
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
        auth_header = request.headers.get("Authorization", "").split("Bearer ")[-1]
        user = jwt.decode(auth_header, options={"verify_signature": False})
        user_id = user["sub"]
        quest_id = request.data.get("quest_id")

        booking = supabase.table("bookings").insert({"user_id": user_id, "quest_id": quest_id}).execute().data[0]
        quest = supabase.table("quests").select("*").eq("id", quest_id).execute().data[0]

        # Отправка email
        user_email = supabase.auth.get_user(auth_header).user.email
        subject = "Успешная запись на квест"
        message = f"Вы записаны на квест: {quest['title']}\nДата: {quest['date']}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

        serializer = BookingSerializer(booking)
        return Response({"message": "Booked successfully", "booking": serializer.data})

# Добавление рейтинга
class RateQuestView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization", "").split("Bearer ")[-1]
        user = jwt.decode(auth_header, options={"verify_signature": False})
        user_id = user["sub"]
        quest_id = request.data.get("quest_id")
        rating = request.data.get("rating")

        rating_data = supabase.table("ratings").insert({"user_id": user_id, "quest_id": quest_id, "rating": rating}).execute().data[0]
        serializer = RatingSerializer(rating_data)
        return Response({"message": "Rating added", "rating": serializer.data})