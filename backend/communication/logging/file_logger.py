# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from django.conf import settings
from pathlib import Path

error_log = "error.log"
"""
Level of severity in increasing severity order
    DEBUG
    INFO
    WARNING
    ERROR
    CRITICAL
"""
def get_file_path(filename):
	#path = settings.BASE_DIR.parent # Get parent directory
	path = Path(__file__).resolve().parent.parent # Get app directory
	logs_path = str(path) + "/logs"
	if not os.path.exists(logs_path):
		os.mkdir(logs_path)
	return logs_path + "/" + filename

def get_logger(filename):	

	def get_weekly_logger():
		logger = logging.getLogger("Rotating Log")
		logger.setLevel(logging.INFO)

		handler = TimedRotatingFileHandler(get_file_path(filename),
										when="w0", #every monday
										interval=1,
										backupCount=0)
		logger.addHandler(handler)
		return logger

	def get_size_based_logger():
		handler = RotatingFileHandler(
					get_file_path(filename),
					maxBytes=20*1024*1024, #set to 20mb max size					
					backupCount=300 #set this to 0 to stop deleting of log files
				)
		handler.setFormatter(formatter)
		logger = logging.getLogger(filename) # __name__)
		logger.setLevel(logging.DEBUG) #All events at or above DEBUG level will now get logged)
		logger.addHandler(handler)
		logger.propagate = False
		return logger
	
	#formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(pathname)s:\n%(message)s')
	formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(message)s')
	# # handler = logging.StreamHandler()	
	logger = get_size_based_logger() # get_weekly_logger()
	return logger

def config_logger(filename):
	#All events at or above DEBUG level will now get logged
	logging.basicConfig(
		level=logging.DEBUG,#All events at or above DEBUG level will now get logged
		filename=get_file_path(filename),
		format='[%(levelname)s] %(asctime)s | %(message)s;'
	)

def log_message(message, filename):
	#config_logger(filename)
	#logging.info(message)
	logger = get_logger(filename)
	logger.info(message)

def log_error(error, filename=error_log):
	# config_logger(filename)
	# #logging.error(error, exc_info=True)
	# logging.exception(error)
	logger = get_logger(filename)
	logger.exception(error)

def test_log():
	logging.debug('This is a debug message')
	logging.info('This is an info message')
	logging.warning('This is a warning message')
	logging.error('This is an error message')
	logging.critical('This is a critical message')

