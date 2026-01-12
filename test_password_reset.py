"""
Test script to verify password reset confirm endpoint
"""
import requests

def test_password_reset_endpoint():
    """
    Test the password reset confirm endpoint accessibility
    """
    print("=" * 60)
    print("Testing Password Reset Confirm Endpoint")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/users/auth/password/reset/confirm/"
    
    print(f"\n1. Testing endpoint: {endpoint}")
    
    # Test with invalid data first just to verify endpoint exists
    # We expect a 400 (bad request) not a 404 (not found)
    payload = {
        "uid": "test-uid",
        "token": "test-token",
        "new_password1": "NewSecurePassword123!@",
        "new_password2": "NewSecurePassword123!@"
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"\n2. Response Status: {response.status_code}")
        print(f"   Response Body: {response.text[:300]}")
        
        if response.status_code == 404:
            print("\n✗ FAILED: Endpoint not found (404)")
            print("   The URL path is still incorrect.")
            return False
        elif response.status_code == 400:
            print("\n✓ SUCCESS: Endpoint exists and is responding!")
            print("   Status 400 is expected with invalid token/uid")
            print("   The endpoint is correctly configured at:")
            print(f"   {endpoint}")
            return True
        elif response.status_code == 200:
            print("\n⚠ UNEXPECTED: Got 200 OK with test data")
            print("   This shouldn't happen with invalid token")
            return True
        else:
            print(f"\n⚠ Got status code: {response.status_code}")
            try:
                print(f"   Response JSON: {response.json()}")
            except:
                pass
            # Any response except 404 means the endpoint exists
            return response.status_code != 404
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to the server")
        print("   Make sure the Django development server is running:")
        print("   python manage.py runserver")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        return False
    finally:
        print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    success = test_password_reset_endpoint()
    sys.exit(0 if success else 1)

