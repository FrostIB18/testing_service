from django.contrib import admin
from django.urls import path, include

from testing.views import home, signup, login, logout

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('', home, name='home'),
    path('themes/', include('testing.urls', namespace='testing'))
]
