import pytest
from fastapi import status
from app.models.user import User
from app.utils.hashing import hash_password

class TestAuthRoutes:
    
    def test_register_user_success(self, client):
        """Test successful user registration"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "User registered successfully"
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["email"] == "john@example.com"
        assert data["data"]["username"] == "johndoe"
    
    def test_register_user_duplicate_email(self, client):
        """Test registration with duplicate email"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        # Register first user
        client.post("/auth/register", json=user_data)
        
        # Try to register with same email
        user_data2 = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "john@example.com",
            "username": "janesmith",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data2)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_user_duplicate_username(self, client):
        """Test registration with duplicate username"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        # Register first user
        client.post("/auth/register", json=user_data)
        
        # Try to register with same username
        user_data2 = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data2)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]
    
    def test_register_user_password_mismatch(self, client):
        """Test registration with password mismatch"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "differentpassword"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Passwords do not match" in response.json()["detail"]
    
    def test_login_user_success(self, client):
        """Test successful user login"""
        # First register a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "password123"
        }
        client.post("/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "email": "john@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Login successful"
        assert "data" in data
        assert data["data"]["email"] == "john@example.com"
        assert data["data"]["username"] == "johndoe"
        
        # Check cookies are set
        cookies = response.cookies
        assert "access_token" in cookies
        assert "refresh_token" in cookies
    
    def test_login_user_not_found(self, client):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_login_user_incorrect_password(self, client):
        """Test login with incorrect password"""
        # First register a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
            "password": "password123",
            "confirm_password": "password123"
        }
        client.post("/auth/register", json=user_data)
        
        # Try login with wrong password
        login_data = {
            "email": "john@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect password" in response.json()["detail"]
    
    def test_logout_success(self, client):
        """Test successful logout"""
        response = client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Logged out successfully"
        
        # Check cookies are deleted
        cookies = response.cookies
        # After deletion, cookies should be empty or have max_age=0
        for cookie in cookies:
            if cookie.name in ["access_token", "refresh_token"]:
                assert cookie.expires or cookie.max_age == 0
    
    def test_refresh_token_missing(self, client):
        """Test refresh endpoint with missing refresh token"""
        response = client.post("/auth/refresh")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Refresh token missing" in response.json()["detail"]
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Auth API is running"}
