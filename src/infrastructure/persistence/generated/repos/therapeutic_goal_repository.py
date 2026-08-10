# repository.py.tpl


# AUTO GENERATED

from src.application.ports.therapeutic_goal_repository_port import (
    TherapeuticGoalRepositoryPort,
)

from src.domain.entities.therapeutic_goal_entities import (
    TherapeuticGoal,
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

from src.infrastructure.persistence.mappers.therapeutic_goal.therapeutic_goal_row_mapper import (
    TherapeuticGoalRowMapper,
)


from src.infrastructure.persistence.schemas.therapeutic_goal.therapeutic_goal_columns import (
    TherapeuticGoalColumns,
)


class GoogleSheetsTherapeuticGoalRepository(
    GoogleSheetsRepository,
    TherapeuticGoalRepositoryPort,
):

    TABLE_NAME = "therapeutic_goal"
    ID_COLUMN = TherapeuticGoalColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: TherapeuticGoalRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_therapeutic_goals(self) -> tuple[TherapeuticGoal, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> TherapeuticGoal:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
