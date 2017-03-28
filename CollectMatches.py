import json
from datetime import datetime
import time
import logging
import Util
from vaingloryai import parseConfig

logger = logging


class Collector(object):
    MATCHES = 0
    OFFSET = 641

    @classmethod
    def setup(cls, config):
        cls.URL = config.get("vainglory", "api_url")
        cls.Key = config.get("vainglory", "api_key")
        cls.MATCH_DIR = config.get("vainglory", "match_dir")

    @classmethod
    def requestMC(cls, offset):
        payload = {
            "page[offset]": offset,
            "page[limit]": 5
        }

        headers = {"Authorization": "Bearer " + cls.Key,
                           "X-TITLE-ID": "semc-vainglory",
                           "Accept": "application/vnd.api+json"}
        mc = Util._requestX(cls.URL, params=payload, headers=headers, retry=30)
        # mc = json.loads(res)
        return mc
		
    @classmethod
    def requestLastMatches(cls, playerName, count=10):
        payload = {
            "page[limit]": count,
			"filter[playerName]": playerName,
			"sort": "-createdAt",
			"filter[createdAt-start]": "2017-01-01T00:00:00Z"
        }

        headers = {"Authorization": "Bearer " + cls.Key,
                           "X-TITLE-ID": "semc-vainglory",
                           "Accept": "application/vnd.api+json"}
        mc = Util._requestX(cls.URL, params=payload, headers=headers, retry=2)
        return mc		

    @classmethod
    def saveMatches(cls, mc):
        metas = {"participant": {}, "roster": {}, "player": {}}

        for i in mc["included"]:
            if i["type"] not in metas.keys():
                metas[i["type"]] = {}
            metas[i["type"]][i["id"]] = i

        # print json.dumps(metas)

        for r in metas["roster"]:
            metas["roster"][r]["participants"] = {}

            paIds =[i["id"] for i in metas["roster"][r]["relationships"]["participants"]["data"]]
            for paId in paIds:
                pId = metas["participant"][paId]["relationships"]["player"]["data"]["id"]
                player = metas["player"][pId]
                metas["participant"][paId]["player"] = player
                metas["roster"][r]["participants"][paId] = metas["participant"][paId]

            metas["roster"][r]["winner"] = metas["participant"][paIds[0]]["attributes"]["stats"]["winner"]


        for m in mc["data"]:
            file = cls.MATCH_DIR + "/" + m["type"] + m["id"]
            match = {}
            match["data"] = m
            rosterIds = [i["id"] for i in m["relationships"]["rosters"]["data"]]
            match["rosters"] = {}
            for rId in rosterIds:
                match["rosters"][rId] = metas["roster"][rId]

            Util.saveData(file, match)
            cls.MATCHES += 1

    @classmethod
    def start(cls):
        logger.info("Starting tasks...")
        while True:
            logger.info("Requesting offset %s" % cls.OFFSET)
            mc = cls.requestMC(cls.OFFSET)
            cls.saveMatches(mc)
            logger.info("Requst finished, current fetched matches %s" % cls.MATCHES)
            cls.OFFSET += 1
            time.sleep(5)

if __name__ == "__main__":
    import os
    import argparse
    import subprocess
    parser = argparse.ArgumentParser(prog='CollectMatches.py')

    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-c', '--config', action='store', dest='config_file', default='vaingloryai.conf')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config = parseConfig(args)
    Collector.setup(config)
    Collector.start()
