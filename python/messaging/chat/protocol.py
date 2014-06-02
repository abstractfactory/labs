import time


class Envelope(object):
    """Over-the-wire protocol"""
    def __str__(self):
        return "(%s: %s)" % (self.author, self.payload)

    def __init__(self,
                 payload=None,
                 author=None,
                 timestamp=None,
                 recipients=None,
                 type=None,
                 trace=None):

        self.payload = payload
        self.author = author
        self.recipients = recipients
        self.timestamp = timestamp or time.time()
        self.type = type
        self.return_address = None
        self.trace = trace or list()

        if hasattr(payload, 'to_dict'):
            self.payload = payload.to_dict()

    @classmethod
    def from_dict(cls, dic):
        # dic.pop('type', None)
        envelope = cls(**dic)
        return envelope

    def to_dict(self):
        payload = self.payload
        if hasattr(payload, 'to_dict'):
            payload = payload.to_dict()

        return {
            'author': self.author,
            'recipients': self.recipients,
            'payload': payload,
            'timestamp': self.timestamp,
            'trace': self.trace,
            'type': self.type
        }


class AbstractItem(object):
    @property
    def type(self):
        return type(self).__name__.lower()

    @classmethod
    def from_dict(cls, dic):
        dic.pop('type', None)
        return dic

    def to_dict(self):
        return {
            'type': self.type
        }


class Log(AbstractItem):
    def __init__(self,
                 name=None,
                 author=None,
                 timestamp=None,
                 level=None,
                 string=None,
                 trace=None,
                 envelope=None):

        self.name = name
        self.author = author
        self.timestamp = timestamp or time.time()
        self.level = level
        self.string = string
        self.trace = trace or list()
        self.envelope = envelope

        if hasattr(envelope, 'to_dict'):
            self.envelope = envelope.to_dict()

    @classmethod
    def from_dict(cls, dic):
        dic = super(Log, cls).from_dict(dic)
        return cls(**dic)

    def to_dict(self):
        return {
            'name': self.name,
            'author': self.author,
            'timestamp': self.timestamp,
            'level': self.level,
            'string': self.string,
            'trace': self.trace,
            'envelope': self.envelope,
            'type': self.type
        }


class Query(AbstractItem):
    def __init__(self, name, questioner, payload=None):
        self.name = name
        self.questioner = questioner
        self.payload = payload

        if hasattr(payload, 'to_dict'):
            self.payload = payload.to_dict()

    @classmethod
    def from_dict(cls, dic):
        dic = super(Query, cls).from_dict(dic)
        return cls(**dic)

    def to_dict(self):
        dic = super(Query, self).to_dict()
        dic['name'] = self.name
        dic['questioner'] = self.questioner
        dic['payload'] = self.payload
        return dic

    def reply(self, peer, payload):
        return QueryResults(
            name=self.name,
            peer=peer,
            questioner=self.questioner,
            payload=payload)


class QueryResults(AbstractItem):
    def __init__(self, name, peer, questioner, payload=None):
        self.name = name  # Name or results (typically name of query)
        self.peer = peer  # Results from who?
        self.questioner = questioner  # Who's askin'?
        self.payload = payload  # The results themselves

    @classmethod
    def from_dict(cls, dic):
        # dic = super(QueryResults, cls).from_dict(dic)
        return cls(name=dic['name'],
                   peer=dic['peer'],
                   questioner=dic['questioner'],
                   payload=dic['payload'])
        # return cls(**dic)

    def to_dict(self):
        dic = super(QueryResults, self).to_dict()
        dic['name'] = self.name
        dic['peer'] = self.peer
        dic['questioner'] = self.questioner
        dic['payload'] = self.payload
        return dic


class Order(AbstractItem):
    def __init__(self,
                 item,
                 location,
                 cost,
                 status=0,
                 payment=None,
                 order_id=0):  # order_id is remapped below
        self.item = item
        self.location = location
        self.cost = cost
        self.status = status
        self.payment = payment
        self.id = order_id

    @classmethod
    def from_dict(cls, dic):
        dic = super(Order, cls).from_dict(dic)

        # Expand item
        item_dict = dic.pop('item')
        typ = item_dict['type']
        item_obj = by_name(typ).from_dict(item_dict)
        dic['item'] = item_obj

        # Remap id matching __init__ signature
        dic['order_id'] = dic.pop('id')

        order = cls(**dic)
        return order

    def to_dict(self):
        dic = super(Order, self).to_dict()
        dic.update({
            'item': self.item.to_dict(),
            'location': self.location,
            'cost': self.cost,
            'status': self.status,
            'payment': self.payment,
            'id': self.id  # Attention, this is remapped in from_dict()
        })
        return dic


class OrderId(AbstractItem):
    def __init__(self, id):
        self.id = id

    @classmethod
    def from_dict(cls, dic):
        dic = super(OrderId, cls).from_dict(dic)
        return cls(**dic)

    def to_dict(self):
        dic = super(OrderId, self).to_dict()
        dic.update({'id': self.id})
        return dic


class Item(AbstractItem):
    def __init__(self, name, quantity=1):
        self.name = name
        self.quantity = quantity

    @classmethod
    def from_dict(cls, dic):
        dic = super(Item, cls).from_dict(dic)
        return cls(**dic)

    def to_dict(self):
        dic = super(Item, self).to_dict()
        dic.update({
            'name': self.name,
            'quantity': self.quantity,
        })
        return dic


class Coffee(Item):
    def __init__(self, milk=False, size='regular', *args, **kwargs):
        super(Coffee, self).__init__(*args, **kwargs)
        self.milk = milk
        self.size = size

    def to_dict(self):
        dic = super(Coffee, self).to_dict()
        dic.update({
            'milk': self.milk,
            'size': self.size,
        })
        return dic


class Chocolate(Item):
    def __init__(self, shade='dark', *args, **kwargs):
        super(Chocolate, self).__init__(*args, **kwargs)
        self.shade = shade

    def to_dict(self):
        dic = super(Chocolate, self).to_dict()
        dic.update({'shade': self.shade})
        return dic


protocols = {
    'item': Item,
    'order': Order,
    'coffee': Coffee,
    'chocolate': Chocolate,
    'orderid': OrderId,
}


def by_name(name):
    try:
        return protocols[name.lower()]
    except IndexError:
        raise ValueError("%r not available" % name)


if __name__ == '__main__':
    item = Coffee(name='latte', quantity=1, milk=True, size='large')
    order = Order(item, location='takeaway', cost=2.10, status=0, payment=None)

    print Coffee.from_dict(item.to_dict()).to_dict()
    print Order.from_dict(order.to_dict()).to_dict()

    query = Query('stats', 'markus')
    print query