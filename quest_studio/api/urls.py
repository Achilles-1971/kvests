from django.urls import path
from .views import (
    ProfileView,
    QuestListView,
    BookQuestView,
    RateQuestView,
    CommentView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('quests/', QuestListView.as_view(), name='quest_list'),
    path('book/', BookQuestView.as_view(), name='book_quest'),
    path('rate/', RateQuestView.as_view(), name='rate_quest'),
    path('comments/', CommentView.as_view(), name='comments'),
]
