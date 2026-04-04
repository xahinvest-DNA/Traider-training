class ReplayBootstrapError(Exception):
    pass


class DatasetNotFoundError(ReplayBootstrapError):
    pass


class InvalidManifestError(ReplayBootstrapError):
    pass


class EmptyTickStreamError(ReplayBootstrapError):
    pass


class OutOfBoundsSeekError(ReplayBootstrapError):
    pass


class ReplayFinishedError(ReplayBootstrapError):
    pass


class CorruptedMetadataError(ReplayBootstrapError):
    pass


class UnsupportedSchemaVersionError(ReplayBootstrapError):
    pass


class ModeRestrictionError(ReplayBootstrapError):
    pass


class DatasetImportError(ReplayBootstrapError):
    pass


class TradingLoopError(Exception):
    pass


class InvalidTradeCommandError(TradingLoopError):
    pass


class ActiveTradeExistsError(TradingLoopError):
    pass


class NoActivePositionError(TradingLoopError):
    pass


class TradingModeRestrictionError(TradingLoopError):
    pass


class JournalRuntimeError(Exception):
    pass


class InvalidJournalValueError(JournalRuntimeError):
    pass


class SessionFinalizationError(JournalRuntimeError):
    pass
