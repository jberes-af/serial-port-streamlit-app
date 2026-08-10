# /src/infrastructure/config/secret_provider.py

from abc import ABC, abstractmethod
from pathlib import Path
import os

from dotenv import load_dotenv


class SecretProvider(ABC):
    @abstractmethod
    def get(
            self,
            name: str,
            default: str | None = None,
    ) -> str | None:
        raise NotImplementedError

    def get_required(self, name: str) -> str:
        value = self.get(name)

        if value is None or not value.strip():
            raise RuntimeError(
                f"Missing required secret: {name}"
            )

        return value.strip()


class StreamlitSecretProvider(SecretProvider):
    def get(
            self,
            name: str,
            default: str | None = None,
    ) -> str | None:
        try:
            import streamlit as st
        except ImportError:
            return default

        try:
            value = st.secrets.get(name, default)
        except Exception:
            return default

        if value is None:
            return None

        return str(value).strip()


class EnvSecretProvider(SecretProvider):
    def __init__(
            self,
            env_path: Path | None = None,
            *,
            require_env_file: bool = False,
    ) -> None:
        if env_path is None:
            return

        resolved_path = env_path.resolve()

        if not resolved_path.exists():
            if require_env_file:
                raise FileNotFoundError(
                    f"Environment file not found: {resolved_path}"
                )

            return

        load_dotenv(
            dotenv_path=resolved_path,
            override=False,
        )

    def get(
            self,
            name: str,
            default: str | None = None,
    ) -> str | None:
        value = os.getenv(name, default)

        if value is None:
            return None

        return value.strip()


class FallbackSecretProvider(SecretProvider):
    def __init__(
            self,
            *providers: SecretProvider,
    ) -> None:
        if not providers:
            raise ValueError(
                "At least one secret provider is required."
            )

        self._providers = providers

    def get(
            self,
            name: str,
            default: str | None = None,
    ) -> str | None:
        for provider in self._providers:
            value = provider.get(name)

            if value is not None and value.strip():
                return value.strip()

        return default
