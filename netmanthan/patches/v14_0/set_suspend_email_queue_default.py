import netmanthan
from netmanthan.cache_manager import clear_defaults_cache


def execute():
	netmanthan.db.set_default(
		"suspend_email_queue",
        netmanthan.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	netmanthan.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
