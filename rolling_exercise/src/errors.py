class InvalidCsvFileError(Exception):
    """The uploaded file can't be used, so none of its rows are saved."""


class InvalidRowError(Exception):
    """A row of the uploaded file can't be used, so only that row is rejected."""
