from typing import Annotated

from pydantic import StringConstraints

CityName = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=1)]
