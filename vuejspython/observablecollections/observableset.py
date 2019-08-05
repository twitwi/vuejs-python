from .observable import Observable

class ObservableSet(Observable, set):

	def __init__(self, *args, **kwargs):
		Observable.__init__(self)
		set.__init__(self, kwargs)

	def add(self, item):
		if item not in self:
			set.add(self, item)
			self.raiseEvent('itemsAdded', items=[item])

	def remove(self, item):
		set.remove(self, item)
		self.raiseEvent('itemsRemoved', items=[item])

	def discard(self, item):
		if item not in self:
			set.discard(self, item)
			self.raiseEvent('itemsRemoved', items=[item])

	def pop(self):
		item = set.pop(self)
		self.raiseEvent('itemsRemoved', items=[item])

	def __isub__(self, other):
		self.difference_update(self, other)
		return self

	def __ixor__(self, other):
		self.symmetric_difference_update(other)
		return self

	def __iand__(self, other):
		self.intersection_update(other)
		return self

	def __ior__(self, other):
		self.update(other)
		return self

	def difference_update(self, *args):
		for arg in args:
			difference = self.difference(arg)

		self._update(difference)

	def symmetric_difference_update(self, other):
		symmetric_difference = self.symmetric_difference(other)
		self._update(symmetric_difference)

	def intersection_update(self, *args):
		for arg in args:
			newSet = set.intersection(self, arg)

		self._update(newSet)

	def update(self, *args):
		for arg in args:
			newSet = set.union(self, arg)

		self._update(newSet)

	def clear(self):
		if (len(self) > 0):
			removedItems = []

			for item in self:
				removedItems.append(item)

			set.clear(self)
			self.raiseEvent('itemsRemoved', items=[removedItems])

	def _update(self, set2):
		elemsAdded = []
		elemsRemoved = []

		added = set2 - self
		for elem in added:
			elemsAdded.append(elem)
			set.add(self, elem)

		removed = self - set2
		for elem in removed:
			elemsRemoved.append(elem)
			set.remove(self, elem)

		if(len(elemsAdded) > 0):
			self.raiseEvent('itemsAdded', items=elemsAdded)

		if (len(elemsRemoved) > 0):
			self.raiseEvent('itemsRemoved', items=elemsRemoved)
