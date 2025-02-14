# Generated by Django 3.1 on 2022-03-30 06:19

from django.db import migrations
from django.db import connection
from django.apps import apps

src_prefix="ldms"
dest_prefix="common"

def forwards(apps, schema_editor):
	changed_tables = [
		   'CommonSettings'
	   ]
	same_tables = [
		'Gallery',
		'Topic',
		'Question',
	   ] 
	tables_lst = []
	tables_lst += changed_tables
	tables_lst += same_tables

	# reset SEQUENCE for the common_gis models that have imported data from the old tables
	# get max id from table
	for tbl in tables_lst:
		with connection.cursor() as cursor: 
			cursor.execute("SELECT id FROM {0}_{1} ORDER BY ID DESC LIMIT 1".format(dest_prefix, tbl))
			row = cursor.fetchone()
			if row:
				max_id = row[0]
				cursor.execute("ALTER SEQUENCE {0}_{1}_id_seq RESTART WITH {2};".format(dest_prefix, tbl.lower(), max_id+1))
	
def backwards(apps, schema_editor):
	pass

def exec_sql(sql):
	with connection.cursor() as cursor:
		cursor.execute(sql) 
	
class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_communicationlog'),
    ]

    operations = [
         migrations.SeparateDatabaseAndState(
		   [
			   migrations.RunPython(forwards, backwards)
		   ]
	   )
    ]

