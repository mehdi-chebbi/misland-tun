import enum

class KeyValueBaseEnum(enum.Enum):
	"""Enumeration for items with key and label properties
	"""
	@property
	def key(self):
		return self.value[0]

	@property
	def label(self):
		return self.value[1]

class SMSApprovalStatusEnum(enum.Enum):
	"""
	Enumeration for SMS approval status. 
	"""
	PENDING = "Pending" # SMS is yet to be reviewed
	APPROVED = "Approved" # SMS was found to contain genuine complaint etc
	REJECTED = "Rejected" # SMS was rejected due to a number of reasons

class SMSSentStatusEnum(enum.Enum):
	"""
	Enumeration for SMS sent status. 
	"""
	PENDING = "Pending" # SMS is yet to be sent
	SENT = "Sent" # SMS was successfully sent
	FAILED = "Failed" # SMS was not sent due to a number of reasons
	
# class IssueCategoryEnum(KeyValueBaseEnum):
# 	"""
# 	Enumeration for specific issue type categorization 
# 	"""
# 	LABOR = (1, _("Labor/Non-payment by contractors"))
# 	OHS = (2, _("Occupational Health and Safety (OHS) claims and compensation"))
# 	INTERRUPTION = (3, _("Interruption of services (water/electricity)"))
# 	BLOCKAGE = (4, _("Blockage of access to facilities (Schools, Homes, Business premises)"))
# 	HAZARD = (5, _("Safety/Hazard"))
# 	NON_COMPENSATION = (6, _("Non-compensation of PAPs by KISIP"))
# 	FEEDBACK = (7, _("Non-completion of projects"))
# 	FEEDBACK = (8, _("Substandard work (i.e. faulty floodlights)"))
# 	FEEDBACK = (9, _("Fatality Cases"))
# 	FEEDBACK = (10, _("Corruption"))
# 	FEEDBACK = (11, _("Damage to property and loss of livelihood Labor"))
# 	FEEDBACK = (12, _("Other"))

# class IssueTypeEnum(enum.Enum):
# 	"""
# 	Enumeration for broad issue categorization 
# 	"""
# 	COMPLAINT = "Complaint" 
# 	APPRECIATION = "Appreciation"
# 	QUESTION = "Question" 
# 	SUGGESTION = "Suggestion"
# 	FEEDBACK = "Feedback"

class SMSTypeEnum(enum.Enum):
	"""
	Enumeration for different SMS types
	"""
	ACKNOWLEDGEMENT = "Acknowledgment" #Acknowledgement e.g confirm to user that SMS has been received
	ALERT = "Alert" # Alerts sent to different system users

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
	PUSH = "Push Notification"