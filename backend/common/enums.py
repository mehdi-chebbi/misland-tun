from enum import Enum

class CommunicationSentStatusEnum(Enum):
    """Enumeration for communication sent status
    """
    SENT = "Sent"
    PENDING = "Pending"
    FAILED = "Failed"

class CommunicationChannelTypeEnum(Enum):
    """Enumeration for communication types status
    """
    EMAIL = "EMAIL"
    SMS = "SMS"