# infrastructure/firebase_auth/firebase_auth_directory_adapter.py

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple

from firebase_admin import auth
from firebase_admin import App as FirebaseApp

from src.application.auth.dto import AuthenticatedUserDTO, LoginRequestDTO
from src.application.auth.ports import AuthProvider


def _ms_to_dt(ms: Optional[int]) -> Optional[datetime]:
    if ms is None:
        return None
    # Firebase provides ms since epoch
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)


def _to_profile(u: auth.UserRecord) -> AuthUserProfileDTO:
    provider_ids: Tuple[str, ...] = tuple(
        info.provider_id for info in (u.provider_data or [])
    )
    meta = u.user_metadata
    created_at = _ms_to_dt(getattr(meta, "creation_timestamp", None))
    last_sign_in_at = _ms_to_dt(getattr(meta, "last_sign_in_timestamp", None))

    return AuthUserProfileDTO(
        uid=u.uid,
        email=u.email,
        display_name=u.display_name,
        email_verified=bool(u.email_verified),
        disabled=bool(u.disabled),
        provider_ids=provider_ids,
        created_at=created_at,
        last_sign_in_at=last_sign_in_at,
    )


@dataclass(frozen=True)
class FirebaseAuthDirectoryAdapter(AuthDirectoryPort):
    app: FirebaseApp

    def create_user_with_email(
        self,
        *,
        email: str,
        display_name: Optional[str] = None,
        password: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> AuthUserProfileDTO:
        params: dict[str, object] = {
            "email": email,
            "email_verified": False,
            "disabled": False,
        }
        if display_name:
            params["display_name"] = display_name
        if password:
            params["password"] = password
        if uid:
            params["uid"] = uid

        user = auth.create_user(app=self.app, **params)
        return _to_profile(user)

    def update_display_name(self, *, uid: str, display_name: str) -> AuthUserProfileDTO:
        user = auth.update_user(uid, display_name=display_name, app=self.app)
        return _to_profile(user)

    def get_user_by_email(self, *, email: str) -> Optional[AuthUserProfileDTO]:
        try:
            user = auth.get_user_by_email(email, app=self.app)
            return _to_profile(user)
        except auth.UserNotFoundError:
            return None

    def get_user_by_uid(self, *, uid: str) -> Optional[AuthUserProfileDTO]:
        try:
            user = auth.get_user(uid, app=self.app)
            return _to_profile(user)
        except auth.UserNotFoundError:
            return None

    def list_users(self) -> Iterable[AuthUserProfileDTO]:
        # Streaming iterator; caller may wrap list(...) if desired
        for user in auth.list_users(app=self.app).iterate_all():
            yield _to_profile(user)