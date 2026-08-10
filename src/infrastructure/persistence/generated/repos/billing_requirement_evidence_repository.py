# repository.py.tpl


# AUTO GENERATED

from src.application.ports.billing_requirement_evidence_repository_port import (
    BillingRequirementEvidenceRepositoryPort,
)

from src.domain.entities.billing_requirement_evidence_entities import (
    BillingRequirementEvidence,
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

from src.infrastructure.persistence.mappers.billing_requirement_evidence.billing_requirement_evidence_row_mapper import (
    BillingRequirementEvidenceRowMapper,
)


from src.infrastructure.persistence.schemas.billing_requirement_evidence.billing_requirement_evidence_columns import (
    BillingRequirementEvidenceColumns,
)


class GoogleSheetsBillingRequirementEvidenceRepository(
    GoogleSheetsRepository,
    BillingRequirementEvidenceRepositoryPort,
):

    TABLE_NAME = "billing_requirement_evidence"
    ID_COLUMN = BillingRequirementEvidenceColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: BillingRequirementEvidenceRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_billing_requirement_evidences(self) -> tuple[BillingRequirementEvidence, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> BillingRequirementEvidence:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
