# /src/infrastructure/persistence/google_sheets/google_sheet_catalog.py

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GoogleSheetLocator:
    spreadsheet_id: str
    worksheet_name: str
    worksheet_range: str

    @property
    def range_a1(self) -> str:
        return (
            f"{self.worksheet_name}!"
            f"{self.worksheet_range}"
        )


@dataclass(frozen=True, slots=True)
class GoogleSheetCatalog:
    _tables: dict[str, GoogleSheetLocator]

    def table(
            self,
            name: str,
    ) -> GoogleSheetLocator:

        try:
            return self._tables[name]

        except KeyError as ex:
            raise KeyError(
                f"Unknown Google Sheets table: {name!r}"
            ) from ex

    def contains(
            self,
            name: str,
    ) -> bool:
        return name in self._tables

    def names(
            self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(self._tables)
        )
