# base_repository.py


# /src/infrastructure/persistence/google_sheets/google_sheets_repository.py

from abc import ABC

from src.infrastructure.persistence.common.types import RawRow

from src.infrastructure.persistence.google_sheets.google_sheet_catalog import (
    GoogleSheetCatalog,
)

from src.infrastructure.persistence.google_sheets.sheets_query_service import (
    GoogleSheetsQueryService,
)


class GoogleSheetsRepository(ABC):
    TABLE_NAME: str

    def __init__(
            self,
            *,
            query_service: GoogleSheetsQueryService,
            catalog: GoogleSheetCatalog,
    ) -> None:
        self._query_service = query_service
        self._catalog = catalog

    def _read_rows(
            self,
    ) -> list[RawRow]:
        table = self._catalog.table(
            self.TABLE_NAME,
        )

        return self._query_service.read_values(
            spreadsheet_id=table.spreadsheet_id,
            range_a1=table.range_a1,
        )

    @staticmethod
    def _find_single_row(
            *,
            rows: list[RawRow],
            column_name: str,
            value: str,
    ) -> RawRow:
        """
        Return exactly one matching row.

        Raises
        ------
        KeyError
            No matching row was found.

        ValueError
            More than one matching row was found.
        """

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "Lookup value cannot be empty."
            )

        matches: list[RawRow] = []

        for row in rows:

            row_value = str(
                row.get(column_name, "")
            ).strip()

            if row_value == normalized_value:
                matches.append(row)

        if not matches:
            raise KeyError(
                f"No row found where "
                f"{column_name!r} == "
                f"{normalized_value!r}."
            )

        if len(matches) > 1:
            raise ValueError(
                f"Expected exactly one row where "
                f"{column_name!r} == "
                f"{normalized_value!r}, "
                f"found {len(matches)}."
            )

        return matches[0]

    @staticmethod
    def _find_rows(
            *,
            rows: list[RawRow],
            column_name: str,
            value: str,
    ) -> list[RawRow]:

        normalized_value = value.strip()

        return [
            row
            for row in rows
            if str(
                row.get(column_name, "")
            ).strip() == normalized_value
        ]
