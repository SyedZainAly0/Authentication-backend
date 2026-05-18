import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status
from app.utils.token import create_access_token, create_refresh_token, verify_token, verify_refresh_token
from app.core.config import settings

class TestTokenUtilities:
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "123", "username": "testuser"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_verify_token_valid(self):
        """Test verification of valid access token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
    
    def test_verify_token_invalid_type(self):
        """Test verification fails for refresh token when expecting access token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_refresh_token(data)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate token" in exc_info.value.detail
    
    def test_verify_token_invalid_signature(self):
        """Test verification fails for token with invalid signature"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate token" in exc_info.value.detail
    
    def test_verify_refresh_token_valid(self):
        """Test verification of valid refresh token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_refresh_token(data)
        
        user_id = verify_refresh_token(token)
        assert user_id == "123"
    
    def test_verify_refresh_token_invalid_type(self):
        """Test verification fails for access token when expecting refresh token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired refresh token" in exc_info.value.detail
    
    def test_verify_refresh_token_missing_sub(self):
        """Test verification fails when sub is missing"""
        # Create a token without sub
        from jose import jwt
        from datetime import datetime, timedelta
        
        payload = {
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "refresh"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired refresh token" in exc_info.value.detail
    
    def test_verify_refresh_token_invalid_signature(self):
        """Test verification fails for token with invalid signature"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired refresh token" in exc_info.value.detail
