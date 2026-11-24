import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    def test_create_user_with_email_success(self):
        user = User.objects.create_user(
            email="developer@example.com",
            password="StrongPassword123!",
        )
        assert user.email == "developer@example.com"
        assert user.check_password("StrongPassword123!")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert str(user) == "developer@example.com"

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(
            email="TEST.User@EXAMPLE.COM",
            password="StrongPassword123!",
        )
        assert user.email == "TEST.User@example.com"

    def test_create_user_missing_email_raises_error(self):
        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email="")

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(
            email="admin@pulseapi.dev",
            password="AdminPassword123!",
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True
