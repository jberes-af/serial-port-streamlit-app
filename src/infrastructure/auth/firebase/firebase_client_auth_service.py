# /src/infrastructure/firebase_auth/firebase_client_auth_service.py

# src/infrastructure/firebase_auth/firebase_client_auth_service.py

from typing import Any

import pyrebase
from requests.exceptions import HTTPError

from src.application.auth.dto import AuthenticatedUserDTO


class FirebaseClientAuthService:
    def __init__(self, web_config: dict[str, Any]) -> None:
        firebase = pyrebase.initialize_app(web_config)
        self._auth = firebase.auth()

    def authenticate(self, email: str, password: str) -> AuthenticatedUserDTO:
        try:
            user: dict[str, Any] = self._auth.sign_in_with_email_and_password(
                email,
                password,
            )
        except HTTPError as exc:
            raise ValueError("Invalid email or password.") from exc

        return AuthenticatedUserDTO(
            email=user["email"],
            uid=user["localId"],
            id_token=user["idToken"],
            refresh_token=user["refreshToken"],
            display_name=user.get("displayName", ""),
        )
