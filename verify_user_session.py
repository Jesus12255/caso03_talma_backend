import asyncio
from unittest.mock import patch, MagicMock
from app.auth.dependencies.dependencies_auth import get_current_user
from app.core.context.user_context import get_user_session
from fastapi import HTTPException

async def test_user_session_context():
    print("Testing UserSession context...")
    
    # Mock settings and jwt
    with patch("app.auth.dependencies.dependencies_auth.settings") as mock_settings, \
         patch("app.auth.dependencies.dependencies_auth.jwt") as mock_jwt:
        
        mock_settings.SECRET_KEY = "secret"
        mock_settings.ALGORITHM = "HS256"
        
        # Test case: Valid token
        mock_jwt.decode.return_value = {"sub": "test@example.com"}
        token = "valid_token"
        
        try:
            email = await get_current_user(token)
            print(f"User email: {email}")
            
            session = get_user_session()
            if session:
                print(f"UserSession found: {session}")
                if session.email == "test@example.com":
                    print("SUCCESS: UserSession email matches.")
                else:
                    print(f"FAILURE: UserSession email mismatch. Got {session.email}")
            else:
                print("FAILURE: UserSession is None.")
                
        except HTTPException as e:
            print(f"FAILURE: Unexpected HTTPException: {e}")
        except Exception as e:
            print(f"FAILURE: Unexpected Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_user_session_context())
