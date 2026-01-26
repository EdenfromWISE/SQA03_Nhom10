from django.urls import path
from .views import ChatbotApiEndpoint, ChatbotHistoryView


urlpatterns = [
    path("chat/", ChatbotApiEndpoint.as_view(), name="chatbot_chat"),
    path("history/", ChatbotHistoryView.as_view(), name="chatbot_history"),
]


