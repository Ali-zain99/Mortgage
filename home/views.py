from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import UserProfile
from .models import Property
from django.shortcuts import get_object_or_404

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
        return redirect('signup')
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

# def browse_properties(request):
#     properties = Property.objects.all()

#     selected_location = request.GET.get('location', '')
#     selected_city = request.GET.get('city', '')
#     selected_budget = request.GET.get('budget', '')

#     if selected_location:
#         properties = properties.filter(location__icontains=selected_location)

#     if selected_city:
#         properties = properties.filter(city__icontains=selected_city)

#     if selected_budget:
#         if selected_budget == 'under-2':
#             properties = properties.filter(price__lt=20000000)
#         elif selected_budget == '2-5':
#             properties = properties.filter(price__gte=20000000, price__lte=50000000)
#         elif selected_budget == 'above-5':
#             properties = properties.filter(price__gt=50000000)

#     return render(request, 'home/browse_properties.html', {
#         'properties': properties
#     })
def property_form(request, property_id):
    seller_number = "0300-1234567"  # dummy seller number

    if request.method == "POST":
        name = request.POST.get('name')
        city = request.POST.get('city')
        contact = request.POST.get('contact')
        cnic = request.POST.get('cnic')
        UserProfile.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=name,
            city=city,
            contact_no=contact,
            cnic=cnic,
            property_id=property_id
        )
        context = {
            'show_modal': True,
            'seller_number': seller_number
        }
        return render(request, 'home/property_form.html', context)

    return render(request, 'home/property_form.html')
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

# --- Updated Logic Views ---

def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=email).exists():
            # Redirect back to signup page with error
            return render(request, 'home/signup.html', {'error': 'User already exists'})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        login(request, user)
        return redirect_after_login(request)
    return redirect('signup_page')

# def property_detail(request, property_id):
#     property_obj = get_object_or_404(Property, id=property_id)

#     return render(request, 'home/property_details.html', {
#         'property': property_obj
#     })
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

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect_after_login(request)
        else:
            # Redirect back to login page with error
            return render(request, 'home/login.html', {'error': 'Invalid credentials'})
    return redirect('login_page')