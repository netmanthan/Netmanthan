"""
Run this after updating country_info.json and or
"""
import netmanthan


def execute():
	for col in ("field", "doctype"):
		netmanthan.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
