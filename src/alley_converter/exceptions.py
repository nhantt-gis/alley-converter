"""Domain-specific exceptions raised by the converter."""


class AlleyConverterError(Exception):
    """Base class for user-facing converter errors."""


class MissingGeometryColumnError(AlleyConverterError):
    """Raised when a CSV does not contain the configured geometry column."""


class NoInputFilesError(AlleyConverterError):
    """Raised when the input directory contains no CSV files."""


class NoValidCsvError(AlleyConverterError):
    """Raised when all CSV files are skipped."""


class LayerNameConflictError(AlleyConverterError):
    """Raised when the combined layer name conflicts with an input layer name."""
