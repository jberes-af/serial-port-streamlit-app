# /src/infrastructure/config/settings_model.py

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class FirebaseAuthenticationSettings:
    api_key: str
    auth_domain: str
    project_id: str
    app_id: str


"""
@dataclass(frozen=True)
class M365Settings:
    m365_tenant_id: str
    m365_client_id: str
    m365_client_secret: str


@dataclass(frozen=True)
class FirebaseAdminSettings:
    database_url: str
    service_account_info: dict[str, Any]


@dataclass(frozen=True)
class FirebaseWebSettings:
    api_key: str
    auth_domain: str
    database_url: str
    project_id: str
    storage_bucket: str
    messaging_sender_id: str
    app_id: str

    def to_pyrebase_config(self) -> Mapping[str, str]:
        return {
            "apiKey": self.api_key,
            "authDomain": self.auth_domain,
            "databaseURL": self.database_url,
            "projectId": self.project_id,
            "storageBucket": self.storage_bucket,
            "messagingSenderId": self.messaging_sender_id,
            "appId": self.app_id,
        }
"""


@dataclass(frozen=True)
class Settings:
    project_root: Path
    config_path: Path

    google_service_account: Mapping[str, str]
    spreadsheet_ids_by_file: Mapping[str, str]

    firebase_authentication: FirebaseAuthenticationSettings

    # m365_authentication: M365Settings
