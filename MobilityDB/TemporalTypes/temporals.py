import re
from MobilityDB.TimeTypes.period import PERIOD
from MobilityDB.TimeTypes.periodset import PERIODSET
from MobilityDB.TemporalTypes.temporalseq import TEMPORALSEQ


class TEMPORALS:
	__slots__ = ['_sequenceList']
	Duration = 4

	def __init__(self, *argv):
		self._sequenceList = []
		# Constructor with a single argument of type string
		if len(argv) == 1 and isinstance(argv[0], str):
			ps = argv[0].strip()
			if ps[0] == '{' and ps[-1] == '}':
				p = re.compile('[\[|\(].*?[^\]\)][\]|\)]')
				sequences = p.findall(ps)
				for seq in sequences:
					self._sequenceList.append(TEMPORALSEQ(seq))
			else:
				raise Exception("ERROR: Could not parse period set value")
		# Constructor with a single argument of type list
		elif len(argv) == 1 and isinstance(argv[0], list):
			# List of strings representing periods
			if all(isinstance(arg, str) for arg in argv[0]):
				for arg in argv[0]:
					self._sequenceList.append(TEMPORALSEQ(arg))
			# List of periods
			elif all(isinstance(arg, TEMPORALSEQ) for arg in argv[0]):
				for arg in argv[0]:
					self._sequenceList.append(arg)
			else:
				raise Exception("ERROR: Could not parse temporal sequence set value")
		# Constructor with multiple arguments
		else:
			# Arguments are of type string
			if all(isinstance(arg, str) for arg in argv):
				for arg in argv:
					self._sequenceList.append(TEMPORALSEQ(arg))
			# Arguments are of type temporal sequence
			elif all(isinstance(arg, TEMPORALSEQ) for arg in argv):
				for arg in argv:
					self._sequenceList.append(arg)
			else:
				raise Exception("ERROR: Could not parse temporal sequence set value")
		# Verify validity of the resulting instance
		self._valid()

	def _valid(self):
		if not all(x.endTimestamp() < y.startTimestamp() or \
			(x.endTimestamp() == y.startTimestamp() and (not x.upper_inc() or not x.lower_inc())) \
				   for x, y in zip(self._sequenceList, self._sequenceList[1:])):
			raise Exception("ERROR: The sequences must be non overlapping")
		return True

	@classmethod
	def duration(cls):
		return "SequenceSet"

	def getTime(self):
		"""
		Timestamp
		"""
		return PERIODSET([seq.period() for seq in self._sequenceList])

	def timespan(self):
		"""
		Interval
		"""
		return self.endTimestamp() - self.startTimestamp()

	def period(self):
		"""
		Period on which the temporal value is defined ignoring the potential time gaps
		"""
		return PERIOD(self.startTimestamp(), self.endTimestamp(),
			self._sequenceList[0].lower_inc, self._sequenceList[-1].upper_inc)

	def startValue(self):
		"""
		Start value
		"""
		return self._sequenceList[0].startInstant()._value

	def endValue(self):
		"""
		Start value
		"""
		return self._sequenceList[len(self._sequenceList) - 1].startInstant()._value

	def numInstants(self):
		"""
		Number of distinct instants
		"""
		return len(self.instants())

	def startInstant(self):
		"""
		Start instant
		"""
		return self._sequenceList[0].startInstant()

	def endInstant(self):
		"""
		End instant
		"""
		return self._sequenceList[len(self._sequenceList) - 1].endInstant()

	def instantN(self, n):
		"""
		N-th instant
		"""
		# 1-based
		if 0 <= n < len(self.instants()):
			return (self.instants())[n - 1]
		else:
			raise Exception("ERROR: Out of range")

	def instants(self):
		"""
		Instants
		"""
		instantList = []
		for sequence in self._sequenceList:
			for instant in sequence._instantList:
				instantList.append(instant)
		return instantList

	def numTimestamps(self):
		"""
		Number of distinct timestamps
		"""
		return len(self.timestamps())

	def startTimestamp(self):
		"""
		Start timestamp
		"""
		return self._sequenceList[0].startInstant().getTimestamp()

	def endTimestamp(self):
		"""
		End timestamp
		"""
		return self._sequenceList[len(self._sequenceList) - 1].endInstant().getTimestamp()

	def timestampN(self, n):
		"""
		N-th timestamp
		"""
		# 1-based
		if 0 <= n < len(self.timestamps()):
			return (self.timestamps())[n - 1]
		else:
			raise Exception("ERROR: Out of range")

	def timestamps(self):
		"""
		Timestamps
		"""
		timestampList = []
		for sequence in self._sequenceList:
			for instant in sequence._instantList:
				timestampList.append(instant.getTimestamp())
		# Remove duplicates
		timestampList = list(dict.fromkeys(timestampList))
		return timestampList

	def numSequences(self):
		"""
		Number of sequences
		"""
		return len(self._sequenceList)

	def startSequence(self):
		"""
		Start sequence
		"""
		return self._sequenceList[0]

	def endSequence(self):
		"""
		End sequence
		"""
		return self._sequenceList[len(self._sequenceList) - 1]

	def sequenceN(self, n):
		"""
		N-th sequence
		"""
		# 1-based
		if 0 <= n < len(self._sequenceList):
			return self._sequenceList[n - 1]
		else:
			raise Exception("ERROR: Out of range")

	def sequences(self):
		"""
		Sequences
		"""
		return self._sequenceList

	def __str__(self):
		return "{{{}}}".format(', '.join('{}'.format(sequence.__str__().replace("'", ""))
			for sequence in self._sequenceList))
