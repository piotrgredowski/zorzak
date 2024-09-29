import enum
import pathlib
import tempfile

import arrow
import pydantic


class AnalysisFileCategory(enum.StrEnum):
    pstats = enum.auto()


class AnalysisFile(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    name: str
    category: AnalysisFileCategory
    date_uploaded: arrow.Arrow = pydantic.Field(default_factory=arrow.now)
    content: bytes

    def __repr__(self):
        return f"<{self.__repr_name__}>(name={self.name})"

    def get_date_uploaded_short(self):
        return self.date_uploaded.format("HH:mm:ss")

    def get_date_uploaded_long(self):
        return self.date_uploaded.format("YYYY-MM-DD HH:mm:ss")

    def save_to_temporary_file(self) -> pathlib.Path:
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        temp_file.write(self.content)
        return pathlib.Path(temp_file.name)
