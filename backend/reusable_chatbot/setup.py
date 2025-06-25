from setuptools import setup, find_packages

setup(
    name="reusable_chatbot",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "Django>=4.0",
        "djangorestframework",
        "openai",
    ],
    entry_points={
        "django.apps": ["chatbot = chatbot.apps.ChatbotConfig"]
    },
)