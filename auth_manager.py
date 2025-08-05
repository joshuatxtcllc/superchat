
import streamlit as st
import hashlib
import jwt
import secrets
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
import json
import os
from database import DatabaseManager

@dataclass
class User:
    """User data model"""
    id: str
    username: str
    email: str
    password_hash: str
    role: str = "user"  # user, admin, super_admin
    created_at: str = ""
    last_login: str = ""
    is_active: bool = True
    preferences: Dict = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class UserSession:
    """User session data"""
    user_id: str
    username: str
    role: str
    login_time: str
    expires_at: str

class AuthManager:
    """Enterprise authentication and authorization manager"""
    
    def __init__(self):
        self.secret_key = os.environ.get('AUTH_SECRET_KEY', self._generate_secret_key())
        self.session_duration_hours = 24
        self.users_file = "users.json"
        self.db = DatabaseManager()
        
        # Initialize admin user if none exists
        self._initialize_admin_user()
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            hash_part, salt = password_hash.split(':')
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == hash_part
        except:
            return False
    
    def _initialize_admin_user(self):
        """Create default admin user if none exists"""
        if not self._load_users():
            admin_user = User(
                id="admin_001",
                username="admin",
                email="admin@company.com",
                password_hash=self._hash_password("admin123"),  # Change in production!
                role="super_admin"
            )
            self._save_user(admin_user)
    
    def _load_users(self) -> Dict[str, User]:
        """Load users from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    return {uid: User(**user_data) for uid, user_data in data.items()}
        except Exception as e:
            st.error(f"Error loading users: {e}")
        return {}
    
    def _save_user(self, user: User):
        """Save user to file"""
        users = self._load_users()
        users[user.id] = user
        
        try:
            with open(self.users_file, 'w') as f:
                json.dump({uid: asdict(u) for uid, u in users.items()}, f, indent=2)
        except Exception as e:
            st.error(f"Error saving user: {e}")
    
    def register_user(self, username: str, email: str, password: str, role: str = "user") -> bool:
        """Register a new user"""
        users = self._load_users()
        
        # Check if username or email already exists
        for user in users.values():
            if user.username == username or user.email == email:
                return False
        
        # Create new user
        user_id = f"user_{len(users) + 1:03d}"
        new_user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            role=role
        )
        
        self._save_user(new_user)
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        users = self._load_users()
        
        for user in users.values():
            if user.username == username and user.is_active:
                if self._verify_password(password, user.password_hash):
                    # Update last login
                    user.last_login = datetime.now().isoformat()
                    self._save_user(user)
                    return user
        return None
    
    def create_session_token(self, user: User) -> str:
        """Create JWT session token"""
        expires_at = datetime.now() + timedelta(hours=self.session_duration_hours)
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': expires_at.timestamp(),
            'iat': datetime.now().timestamp()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_session_token(self, token: str) -> Optional[UserSession]:
        """Verify and decode session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            return UserSession(
                user_id=payload['user_id'],
                username=payload['username'],
                role=payload['role'],
                login_time=datetime.fromtimestamp(payload['iat']).isoformat(),
                expires_at=datetime.fromtimestamp(payload['exp']).isoformat()
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, required_role: str = "user") -> Optional[UserSession]:
        """Decorator/middleware for requiring authentication"""
        if 'auth_token' not in st.session_state:
            return None
        
        session = self.verify_session_token(st.session_state['auth_token'])
        if not session:
            del st.session_state['auth_token']
            return None
        
        # Check role authorization
        role_hierarchy = {"user": 1, "admin": 2, "super_admin": 3}
        user_level = role_hierarchy.get(session.role, 0)
        required_level = role_hierarchy.get(required_role, 1)
        
        if user_level < required_level:
            return None
        
        return session
    
    def render_login_page(self):
        """Render login/registration page"""
        st.title("🔐 Authentication Required")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.header("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    user = self.authenticate_user(username, password)
                    if user:
                        token = self.create_session_token(user)
                        st.session_state['auth_token'] = token
                        st.session_state['current_user'] = user.username
                        st.session_state['user_role'] = user.role
                        st.success(f"Welcome back, {user.username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            st.header("Register New Account")
            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email Address")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register")
                
                if submitted:
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters")
                    elif self.register_user(new_username, new_email, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username or email already exists")
    
    def render_user_management(self):
        """Render user management interface (admin only)"""
        st.header("👥 User Management")
        
        users = self._load_users()
        
        # User list
        for user in users.values():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                status = "🟢 Active" if user.is_active else "🔴 Inactive"
                st.write(f"**{user.username}** ({status})")
            
            with col2:
                st.write(f"{user.email} - {user.role}")
            
            with col3:
                if st.button(f"{'Deactivate' if user.is_active else 'Activate'}", key=f"toggle_{user.id}"):
                    user.is_active = not user.is_active
                    self._save_user(user)
                    st.rerun()
            
            with col4:
                if user.role != "super_admin" and st.button("Delete", key=f"delete_{user.id}"):
                    users = self._load_users()
                    del users[user.id]
                    try:
                        with open(self.users_file, 'w') as f:
                            json.dump({uid: asdict(u) for uid, u in users.items()}, f, indent=2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting user: {e}")
    
    def logout(self):
        """Logout current user"""
        for key in ['auth_token', 'current_user', 'user_role']:
            if key in st.session_state:
                del st.session_state[key]

# Global auth manager instance
try:
    auth_manager = AuthManager()
except Exception as e:
    import streamlit as st
    st.error(f"Failed to initialize auth manager: {e}")
    auth_manager = None
