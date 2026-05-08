"""
Firebase Authentication Backend for Django
This module handles Firebase token verification and user management
"""
import firebase_admin
from firebase_admin import credentials, auth
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

# Initialize Firebase Admin SDK
# Note: You'll need to download your service account key from Firebase Console
# and place it in your project directory
try:
    # If not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")


class FirebaseAuthenticationBackend(BaseBackend):
    """
    Custom authentication backend that verifies Firebase ID tokens
    and creates/retrieves corresponding Django users
    """
    
    def authenticate(self, request, firebase_token=None, **kwargs):
        """
        Verify Firebase token and return Django user
        
        Args:
            request: Django request object
            firebase_token: Firebase ID token from client
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if firebase_token is None:
            return None
        
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(firebase_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            
            # Get or create Django user
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': name,
                }
            )
            
            # Store Firebase UID in user profile or session
            request.session['firebase_uid'] = uid
            
            return user
            
        except auth.InvalidIdTokenError:
            print("Invalid Firebase token")
            return None
        except Exception as e:
            print(f"Firebase authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None