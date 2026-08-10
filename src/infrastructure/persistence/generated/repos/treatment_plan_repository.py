# repository.py.tpl


# AUTO GENERATED

from src.application.ports.treatment_plan_repository_port import (
    TreatmentPlanRepositoryPort,
)

from src.domain.entities.treatment_plan_entities import (
    TreatmentPlan,
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

from src.infrastructure.persistence.mappers.treatment_plan.treatment_plan_row_mapper import (
    TreatmentPlanRowMapper,
)


from src.infrastructure.persistence.schemas.treatment_plan.treatment_plan_columns import (
    TreatmentPlanColumns,
)


class GoogleSheetsTreatmentPlanRepository(
    GoogleSheetsRepository,
    TreatmentPlanRepositoryPort,
):

    TABLE_NAME = "treatment_plan"
    ID_COLUMN = TreatmentPlanColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: TreatmentPlanRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_treatment_plans(self) -> tuple[TreatmentPlan, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> TreatmentPlan:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
