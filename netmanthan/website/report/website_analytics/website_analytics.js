// Copyright (c) 2016, netmanthan Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

netmanthan.query_reports["Website Analytics"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: netmanthan.datetime.add_days(netmanthan.datetime.now_date(true), -100),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: netmanthan.datetime.now_date(true),
		},
		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: [
				{ value: "Daily", label: __("Daily") },
				{ value: "Weekly", label: __("Weekly") },
				{ value: "Monthly", label: __("Monthly") },
			],
			default: "Daily",
			reqd: 1,
		},
	],
};
