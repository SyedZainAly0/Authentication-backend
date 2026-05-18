import pytest
from app.utils.response import success_response, error_response, APIResponse

class TestResponseUtilities:
    
    def test_success_response_basic(self):
        """Test basic success response"""
        response = success_response("Operation successful")
        
        assert isinstance(response, APIResponse)
        assert response.status == "success"
        assert response.message == "Operation successful"
        assert response.data is None
    
    def test_success_response_with_data(self):
        """Test success response with data"""
        data = {"id": 1, "name": "test"}
        response = success_response("User created", data)
        
        assert response.status == "success"
        assert response.message == "User created"
        assert response.data == data
    
    def test_success_response_with_list_data(self):
        """Test success response with list data"""
        data = [1, 2, 3, 4, 5]
        response = success_response("Items retrieved", data)
        
        assert response.status == "success"
        assert response.message == "Items retrieved"
        assert response.data == data
    
    def test_error_response_basic(self):
        """Test basic error response"""
        response = error_response("Operation failed")
        
        assert isinstance(response, APIResponse)
        assert response.status == "error"
        assert response.message == "Operation failed"
        assert response.data is None
    
    def test_error_response_with_data(self):
        """Test error response with data"""
        data = {"error_code": 500, "details": "Internal server error"}
        response = error_response("Server error", data)
        
        assert response.status == "error"
        assert response.message == "Server error"
        assert response.data == data
    
    def test_response_serialization(self):
        """Test that response can be serialized to dict"""
        data = {"id": 1, "name": "test"}
        response = success_response("Test", data)
        
        response_dict = response.model_dump()
        assert response_dict["status"] == "success"
        assert response_dict["message"] == "Test"
        assert response_dict["data"] == data
    
    def test_response_json_compatibility(self):
        """Test that response is JSON compatible"""
        data = {"id": 1, "name": "test"}
        response = success_response("Test", data)
        
        # This should not raise an exception
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert len(json_str) > 0
