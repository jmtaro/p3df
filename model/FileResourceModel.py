# -*- coding: utf-8 -*-

import os
from twisted.python import log

def putRawData(filepath, data):
    try:
        dir = os.path.dirname(filepath)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(filepath, 'wb') as f:
            f.write(data)
    except Exception, e:
        #todo: raise error properly for this model
        raise e

# private

def info(*args):
    log.msg( "[FileResourceModel]%s" % ":".join( str(arg) for arg in args ) )
def warn(*args):
    info('[warning]', *args)

