# /src/infrastructure/config/firebase_settings_loader.py

from typing import Any

from src.infrastructure.config.secret_provider import SecretProvider
from src.infrastructure.config.settings_model import (
    FirebaseAuthenticationSettings,
)


def load_firebase_authentication_settings(
        secret_provider: SecretProvider,
) -> FirebaseAuthenticationSettings:
    return FirebaseAuthenticationSettings(
        api_key=secret_provider.get_required("FIREBASE_API_KEY"),
        auth_domain=secret_provider.get_required("FIREBASE_AUTH_DOMAIN"),
        project_id=secret_provider.get_required("FIREBASE_PROJECT_ID"),
        app_id=secret_provider.get_required("FIREBASE_APP_ID"),
    )


"""

def load_firebase_web_settings2(
        secret_provider: SecretProvider,
) -> FirebaseWebSettings:
    return FirebaseWebSettings(
        api_key=secret_provider.get_required("FIREBASE_API_KEY"),
        auth_domain=secret_provider.get_required("FIREBASE_AUTH_DOMAIN"),
        database_url=secret_provider.get_required("FIREBASE_DATABASE_URL"),
        project_id=secret_provider.get_required("FIREBASE_PROJECT_ID"),
        storage_bucket=secret_provider.get_required("FIREBASE_STORAGE_BUCKET"),
        messaging_sender_id=secret_provider.get_required(
            "FIREBASE_MESSAGING_SENDER_ID"
        ),
        app_id=secret_provider.get_required("FIREBASE_APP_ID"),
    )


def load_firebase_authentication_settings2(
        secret_provider: SecretProvider,
) -> FirebaseAuthenticationSettings:
    return FirebaseAuthenticationSettings(
        api_key=secret_provider.get_required("FIREBASE_API_KEY"),
        auth_domain=secret_provider.get_required("FIREBASE_AUTH_DOMAIN"),
        project_id=secret_provider.get_required("FIREBASE_PROJECT_ID"),
        app_id=secret_provider.get_required("FIREBASE_APP_ID"),
    )
    
def load_firebase_admin_service_account(
        secret_provider: SecretProvider,
) -> dict[str, Any]:
    private_key = secret_provider.get_required(
        "FIREBASE_ADMIN_PRIVATE_KEY"
    )

    return {
        "type": "service_account",
        "project_id": secret_provider.get_required(
            "FIREBASE_ADMIN_PROJECT_ID"
        ),
        "private_key_id": secret_provider.get_required(
            "FIREBASE_ADMIN_PRIVATE_KEY_ID"
        ),
        "private_key": private_key.replace("\\n", "\n"),
        "client_email": secret_provider.get_required(
            "FIREBASE_ADMIN_CLIENT_EMAIL"
        ),
        "client_id": secret_provider.get_required(
            "FIREBASE_ADMIN_CLIENT_ID"
        ),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": (
            "https://www.googleapis.com/oauth2/v1/certs"
        ),
        "client_x509_cert_url": secret_provider.get_required(
            "FIREBASE_ADMIN_CLIENT_X509_CERT_URL"
        ),
        "universe_domain": "googleapis.com",
    }


def load_firebase_admin_settings(
        secret_provider: SecretProvider,
) -> FirebaseAdminSettings:
    return FirebaseAdminSettings(
        database_url=secret_provider.get_required("FIREBASE_DATABASE_URL"),
        service_account_info=load_firebase_admin_service_account(
            secret_provider
        ),
    )
"""
