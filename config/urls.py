"""
URL configuration for Knowledge Map project.
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Knowledge Map</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Segoe UI', system-ui, sans-serif; }
        </style>
    </head>
    <body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
            <div class="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span class="text-white text-3xl font-bold">KM</span>
            </div>
            <h1 class="text-3xl font-bold text-gray-800 mb-2">Knowledge Map</h1>
            <p class="text-gray-600 mb-6">Карта ваших знаний и достижений</p>
            
            <div class="space-y-3 mb-8">
                <div class="flex items-center text-green-600">
                    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    <span>Django успешно работает</span>
                </div>
                <div class="flex items-center text-blue-600">
                    <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    <span>База данных настроена</span>
                </div>
            </div>
            
            <div class="space-y-4">
                <a href="/admin/" class="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition shadow-md">
                    Перейти в админ-панель
                </a>
                <p class="text-sm text-gray-500">
                    Используйте созданные учетные данные для входа
                </p>
            </div>
            
            <div class="mt-8 pt-6 border-t border-gray-200">
                <p class="text-xs text-gray-500">
                    Knowledge Map v1.0 • Django 5.0
                </p>
            </div>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]
