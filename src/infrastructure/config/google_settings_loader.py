# /src/infrastructure/config/google_settings_loader.py

from typing import Any

from src.infrastructure.config.secret_provider import (
    SecretProvider,
)


class GoogleSettingsError(RuntimeError):
    pass


def load_google_service_account_key(
        secret_provider: SecretProvider,
) -> dict[str, Any]:
    client_email = secret_provider.get_required(
        "CLIENT_EMAIL"
    )

    private_key = secret_provider.get_required(
        "PRIVATE_KEY"
    ).replace("\\n", "\n")

    return {
        "type": "service_account",
        "project_id": secret_provider.get_required(
            "PROJECT_ID"
        ),
        "private_key_id": secret_provider.get_required(
            "PRIVATE_KEY_ID"
        ),
        "private_key": private_key,
        "client_email": client_email,
        "client_id": secret_provider.get_required(
            "CLIENT_ID"
        ),
        "auth_uri": (
            "https://accounts.google.com/o/oauth2/auth"
        ),
        "token_uri": (
            "https://oauth2.googleapis.com/token"
        ),
        "auth_provider_x509_cert_url": (
            "https://www.googleapis.com/oauth2/v1/certs"
        ),
        "client_x509_cert_url": (
            "https://www.googleapis.com/robot/v1/"
            "metadata/x509/"
            f"{client_email.replace('@', '%40')}"
        ),
        "universe_domain": "googleapis.com",
    }


def load_spreadsheet_ids(
        secret_provider: SecretProvider,
) -> dict[str, str]:
    """
    spreadsheet_name_billing = secret_provider.get_required(
        "SHEETS_NAME_BILLING"
    )

    spreadsheet_id_billing = secret_provider.get_required(
        "SHEETS_ID_BILLING"
    )

    spreadsheet_name_patient = secret_provider.get_required(
        "SHEETS_NAME_PATIENT"
    )

    spreadsheet_id_patient = secret_provider.get_required(
        "SHEETS_ID_PATIENT"
    )

    spreadsheet_id_provider = secret_provider.get_required(
        "SHEETS_ID_PROVIDER"
    )
    spreadsheet_name_provider = secret_provider.get_required(
        "SHEETS_NAME_PROVIDER"
    )

    spreadsheet_name_treatment = secret_provider.get_required(
        "SHEETS_NAME_TREATMENT"
    )

    spreadsheet_id_treatment = secret_provider.get_required(
        "SHEETS_ID_TREATMENT"
    )

    return {
        spreadsheet_name_billing: spreadsheet_id_billing,
        spreadsheet_name_patient: spreadsheet_id_patient,
        spreadsheet_name_provider: spreadsheet_id_provider,
        spreadsheet_name_treatment: spreadsheet_id_treatment,
    }
    """

    spreadsheet_name_patient = secret_provider.get_required(
        "SHEETS_NAME_PATIENT"
    )

    spreadsheet_id_patient = secret_provider.get_required(
        "SHEETS_ID_PATIENT"
    )

    return {
        spreadsheet_name_patient: spreadsheet_id_patient,
    }
