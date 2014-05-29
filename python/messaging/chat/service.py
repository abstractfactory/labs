from __future__ import absolute_import

import time
import lib

orders = {}


def order_coffee(order):
    """Order a coffee

    Place an order for a coffee; your options are:
        - Latte
        - Cappucino

    Usage:
        > order coffee latte --no-milk
        > order coffee cappucino --milk --quantity 2

    """

    time.sleep(0.2)  # Ordering coffee takes time.

    item = order.item

    types = ('cappucino', 'latte', 'frappe')
    sizes = ('large', 'regular', 'small')

    if not item.name in types:
        raise ValueError("Sorry, we don't have '%s'" % item.name)

    if not item.size in sizes:
        raise ValueError("Sorry, we can't make the size '%s'" % item.size)

    order_id = 0
    while order_id in orders:
        order_id += 1

    orders[order_id] = order

    order.status = 'ordered'
    order.id = order_id

    lib.spawn(make_coffee, args=[order], name='order: %s' % order_id)

    print "Id: %s" % order_id

    return order


def order_chocolate(order):
    """Order a chocolate

    Place an order for a chocolate; your options are:
        - Dark
        - White

    Usage:
        > order chocolate --dark
        > order chocolate --white --quantity 2

    """

    order_id = 0
    while order_id in orders:
        order_id += 1

    orders[order_id] = order

    order.status = 'served'  # Chocolate is self-serve
    order.id = order_id

    return order


def make_coffee(order):
    order.status = 'being prepared'
    time.sleep(10)
    order.status = 'in progress'
    time.sleep(30)
    order.status = 'served'


services = {
    'order_coffee': order_coffee,
    'order_chocolate': order_chocolate
}


def by_name(name):
    try:
        return services[name]
    except IndexError:
        raise ValueError("%r not available" % name)
