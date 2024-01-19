from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import update_status


app_name = 'pointqueapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('logout', views.logout_request, name='logout'),
    path('tech_que/', views.tech_que, name='tech_que'),
    path('set_dc/', views.set_dc, name='set_dc'),
    path('update_status/<int:piece_id>/', update_status, name='update_status'),
    path('data', views.data, name='data'),
    path('tv_display', views.tv_display, name='tv_display'),
    
    


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)