from django.utils.translation import gettext as _
from django.conf import settings
import datetime

def validate_years(start_year, end_year, both_valid=True):
	"""
	Validate the start and end periods

	Args:
		start_year (int): Start year
		end_year (int): End year
		both_valid (bool): If True, both years will be validated
	Returns:
		tuple (start_year, end_year, error)
	"""		

	# Validate that at least one period is specified
	if not start_year and not end_year:
		return (None, None, _("Select at least one period to analyse")) 

	# convert the years into integers
	start_year = cint(start_year) if start_year else None
	end_year = cint(end_year) if end_year else None

	# check start must be earlier than end
	if start_year and end_year:
		if start_year > end_year:
			return (None, None, _("Start period must be earlier than the end period"))

	if both_valid:
		if start_year and end_year:
			if start_year > end_year:
				return (None, None, _("Start period must be earlier than the end period"))
		else:
			return (None, None, _("Start period and end period must both be specified"))
	else:
		# If either is null, assign to the value of the other non-null
		start_year = start_year if start_year else end_year
		end_year = end_year if end_year else start_year
	return (start_year, end_year, None)

def validate_dates(start_date, end_date, both_valid=True):
	"""
	Validate the start and end dates

	Args:
		start_date (string or date): Start year
		end_date (string or date): End year
		both_valid (bool): If True, both dates will be validated
	Returns:
		tuple (start_date, end_date, error)
	"""		

	# Validate that at least one period is specified
	if not start_date and not end_date:
		return (None, None, _("Select at least one period to analyse")) 

	# convert the years into integers
	start_date = parse_date(start_date) if start_date else None
	end_date = parse_date(end_date) if end_date else None

	# check start must be earlier than end
	if start_date and end_date:
		if start_date > end_date:
			return (None, None, _("Start date must be earlier than the end date"))

	if both_valid:
		if start_date and end_date:
			if start_date > end_date:
				return (None, None, _("Start date must be earlier than the end date"))
		else:
			return (None, None, _("Start date and end date must both be specified"))
	else:
		# If either is null, assign to the value of the other non-null
		start_date = start_date if start_date else end_date
		end_date = end_date if end_date else start_date
	return (start_date, end_date, None)

def format_date(dt, fmt="%Y-%m-%d"):
	return datetime.datetime.strftime(dt, fmt)

def parse_date(dt, fmt="%Y-%m-%d"):
	if not dt:
		return None
	if isinstance(dt, datetime.datetime):
		return dt
	return datetime.datetime.strptime(dt, fmt) 

def days_between_dates(start_date, end_date):
	"""
	Get days between dates
	"""
	diff = parse_date(end_date).date() - parse_date(start_date).date()
	return diff.days

def cint(s):
	from common.utils.common_util import cint
	return cint(s)