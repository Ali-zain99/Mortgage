from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('buy-property/', views.browse_properties, name='browse_properties'),
    path('buy-now/<int:property_id>/', views.buy_now_handler, name='buy_now_handler'),
    # Auth
    path('auth/<int:property_id>/', views.auth_page, name='auth_page'),
    path('property-form/<int:property_id>/', views.property_form, name='property_form'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('property/<int:property_id>/', views.property_detail, name='property_details'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_page, name='login'), # Changed from 'login_page'
    path('signup/', views.signup_page, name='signup'), # Changed from 'signup_page'
    path('login-action/', views.login_view, name='login_action'),
    path('signup-action/', views.signup_view, name='signup_action'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 