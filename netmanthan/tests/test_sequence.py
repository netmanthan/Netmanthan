import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestSequence(netmanthanTestCase):
	def generate_sequence_name(self) -> str:
		return self._testMethodName + "_" + netmanthan.generate_hash(length=5)

	def test_set_next_val(self):
		seq_name = self.generate_sequence_name()
		netmanthan.db.create_sequence(seq_name, check_not_exists=True, temporary=True)

		next_val = netmanthan.db.get_next_sequence_val(seq_name)
		netmanthan.db.set_next_sequence_val(seq_name, next_val + 1)
		self.assertEqual(next_val + 1, netmanthan.db.get_next_sequence_val(seq_name))

		next_val = netmanthan.db.get_next_sequence_val(seq_name)
		netmanthan.db.set_next_sequence_val(seq_name, next_val + 1, is_val_used=True)
		self.assertEqual(next_val + 2, netmanthan.db.get_next_sequence_val(seq_name))

	def test_create_sequence(self):
		seq_name = self.generate_sequence_name()
		netmanthan.db.create_sequence(seq_name, max_value=2, cycle=True, temporary=True)
		netmanthan.db.get_next_sequence_val(seq_name)
		netmanthan.db.get_next_sequence_val(seq_name)
		self.assertEqual(1, netmanthan.db.get_next_sequence_val(seq_name))

		seq_name = self.generate_sequence_name()
		netmanthan.db.create_sequence(seq_name, max_value=2, temporary=True)
		netmanthan.db.get_next_sequence_val(seq_name)
		netmanthan.db.get_next_sequence_val(seq_name)

		try:
			netmanthan.db.get_next_sequence_val(seq_name)
		except netmanthan.db.SequenceGeneratorLimitExceeded:
			pass
		else:
			self.fail("NEXTVAL didn't raise any error upon sequence's end")

		# without this, we're not able to move further
		# as postgres doesn't allow moving further in a transaction
		# when an error occurs
		netmanthan.db.rollback()

		seq_name = self.generate_sequence_name()
		netmanthan.db.create_sequence(seq_name, min_value=10, max_value=20, increment_by=5, temporary=True)
		self.assertEqual(10, netmanthan.db.get_next_sequence_val(seq_name))
		self.assertEqual(15, netmanthan.db.get_next_sequence_val(seq_name))
		self.assertEqual(20, netmanthan.db.get_next_sequence_val(seq_name))
