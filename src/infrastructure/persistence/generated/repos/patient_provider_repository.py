# repository.py.tpl


# AUTO GENERATED

from src.application.ports.patient_provider_repository_port import (
    PatientProviderRepositoryPort,
)

from src.domain.entities.patient_provider_entities import (
    PatientProvider,
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

from src.infrastructure.persistence.mappers.patient_provider.patient_provider_row_mapper import (
    PatientProviderRowMapper,
)


from src.infrastructure.persistence.schemas.patient_provider.patient_provider_columns import (
    PatientProviderColumns,
)


class GoogleSheetsPatientProviderRepository(
    GoogleSheetsRepository,
    PatientProviderRepositoryPort,
):

    TABLE_NAME = "patient_provider"
    ID_COLUMN = PatientProviderColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: PatientProviderRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_patient_providers(self) -> tuple[PatientProvider, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> PatientProvider:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
