from webFiles import app, models, db
from flask import request, json, jsonify, Response
from sqlalchemy import exc, asc, desc
from sqlalchemy.sql import select
import sys
import string
import traceback

# IN:  Quantity (int)
#      Price (float)
#      Use the buy DB instead of the sell DB (bool)
# OUT: None
# RET: String indicating the add results.
def addDataToDB(inQty, inPrc, useBuyDB):
    """
    Attempt to add some data to the buy/sell DBs. The code sanity checks on the
    JSON string. It assumes you've already checked for validity!
    """

    # The spec doesn't define what to do if there's already a buy/sell in the
    # DB. We'll assume that multiple adds are allowed, as the idea of "pooling"
    # buys/sells doesn't seem right.

    # Add an entry to the DB. If returned string is empty, assume success.
    retStr = ''
    if useBuyDB == True:
        addObj = models.buyDB(qty=inQty, prc=inPrc)
    else:
        addObj = models.sellDB(qty=inQty, prc=inPrc)
    db.session.add(addObj)
    try:
        db.session.commit()
        retStr = 'Added qty=%d prc=%f to %s' % \
            (inQty, inPrc, 'Buy DB' if useBuyDB else 'Sell DB')
    except exc.OperationalError:
        return 'Database does not exist! Data not added.\n'
    except:
        return 'Unknown Database Error! Data not added. Error = %s\n' % \
            sys.exc_info()[0]
    finally:
        # Log whatever happened for debug purposes.
        print 'DEBUG (addDataToDB): %s' % retStr
        retStr = ''

    return retStr


# IN:  Use the buy DB instead of the sell DB (bool)
# OUT: None
# RET: List with the buyDB or sellDB objects found in the DB after a query.
def queryDB(useBuyDB):
    """
    Returns the contents of the buy or sell DBs, sorted by price (buy in
    descending order, sell in ascending order) and, secondarily, by order of
    insertion into the DB.
    """

    # Secondary ID sort is just insurance. Code assumes first-come first-served
    # when dealing with the DB.
    if useBuyDB == True:
        dbQuery = models.buyDB.query.order_by(desc(models.buyDB.prc), \
                                              asc(models.buyDB.id)).all()
    else:
        dbQuery = models.sellDB.query.order_by(asc(models.sellDB.prc), \
                                               asc(models.sellDB.id)).all()

    return dbQuery


# IN:  None
# OUT: None
# RET: None
@app.route('/')
def index():
    """
    Return a "Hello, World!" message alongside a little ray of sunshine.
    """
    return "Hello, you big, beautiful world. Go get 'em!"


# IN:  None
# OUT: None
# RET: None
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    """
    Handles the case when a buy order comes in. Incoming order must include the
    quantity (int) and buy price (float) in JSON format.
    """

    # The headers must contain "Content-Type: application/json" or the data
    # won't be added to the DB.
    if request.json == None:
        return "Request type is not JSON! mimetype = %s\n" % request.mimetype

    # Search sell DB for the lowest price that can be bought and buy it if at or
    # below the buy price. If seller's quantity runs out, go to next highest,
    # etc. Stay at or below the buy price. If there are still any buys remaining
    # at the end, pop the remaining buy order into the buy DB.
    retStr = ''
    if request.method == 'POST':
        # Make sure JSON is properly formatted first.
        try:
            inQty = request.json["qty"]
            inPrc = request.json["prc"]
        except KeyError:
            return 'Incoming buy order doesn\'t contain quantity and price!\n'

        # Process the order.
        sellRes = queryDB(False)
        if len(sellRes) > 0:
            for sellOrder in sellRes:
                if sellOrder.prc <= inPrc:
                    if sellOrder.qty <= inQty: # Buy order partially filled.
                        inQty -= sellOrder.qty
                        db.session.delete(sellOrder)
                        db.session.commit()
                    else:                      # Buy order completely filled.
                        sellOrder.qty -= inQty
                        db.session.commit()
                        inQty = 0

                    if inQty == 0:
                        break
                else:   # No more appropriate sell orders.
                    break

        # If there's any outstanding buy qty, add to buy DB.
        if inQty != 0:
            retStr = addDataToDB(inQty, inPrc, True)
        return retStr
    else:
        # In theory, you could do something here for GET. We won't for now.
        pass

    return retStr


# IN:  None
# OUT: None
# RET: None
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    """
    Handles the case when a sell order comes in. Incoming order must include the
    quantity (int) and sell price (float) in JSON format.
    """

    # The headers must contain "Content-Type: application/json" or the data
    # won't be added to the DB.
    if request.json == None:
        return "Request type is not JSON! mimetype = %s\n" % request.mimetype

    # Search buy DB for the lowest price that can be sold and sell it if at or
    # above the sell price. If buyer's quantity runs out, go to next lowest,
    # etc. Stay at or above the sell price. If there are still any sells
    # remaining at the end, pop the remaining sell order into the sell DB.
    retStr = ''
    if request.method == 'POST':
        # Make sure JSON is properly formatted first.
        try:
            inQty = request.json["qty"]
            inPrc = request.json["prc"]
        except KeyError:
            return 'Incoming sell order doesn\'t contain quantity and price!\n'

        # Process the order.
        buyRes = queryDB(True)
        if len(buyRes) > 0:
            for buyOrder in buyRes:
                if buyOrder.prc >= inPrc:
                    if buyOrder.qty <= inQty: # Sell order partially filled
                        inQty -= buyOrder.qty
                        db.session.delete(buyOrder)
                        db.session.commit()
                    else:                     # Sell order completely filled
                        buyOrder.qty -= inQty
                        db.session.commit()
                        inQty = 0

                    if inQty == 0:
                        break
                else:   # No more appropriate buy orders.
                    break

        # If there's any outstanding sell qty, add to sell DB.
        if inQty != 0:
            retStr = addDataToDB(inQty, inPrc, False)
    else:
        # In theory, you could do something here for GET. We won't for now.
        pass

    return retStr


# IN:  None
# OUT: None
# RET: None
@app.route('/book', methods=['GET'])
def book():
    """
    Returns the buy and sell DB contents, sorted (buy orders in descending
    price, sell orders in ascending price).
    """

    # Get everything from the buy & sell DBs, then return as JSON data.
    buyRes = queryDB(True)
    sellRes = queryDB(False)
    buyList = [{"qty": x.qty, "prc": x.prc} for x in buyRes]
    sellList = [{"qty": y.qty, "prc": y.prc} for y in sellRes]

    # Python sometimes rearranges the order of "qty" and "prc" in the list
    # dictionaries. Python makes it very difficult to work around this, so we
    # won't worry about it for now.
    return jsonify(buys=buyList, sells=sellList)
