# from django.urls import path
# from django.conf import settings
# from django.conf.urls.static import static
# from . import views


# urlpatterns = [
#     path('', views.homepage, name='homepage'),
#     path('buy-property/', views.browse_properties, name='browse_properties'),
#     path('buy-now/<int:property_id>/', views.buy_now_handler, name='buy_now_handler'),
#     # Auth
#     path('auth/<int:property_id>/', views.auth_page, name='auth_page'),
#     path('property-form/<int:property_id>/', views.property_form, name='property_form'),
#     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('property/<int:property_id>/', views.property_detail, name='property_details'),
#     path('logout/', views.logout_view, name='logout'),
#     path('login/', views.login_page, name='login'), # Changed from 'login_page'
#     path('signup/', views.signup_page, name='signup'), # Changed from 'signup_page'
#     path('login-action/', views.login_view, name='login_action'),
#     path('signup-action/', views.signup_view, name='signup_action'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('buy-property/', views.browse_properties, name='browse_properties'),
    path('buy-now/<int:property_id>/', views.buy_now_handler, name='buy_now_handler'),
    
    # Auth Pages
    path('auth/', views.auth_unified, name='auth_unified'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('signup/continue/', views.signup_continue_page, name='signup_continue'),
    path('signup/create-password/', views.signup_create_password_page, name='signup_create_password'),
    path('mortgage-calculator/', views.mortgage_calculator, name='mortgage_calculator'),
    path('calculate-mortgage/', views.calculate_mortgage, name='calculate_mortgage'),
    # Firebase Authentication Endpoints
    path('api/firebase-signup/', views.firebase_signup, name='firebase_signup'),
    path('api/firebase-login/', views.firebase_login, name='firebase_login'),
    path('forgot-password/', views.forgot_password_page, name='forgot_password'),
    path('api/send-reset-otp/', views.send_reset_otp, name='send_reset_otp'),
    path('api/verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('api/reset-password/', views.reset_password, name='reset_password'),
    
    # Legacy endpoints (for backward compatibility)
    path('login-action/', views.login_view, name='login_action'),
    path('signup-action/', views.signup_view, name='signup_action'),
    
    # Property and User Management
    path('property-form/<int:property_id>/', views.property_form, name='property_form'),
    path('property/<int:property_id>/', views.property_detail, name='property_details'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)