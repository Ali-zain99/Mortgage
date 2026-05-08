from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import UserProfile
from .models import Property
from django.shortcuts import get_object_or_404
import json
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone
import json
from .models import PasswordResetOTP
from firebase_admin import auth as firebase_auth

def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))
 
 
def forgot_password_page(request):
    """Render forgot password page"""
    return render(request, 'home/forgot_password.html')
 
 
@csrf_exempt
def send_reset_otp(request):
    """
    Send OTP to user's email for password reset
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
            
            # Check if user exists in Django database
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'error': 'No account found with this email address'
                }, status=404)
            
            # Generate OTP
            otp = generate_otp()
            
            # Delete any existing OTPs for this email
            PasswordResetOTP.objects.filter(email=email).delete()
            
            # Create new OTP entry
            otp_entry = PasswordResetOTP.objects.create(
                email=email,
                otp=otp
            )
            
            # Send OTP via email
            try:
                subject = 'Password Reset OTP - Alfa Mortgage'
                message = f'''
Hello,
 
You have requested to reset your password for your Alfa Mortgage account.
 
Your OTP code is: {otp}
 
⚠️ This code will expire in 60 seconds.
 
If you did not request this password reset, please ignore this email.
 
Best regards,
Alfa Mortgage Team
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,  # From email
                    [email],  # To email
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'OTP sent to {email}. Please check your inbox.'
                })
                
            except Exception as email_error:
                # Log the error but don't expose it to the user
                print(f"Email sending error: {email_error}")
                return JsonResponse({
                    'error': 'Failed to send email. Please try again later.'
                }, status=500)
                
        except Exception as e:
            print(f"Send OTP error: {e}")
            return JsonResponse({
                'error': 'An error occurred. Please try again.'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
 
 
@csrf_exempt
def verify_reset_otp(request):
    """
    Verify the OTP entered by user
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            otp = data.get('otp', '').strip()
            
            if not email or not otp:
                return JsonResponse({
                    'error': 'Email and OTP are required'
                }, status=400)
            
            # Find the most recent OTP for this email
            try:
                otp_entry = PasswordResetOTP.objects.filter(
                    email=email,
                    is_verified=False
                ).latest('created_at')
            except PasswordResetOTP.DoesNotExist:
                return JsonResponse({
                    'error': 'No OTP found. Please request a new one.'
                }, status=404)
            
            # Check if OTP has expired
            if otp_entry.is_expired():
                # Delete expired OTP
                otp_entry.delete()
                return JsonResponse({
                    'error': 'OTP has expired. Please request a new one.'
                }, status=400)
            
            # Verify OTP
            if otp_entry.otp != otp:
                return JsonResponse({
                    'error': 'Invalid OTP. Please try again.'
                }, status=400)
            
            # Mark OTP as verified
            otp_entry.is_verified = True
            otp_entry.save()
            
            return JsonResponse({
                'success': True,
                'message': 'OTP verified successfully'
            })
            
        except Exception as e:
            print(f"Verify OTP error: {e}")
            return JsonResponse({
                'error': 'Verification failed. Please try again.'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
 
@csrf_exempt
def reset_password(request):
    """
    Reset user password after OTP verification
    Updates both Django and Firebase passwords
    Password is IMMEDIATELY and PERMANENTLY saved to database
    No time limit on password entry after OTP verification
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            new_password = data.get('new_password', '')
            
            if not email or not new_password:
                return JsonResponse({
                    'error': 'Email and new password are required'
                }, status=400)
            
            if len(new_password) < 6:
                return JsonResponse({
                    'error': 'Password must be at least 6 characters'
                }, status=400)
            
            # Check if OTP was verified (no time limit after verification)
            try:
                otp_entry = PasswordResetOTP.objects.filter(
                    email=email,
                    is_verified=True
                ).latest('created_at')
            except PasswordResetOTP.DoesNotExist:
                return JsonResponse({
                    'error': 'OTP not verified. Please verify OTP first.'
                }, status=403)
            
            # Get Django user
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'error': 'User not found'
                }, status=404)
            
            # IMMEDIATELY save new password to Django database
            user.set_password(new_password)
            user.save()
            
            print(f"✅ Password saved to Django database for user: {email}")
            
            # Update Firebase password (if Firebase is being used)
            try:
                from firebase_admin import auth as firebase_auth
                
                # Get Firebase user by email
                firebase_user = firebase_auth.get_user_by_email(email)
                
                # Update Firebase password
                firebase_auth.update_user(
                    firebase_user.uid,
                    password=new_password
                )
                print(f"✅ Password updated in Firebase for user: {email}")
            except ImportError:
                print("⚠️ Firebase not configured, skipping Firebase password update")
            except Exception as firebase_error:
                print(f"⚠️ Firebase password update error: {firebase_error}")
                # Continue - Django password is already saved
            
            # Clean up: Delete OTP entry after successful password reset
            otp_entry.delete()
            print(f"✅ OTP cleaned up for user: {email}")
            
            return JsonResponse({
                'success': True,
                'message': 'Password reset successfully! You can now login with your new password.'
            })
            
        except Exception as e:
            print(f"❌ Reset password error: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': 'Password reset failed. Please try again.'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
  
# Create your views here.
def homepage(request):
    return render(request, 'home/index.html')
def buy_now_handler(request, property_id): 
    """
    Traffic controller for the Buy Now button.
    """
    if request.user.is_authenticated:
        # User is logged in, go straight to the form
        return redirect('property_form', property_id=property_id)
    else:
        # User is a guest, save the property ID in session
        request.session['property_id'] = property_id
        
        # IMPORTANT: Match this name exactly to your urls.py name=''
        return redirect('auth_unified')
def auth_unified(request):
    """
    Unified authentication page with both login and signup forms
    Login is shown by default
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to homepage or property form if pending
        property_id = request.session.get('property_id')
        if property_id:
            return redirect('property_form', property_id=property_id)
        return redirect('homepage')
    
    return render(request, 'home/auth_unified.html')

def mortgage_calculator(request):
    """Display the mortgage calculator page"""
    return render(request, 'home/mortgage_calculator.html')

def calculate_mortgage(request):
    if request.method == 'POST':
        segment = request.POST.get('segment')
        property_value = float(request.POST.get('property_value', 0))
        dob = request.POST.get('dob')
        monthly_income = float(request.POST.get('monthly_income', 0))
        expenses = float(request.POST.get('expenses', 0))
        
        # Calculate age
        birth_date = datetime.strptime(dob, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

        # 🚫 Age restriction
        if age < 21:
            return render(request, 'home/mortgage_calculator.html', {
                'error': 'You must be at least 21 years old to apply for a mortgage.',
                'show_results': False
            })

        # Continue if eligible
        tenure_years = 60 - age
        net_salary = monthly_income - expenses
        
        # EMI Calculation
        annual_rate = 13
        monthly_rate = (annual_rate / 100) / 12
        total_months = tenure_years * 12
        
        if total_months > 0 and property_value > 0:
            emi = (
        property_value * monthly_rate
    ) / (
        1 - pow((1 + monthly_rate), -total_months)
    )
        else:
            emi = 0
        
        context = {
            'segment': segment,
            'property_value': property_value,
            'age': age,
            'tenure': tenure_years,
            'net_salary': net_salary,
            'emi': round(emi, 2),
            'show_results': True
        }
        
        return render(request, 'home/mortgage_calculator.html', context)

    return redirect('mortgage_calculator')
    
def browse_properties(request):
    properties = [
        {
            'id': 1,
            'title': 'PKR 1.6 Crore',
            'price': 1.6,
            'location': 'DHA Phase 4, Karachi',
            'type': '300 Yard Bungalow',
            'bedrooms': 5,
            'image': '/static/images/property1.jfif',   # Modern house
            'status': 'Unverified',
            'financing': True
        },
        {
            'id': 2,
            'title': 'PKR 3.8 Crore',
            'price': 3.8,
            'location': 'DHA Phase 4, Karachi',
            'type': '300 Yard Bungalow',
            'bedrooms': 6,
            'image': '/static/images/property2.jfif',   # Luxury bungalow
            'status': 'Verified',
            'financing': True
        },
        {
            'id': 3,
            'title': 'PKR 2.45 Crore',
            'price': 2.45,
            'location': 'DHA Phase 6, Karachi',
            'type': '250 Yard House',
            'bedrooms': 4,
            'image': '/static/images/property3.jfif',   # Interior + exterior feel
            'status': 'Unverified',
            'financing': True
        },
        {
            'id': 4,
            'title': 'PKR 5.2 Crore',
            'price':5.2,
            'location': 'DHA Phase 8, Karachi',
            'type': '400 Yard Luxury Bungalow',
            'bedrooms': 7,
            'image': '/static/images/property4.jfif',
            'status': 'Verified',
            'financing': True
        }
    ]
    # Get filter values from URL (GET parameters)
    selected_location = request.GET.get('location', '')
    selected_city = request.GET.get('city', '')
    selected_budget = request.GET.get('budget', '')

    # Apply filters
    filtered_properties = properties

    if selected_location:
        filtered_properties = [p for p in filtered_properties if selected_location.lower() in p['location'].lower()]

    if selected_city:
        filtered_properties = [
            p for p in filtered_properties
            if selected_city.lower() in p['location'].lower()
        ]
    if selected_budget:
        try:
            if selected_budget == 'under-2':
                filtered_properties = [p for p in filtered_properties if p['price'] < 2]
                print(filtered_properties)
            elif selected_budget == '2-5':
                filtered_properties = [p for p in filtered_properties if 2 <= p['price'] <= 5]
            elif selected_budget == 'above-5':
                filtered_properties = [p for p in filtered_properties if p['price'] > 5]
        except:
            pass

    context = {
        'properties': filtered_properties,
        'selected_location': selected_location,
        'selected_city': selected_city,
        'selected_budget': selected_budget,
    }
    return render(request, 'home/browse_properties.html', context)


def property_form(request, property_id):
    seller_number = "0300-1234567"
    print(property_id)
    return render(request, 'home/property_form.html', {'seller_number': seller_number})
# def auth_page(request, property_id):
#     context = {
#         'property_id': property_id
#     }
#     return render(request, 'home/auth.html', context)

def auth_page(request, property_id):
    if request.user.is_authenticated:
        return redirect('browse_properties')  # or property detail

    request.session['property_id'] = property_id
    return render(request, 'home/auth.html')
# def auth_page(request, property_id):
#     request.session['property_id'] = property_id  # save property
#     return render(request, 'home/auth.html')


# SIGNUP





# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('homepage')


# Redirect after login
def redirect_after_login(request):
    property_id = request.session.get('property_id')

    if property_id:
        # Remove it from session so it doesn't trigger again on next login
        del request.session['property_id'] 
        # Send them to the form they wanted
        return redirect('property_form', property_id=property_id)

    return redirect('homepage')

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Fetch all profiles from the database
    profiles = UserProfile.objects.all()
    return render(request, 'home/admin_dashboard.html', {'profiles': profiles})


# --- New Page Renders ---

def login_page(request):
    # If user is already logged in, don't show login page
    if request.user.is_authenticated:
        return redirect('homepage')
    return render(request, 'home/login.html')

def signup_page(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    return render(request, 'home/signup.html')

@csrf_exempt
def firebase_signup(request):
    """
    Handle Firebase signup - verify token and create Django user
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firebase_token = data.get('idToken')
            
            if not firebase_token:
                return JsonResponse({'error': 'No token provided'}, status=400)
            
            # Authenticate using Firebase backend
            user = authenticate(request, firebase_token=firebase_token)
            
            if user:
                login(request, user)
                
                # Check if there's a pending property
                property_id = request.session.get('property_id')
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/property-form/{property_id}/' if property_id else '/'
                })
            else:
                return JsonResponse({'error': 'Authentication failed'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
 
 
@csrf_exempt
def firebase_login(request):
    """
    Handle Firebase login - verify token and login Django user
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firebase_token = data.get('idToken')
            
            if not firebase_token:
                return JsonResponse({'error': 'No token provided'}, status=400)
            
            # Authenticate using Firebase backend
            user = authenticate(request, firebase_token=firebase_token)
            
            if user:
                login(request, user)
                
                # Check if there's a pending property
                property_id = request.session.get('property_id')
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/property-form/{property_id}/' if property_id else '/'
                })
            else:
                return JsonResponse({'error': 'Authentication failed'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
 
# --- Updated Logic Views ---

def signup_view(request):
    """Legacy signup view - redirects to new signup page"""
    return redirect('signup')
 
def login_view(request):
    """Legacy login view - redirects to new login page"""
    return redirect('login')

def property_detail(request, property_id):
    # First try real database model
    try:
        property_obj = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        # Fallback to dummy data if no real property exists yet
        dummy_properties = {
            1: {
                'id': 1,
                'title': 'Luxury Bungalow DHA Phase 4',
                'location': 'DHA Phase 4, Karachi',
                'price': '16000000',
                'bedrooms': 5,
                'type': '300 Yard House',
                'image': '/static/images/property1.jfif',
                'description': 'Beautiful 5 bedroom luxury bungalow in prime location of DHA Phase 4. Modern design with spacious living areas.',
                'status': 'Verified'
            },
            # Add more dummy entries for id 2,3,4 if needed
        }
        property_obj = dummy_properties.get(property_id)

    if not property_obj:
        # Optional: show 404
        from django.http import Http404
        raise Http404("Property not found")

    context = {
        'property': property_obj,
    }
    return render(request, 'home/property_details.html', context)

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, username=email, password=password)

#         if user:
#             login(request, user)
#             return redirect_after_login(request)
#         else:
#             # Redirect back to login page with error
#             return render(request, 'home/login.html', {'error': 'Invalid credentials'})
#     return redirect('login_page')