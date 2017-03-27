import json
import requests
import logging
import time

logger = logging


def _requestX(url, headers=None, post=False, data=None, jsonData=None, params=None, verify=False, retry=1):
    meta = {"verify": verify}
    if data is not None:
        meta["data"] = data
    if jsonData is not None:
        meta["json"] = jsonData
    if params is not None:
        meta["params"] = params

    # print meta
    for i in xrange(retry):
        try:
            if post:
                r = requests.post(url, **meta)
            else:
                r = requests.get(url, **meta)
            res = json.loads(r.content)
            break
        except Exception as e:
            logger.error("%s\n%s" % (str(e), traceback.format_exc()))
            time.sleep(20 * (i + 1))
    else:
        raise Exception("Tried timeout")
    return res

def saveData(file, data):
    try:
        dump = json.dumps(data)
        with open(file, "w+b") as f:
            f.write(dump)
    except Exception as e:
        logger.error(str(e))
