# /src/infrastructure/services/writers/dataframe_console_writer.py

import pandas as pd


class DataFrameConsoleWriter:
    def write(
        self,
        dataframe: pd.DataFrame,
        *,
        title: str | None = None,
    ) -> None:
        if title:
            print()
            print(title)
            print("=" * len(title))

        if dataframe.empty:
            print("[No records]")
            return

        print(
            dataframe.to_string(
                index=False,
            )
        )