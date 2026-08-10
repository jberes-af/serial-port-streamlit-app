# /service_account_credentials_provider.py

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from google.oauth2.service_account import Credentials


@dataclass(frozen=True, slots=True)
class GoogleServiceAccountCredentialsProvider:
    service_account_info: Mapping[str, Any]
    scopes: Sequence[str]

    def load(self) -> Credentials:
        return Credentials.from_service_account_info(
            dict(self.service_account_info),
            scopes=list(self.scopes),
        )