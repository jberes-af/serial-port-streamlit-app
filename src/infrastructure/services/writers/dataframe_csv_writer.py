# /src/infrastructure/services/writers/dataframe_csv_writer.py

from pathlib import Path

import pandas as pd


class DataFrameCsvWriter:
    def write(
        self,
        dataframe: pd.DataFrame,
        *,
        output_path: Path,
    ) -> Path:
        output_path = output_path.resolve()

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )

        return output_path