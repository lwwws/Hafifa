from pydantic import BaseModel

from src.models.rejected_row import RejectedRow
from src.models.valid_row import ValidRow


class ParsedUpload(BaseModel):
    valid_rows: list[ValidRow]
    rejected_rows: list[RejectedRow]
