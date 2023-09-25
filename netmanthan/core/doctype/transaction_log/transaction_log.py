# Copyright (c) 2021, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import hashlib

import netmanthan
from netmanthan.model.document import Document
from netmanthan.query_builder import DocType
from netmanthan.utils import cint, now_datetime


class TransactionLog(Document):
	def before_insert(self):
		index = get_current_index()
		self.row_index = index
		self.timestamp = now_datetime()
		if index != 1:
			prev_hash = netmanthan.get_all(
				"Transaction Log", filters={"row_index": str(index - 1)}, pluck="chaining_hash", limit=1
			)
			if prev_hash:
				self.previous_hash = prev_hash[0]
			else:
				self.previous_hash = "Indexing broken"
		else:
			self.previous_hash = self.hash_line()
		self.transaction_hash = self.hash_line()
		self.chaining_hash = self.hash_chain()
		self.checksum_version = "v1.0.1"

	def hash_line(self):
		sha = hashlib.sha256()
		sha.update(
            netmanthan.safe_encode(str(self.row_index))
            + netmanthan.safe_encode(str(self.timestamp))
            + netmanthan.safe_encode(str(self.data))
		)
		return sha.hexdigest()

	def hash_chain(self):
		sha = hashlib.sha256()
		sha.update(
            netmanthan.safe_encode(str(self.transaction_hash)) + netmanthan.safe_encode(str(self.previous_hash))
		)
		return sha.hexdigest()


def get_current_index():
	series = DocType("Series")
	current = (
		netmanthan.qb.from_(series).where(series.name == "TRANSACTLOG").for_update().select("current")
	).run()

	if current and current[0][0] is not None:
		current = current[0][0]

		netmanthan.db.sql(
			"""UPDATE `tabSeries`
			SET `current` = `current` + 1
			where `name` = 'TRANSACTLOG'"""
		)
		current = cint(current) + 1
	else:
		netmanthan.db.sql("INSERT INTO `tabSeries` (name, current) VALUES ('TRANSACTLOG', 1)")
		current = 1
	return current
