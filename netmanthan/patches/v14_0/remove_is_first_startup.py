import netmanthan


def execute():
	singles = netmanthan.qb.Table("tabSingles")
	netmanthan.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
