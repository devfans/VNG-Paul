import logging
import time
import json
from threading import Thread

from TwitterAPI import TwitterAPI, TwitterRequestError, TwitterConnectionError
from Analyze import VaingloryAI

logger = logging

class TwitterHooking(object):
    @classmethod
    def setup(cls, config):
        section = "twitter"
        consumer_token = config.get(section, "consumer_token")
        consumer_secret = config.get(section, "consumer_secret")
        access_token = config.get(section, "access_token")
        access_token_secret = config.get(section, "access_token_secret")
        cls.ID = config.get(section, "account")
        cls.mention = '@' + cls.ID

        cls.api = TwitterAPI(consumer_token, consumer_secret, access_token, access_token_secret)

        cls._thread = Thread(target=cls.stream)
        cls._thread.daemon = True
        cls._thread.start()

    @classmethod
    def stream(cls):
        try:
            cls._stream()
        except Exception as e:
            logger.exception(e)


    @classmethod
    def _stream(cls):
        while True:
            try:
                iterator = cls.api.request('statuses/filter', {'track': cls.ID}).get_iterator()
                for item in iterator:
                    if cls.mention in item.get('text', None).lower():
                        cls.reply(item)
                    if 'text' in item:
                        print(item['text'])
                    elif 'disconnect' in item:
                        event = item['disconnect']
                        if event['code'] in [2,5,6,7]:
                            # something needs to be fixed before re-connecting
                            raise Exception(event['reason'])
                        else:
                            # temporary interruption, re-try request
                            time.sleep(5)
                            break
            except TwitterRequestError as e:
                if e.status_code < 500:
                    # something needs to be fixed before re-connecting
                    raise
                else:
                    # temporary interruption, re-try request
                    time.sleep(5)
            except TwitterConnectionError:
                # temporary interruption, re-try request
                time.sleep(5)

            except Exception as e:
                logger.exception(e)

    @classmethod
    def reply(cls, item):
        userName = item['user'].get("screen_name", "")
        inputText = item.get('text', None).replace(cls.mention, '').strip()

        answer, pic, ok = VaingloryAI.predict(inputText, pic=True)

        answer = '@' + userName + ' ' + answer
        logger.info("replying to tweet of %s", userName)
        if ok:
            r = cls.api.request('statuses/update_with_media', {'status': answer, 'in_reply_to_status_id': item.get('id', None)}, {'media[]': pic})
        else:
            r = cls.api.request('statuses/update', {'status': answer, 'in_reply_to_status_id': item.get('id', None)})
        logger.info('SUCCESS' if r.status_code == 200 else 'FAILURE')
