class SatQueryException(Exception):
    """Base exception class for all SatQuery AI domain errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class QueryParsingError(SatQueryException):
    """Raised when a natural language query cannot be parsed into valid structured intent."""
    def __init__(self, message: str):
        super().__init__(message=message, code="QUERY_PARSING_ERROR", status_code=400)

class InvalidGeometryError(SatQueryException):
    """Raised when coordinates, bounding boxes, or polygons are geographically invalid."""
    def __init__(self, message: str):
        super().__init__(message=message, code="INVALID_GEOMETRY", status_code=400)

class InvalidBoundingBoxError(InvalidGeometryError):
    """Raised when bounding box coordinates exceed valid latitude/longitude bounds."""
    pass

class InvalidDateRangeError(QueryParsingError):
    """Raised when start date occurs after end date."""
    pass

class SatelliteDataUnavailableError(SatQueryException):
    """Raised when satellite scenes or required spectral bands cannot be accessed."""
    def __init__(self, message: str):
        super().__init__(message=message, code="SATELLITE_DATA_UNAVAILABLE", status_code=404)

class InsufficientEvidenceError(SatQueryException):
    """Raised when evidence quality (cloud cover, valid pixels, spatial coverage) is inadequate."""
    def __init__(self, message: str):
        super().__init__(message=message, code="INSUFFICIENT_EVIDENCE", status_code=422)

class ClaimValidationError(SatQueryException):
    """Raised when a generated claim cites invalid evidence IDs or makes unsupported causal leaps."""
    def __init__(self, message: str):
        super().__init__(message=message, code="CLAIM_VALIDATION_ERROR", status_code=422)

class StorageError(SatQueryException):
    """Raised when metadata DB or tile object storage operations fail."""
    def __init__(self, message: str):
        super().__init__(message=message, code="STORAGE_ERROR", status_code=500)

class RetrievalError(SatQueryException):
    """Raised when spatial/temporal filtering or vector re-ranking fails."""
    def __init__(self, message: str):
        super().__init__(message=message, code="RETRIEVAL_ERROR", status_code=500)

class ModelError(SatQueryException):
    """Raised when external LLM/VLM provider fails or times out."""
    def __init__(self, message: str):
        super().__init__(message=message, code="MODEL_ERROR", status_code=502)
