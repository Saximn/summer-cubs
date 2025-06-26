from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
import os

# Import the chatbot from the reusable_chatbot package
from chatbot.langgraph_chatbot import LangGraphChatbot

# Create your views here.

class ChatbotAPIView(APIView):
    permission_classes = [AllowAny]
    # Dynamically build the path to doctors.db
    db_path = os.path.join(settings.BASE_DIR, 'chatbot', 'doctors.db')
    chatbot = LangGraphChatbot(db_path=db_path)

    def post(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "No message provided"}, status=400)
        reply = self.chatbot.ask(user_message)
        return Response({"reply": reply})