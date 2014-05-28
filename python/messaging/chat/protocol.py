import time


class Envelope(object):
    """Over-the-wire protocol"""
    def __str__(self):
        return "(%s: %s)" % (self.author, self.payload)

    def __init__(self, payload=None, author=None, recipients=None, type=None):
        self.payload = payload
        self.author = author
        self.recipients = recipients
        self.timestamp = time.time()
        self.type = type

    @classmethod
    def from_dict(cls, message):
        envelope = cls(author=message['author'],
                       payload=message['payload'],
                       recipients=message['recipients'],
                       type=message['type'])
        return envelope

    def to_dict(self):
        return {
            'type': self.type,
            'author': self.author,
            'recipients': self.recipients,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'type': self.type
        }


class AbstractItem(object):
    @classmethod
    def from_dict(cls, dic):
        dic.pop('type')
        return dic

    def to_dict(self):
        return {
            'type': type(self).__name__.lower()
        }


class Order(AbstractItem):
    def __init__(self, item, location,
                 cost, status=0, payment=None,
                 order_id=0):
        self.item = item
        self.location = location
        self.cost = cost
        self.status = status
        self.payment = payment
        self.id = order_id

    @classmethod
    def from_dict(cls, dic):
        dic = super(Order, cls).from_dict(dic)

        item = dic.pop('item')
        coffee = by_name('coffee').from_dict(item)
        dic['item'] = coffee
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
            'id': self.id
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
    def __init__(self, name, quantity=1, milk=False, size='regular'):
        self.name = name
        self.quantity = quantity
        self.milk = milk
        self.size = size

    @classmethod
    def from_dict(cls, dic):
        dic = super(Item, cls).from_dict(dic)
        return cls(**dic)

    def to_dict(self):
        dic = super(Order, self).to_dict()
        dic.update({
            'name': self.name,
            'quantity': self.quantity,
            'milk': self.milk,
            'size': self.size,
        })
        return dic


class Coffee(Item):
    def __init__(self, *args, **kwargs):
        super(Coffee, self).__init__(*args, **kwargs)


protocols = {
    'item': Item,
    'order': Order,
    'coffee': Coffee,
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
