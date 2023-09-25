import netmanthan


def execute():
	netmanthan.reload_doctype("Translation")
	netmanthan.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
