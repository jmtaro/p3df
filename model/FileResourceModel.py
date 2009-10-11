# -*- coding: utf-8 -*-

import os
import __init__ as model

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

info, warn, error = model.logging('[FileResourceModel]')

