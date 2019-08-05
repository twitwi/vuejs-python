from .event import Event
from .observable import Observable
from .collections import namedtuple

class ObservableDict(dict, Observable):
	_itemTuple = namedtuple('item', 'key value')
	_itemChangedTuple = namedtuple('item', 'key value oldValue')

	def __init__(self, *args, **kwargs):
		Observable.__init__(self)
		dict.__init__(self, *args, **kwargs)

	def popitem(self):
		keyValue = dict.popitem(self)
		self.raiseEvent('itemsRemoved', items=[self._createItemTuple(keyValue[0], keyValue[1])])
		return keyValue

	def pop(self, key, default=None):
		value = dict.pop(self, key, default)
		self.raiseEvent('itemsRemoved', items=[self._createItemTuple(key, value)])
		return value

	def __setitem__(self, key, value):
		oldValue = dict.get(self, key)

		dict.__setitem__(self, key, value)
		item = self._createItemTuple(key, value, oldValue)

		if (oldValue != None):
			actionName = 'itemsUpdated'
		else:
			actionName = 'itemsAdded'

		self.raiseEvent(actionName, items=[item])

	def __delitem__(self, key):
		value = dict.__getitem__(self, key)
		dict.__delitem__(self, key)
		self.raiseEvent('itemsRemoved', items=[ self._createItemTuple(key, value) ])

	def update(self, dict2):
		itemsAdded = []
		itemsChanged = []

		for keyValue in dict2.items():
			key = keyValue[0]
			value = keyValue[1]

			currValue = dict.get(self, key)

			if currValue == None:
				dict.__setitem__(self, key, value)
				itemsAdded.append(self._createItemTuple(key, value))
			elif currValue != value:
				dict.__setitem__(self, key, value)
				itemsChanged.append(self._createItemTuple(key, value, oldValue))

		if len(itemsAdded) > 0:
			self.raiseEvent('itemsAdded', items=itemsAdded)

		if len(itemsChanged) > 0:
			self.raiseEvent('itemsUpdated', items=itemsChanged)

	def clear(self):
		itemsRemoved = []
		items = self.items()

		for item in items:
			itemsRemoved.append(self._createItemTuple(item[0], item[1]))
			dict.__delitem__(self, item[0])

		self.raiseEvent('itemsRemoved', items=itemsRemoved)

	def _createItemTuple(self, key, value, oldValue=None):

		if oldValue == None:
			item = self._itemTuple(key=key, value=value)
		else:
			item = self._itemChangedTuple(key=key, value=value, oldValue=oldValue)
		return item
