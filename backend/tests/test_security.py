import pytest
from app.core.security import verify_password, hash_password


@pytest.mark.unit
def test_password_hashing():
    password = "securepassword123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


@pytest.mark.unit
def test_password_hashing_consistency():
    password = "mypassword"
    
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    assert hash1 != hash2
    
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
