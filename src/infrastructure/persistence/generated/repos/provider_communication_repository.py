# repository.py.tpl


# AUTO GENERATED

from src.application.ports.provider_communication_repository_port import (
    ProviderCommunicationRepositoryPort,
)

from src.domain.entities.provider_communication_entities import (
    ProviderCommunication,
)

from src.infrastructure.persistence.google_sheets.base_repository import (
    GoogleSheetsRepository,
)

from src.infrastructure.persistence.google_sheets.google_sheet_catalog import (
    GoogleSheetCatalog,
)

from src.infrastructure.persistence.google_sheets.sheets_query_service import (
    GoogleSheetsQueryService,
)

from src.infrastructure.persistence.mappers.provider_communication.provider_communication_row_mapper import (
    ProviderCommunicationRowMapper,
)


from src.infrastructure.persistence.schemas.provider_communication.provider_communication_columns import (
    ProviderCommunicationColumns,
)


class GoogleSheetsProviderCommunicationRepository(
    GoogleSheetsRepository,
    ProviderCommunicationRepositoryPort,
):

    TABLE_NAME = "provider_communication"
    ID_COLUMN = ProviderCommunicationColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: ProviderCommunicationRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_provider_communications(self) -> tuple[ProviderCommunication, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> ProviderCommunication:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
