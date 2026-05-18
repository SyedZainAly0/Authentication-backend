import pytest
from app.utils.hashing import hash_password, verify_password

class TestHashingUtilities:
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Hash should be different from original
    
    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different hashes due to salt
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) == False
    
    def test_verify_password_empty_string(self):
        """Test password verification with empty string"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) == False
    
    def test_hash_and_verify_various_passwords(self):
        """Test hashing and verification with various password types"""
        passwords = [
            "simple",
            "complex123!@#",
            "verylongpasswordwithmanychars123456789",
            "P@ssw0rd!#$%",
            "unicode_password_你好世界"
        ]
        
        for password in passwords:
            hashed = hash_password(password)
            assert verify_password(password, hashed) == True
            assert verify_password("wrong" + password, hashed) == False
