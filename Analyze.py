import logging
import os
import json
from PIL import Image, ImageDraw, ImageFont
import StringIO
# import uuid

from Compute import DATA

logger = logging

class Painter(object):
    @classmethod
    def setup(cls, config):
        cls.font = config.get('general', 'font')
        cls.nameSize = 80
        cls.nameMaxWidth = 300
        cls.winnerPoint = (211, 54)
        cls.loserPoint = (776, 54)

        cls.color = (0, 0, 0, 255)
        cls.size = 30

    def __init__(self, c):
        winner, loser = (c.left, c.right) if c.left.WIN else (c.right, c.left)
        self.points = []
        winnerName = winner.getName()
        loserName = loser.getName()
        winnerPoint, winnerSize = self.calculateName(winnerName, winner=True)
        loserPoint, loserSize = self.calculateName(loserName, winner=False)
        winnerColor = (253,130,0, 255)
        loserColor = (255,255,255, 255)
        self.points.append({"position": winnerPoint, "content": winnerName, "size": winnerSize, 'color': winnerColor})
        self.points.append({"position": (115, 113), "content": winner.getKills(), 'color': winnerColor})
        self.points.append({"position": (115, 162), "content": winner.getDeaths(), 'color': winnerColor})
        self.points.append({"position": (115, 212), "content": winner.getAssists(), 'color': winnerColor})
        self.points.append({"position": (115, 254), "content": winner.getFarm(), 'color': winnerColor})
        self.points.append({"position": (115, 306), "content": winner.getWins(), 'color': winnerColor})
        self.points.append({"position": (106, 345), "content": winner.getTotal(), "size": 45, 'color': winnerColor})

        self.points.append({"position": loserPoint, "content": loserName, "size": loserSize, 'color': loserColor})
        self.points.append({"position": (662, 113), "content": loser.getKills(), 'color': loserColor})
        self.points.append({"position": (662, 162), "content": loser.getDeaths(), 'color': loserColor})
        self.points.append({"position": (662, 212), "content": loser.getAssists(), 'color': loserColor})
        self.points.append({"position": (662, 254), "content": loser.getFarm(), 'color': loserColor})
        self.points.append({"position": (662, 306), "content": loser.getWins(), 'color': loserColor})
        self.points.append({"position": (650, 345), "content": loser.getTotal(), "size": 45, 'color': loserColor})


    def draw(self, draw):
        for point in self.points:
            font = point['font'] if 'font' in point else self.font
            size = point['size'] if 'size' in point else self.size
            color = point['color'] if 'color' in point else self.color

            fmt = ImageFont.truetype(font, size)
            draw.text(point['position'], point['content'], font=fmt, fill=color)

    def calculateName(self, name, winner=True):
        canvas = Image.new('RGBA', (1000,1000), (255,255,255, 0))
        draw = ImageDraw.Draw(canvas)

        point = self.winnerPoint if winner else self.loserPoint
        size = self.nameSize
        w, h = 0, 0

        while True:
            font = ImageFont.truetype(self.font, size)
            w, h = draw.textsize(name, font)
            if w > self.nameMaxWidth:
                size -= 2
            else:
                break

        if winner:
            return (self.winnerPoint[0] - w/2, self.winnerPoint[1] - h/2), size
        else:
            return (self.loserPoint[0] - w/2, self.loserPoint[1] - h/2), size


class Paul(object):
    @classmethod
    def setup(cls, config):
        cls.image_dir = config.get('general', 'image_dir')
        cls.background = os.path.join(cls.image_dir, config.get('general', 'background'))

        Painter.setup(config)

    @classmethod
    def feed(cls, inputText):
        RAW = str(inputText)
        f = RAW.lower().find(Compare.key)
        if f == -1:
            raise Exception("Invalid vs question!")

        l = Team(RAW[:f])
        r = Team(RAW[f+len(Compare.key):])

        c = Compare(RAW, l, r)
        return cls.analyze(c)

    @classmethod
    def analyze(cls, c):
        Team.compute(c.left)
        Team.compute(c.right)
        if c.left.score > c.right.score:
            c.left.WIN = True
            c.winComment = c.left.getName() + ' will win.'
        elif c.left.score < c.right.score:
            c.right.WIN = True
            c.winComment = c.right.getName() + ' will win.'
        elif c.left.score == 0:
            c.winComment = "Paul think you're kidding."
        else:
            c.winComment = "Paul will always win, because Paul could be a fool sometimes."

        c.invalid = c.left.invalid + c.right.invalid
        if len(c.invalid) > 0:
            c.unknownComment = '<Paul can not recognize %s' % ', '.join(c.invalid) + '>'
        c.detailComment = """      Summary
name: %s vs %s
Kill Rate: %s vs %s
Death Rate: %s vs %s
Win Rate: %s vs %s
Assist Rate: %s vs %s
Farming: %s vs %s
Total Score: %s vs %s""" % \
(c.left.getName(), c.right.getName(),
 c.left.kills, c.right.kills,
 c.left.deaths, c.right.deaths,
 c.left.wins, c.right.wins,
 c.left.assists, c.right.assists,
 c.left.farm, c.right.farm,
 c.left.score, c.right.score)
        return c

    @classmethod
    def predict(cls, inputText, pic=False):
        try:
            c = cls.feed(inputText)
            logger.info(c.detailComment)
            if not pic:
                c.comment = "%s %s %s" % (c.winComment, c.unknownComment, c.detailComment)
                return c.comment, True

            else:
                c.comment = "%s %s" % (c.winComment, c.unknownComment)

                base = Image.open(cls.background).convert('RGBA')
                txt = Image.new('RGBA', base.size, (255,255,255,0))

                draw = ImageDraw.Draw(txt)
                painter = Painter(c)
                painter.draw(draw)

                out = Image.alpha_composite(base, txt)
                png = StringIO.StringIO()
                out.save(png, 'PNG')
                png.seek(0)
                return c.comment, png, True

        except Exception as e:
            logger.exception(e)

            if not pic:
                return None, False
            else:
                return None, None, False



class Team(object):
    def __init__(self, text):
        self.text = text.strip()
        self.valid = True

        self.kills = 0
        self.deaths = 0
        self.wins = 0
        self.loses = 0
        self.assists = 0
        self.farm = 0
        self.level = 0
        self.WIN = False
        self.score = 0

    def getName(self):
        return '+'.join(self.valid) if len(self.valid) > 0 else 'Unknown'

    def getKills(self):
        return 'Kills Score: ' + str(self.kills)[:6]

    def getDeaths(self):
        return 'Deaths Score: ' + str(self.deaths)[:6]

    def getAssists(self):
        return 'Assists Score: ' + str(self.assists)[:6]

    def getWins(self):
        return 'Defeating Score: ' + str(self.wins)[:6]

    def getTotal(self):
        return 'Total Score: ' + str(self.score)[:6]

    def getFarm(self):
        return 'Farming Score: ' + str(self.farm)[:6]



    @staticmethod
    def compute(t):
        Team.recognize(t)
        for h in t.heroes + t.players:
            t.kills += h.kills / float(h.samples)
            t.deaths += h.deaths / float(h.samples)
            t.wins += h.wins / float(h.samples)
            t.loses += h.loses / float(h.samples)
            t.assists += h.assists / float(h.samples)
            t.farm += h.farm / float(h.samples)
            t.level += h.level / float(h.samples)

        Team.score(t)

    @staticmethod
    def recognize(t):
        t.members = [m for m in t.text.split('+') if m.strip() != '']
        t.valid = []
        t.heroes = []
        t.players = []
        t.invalid = []
        for m in t.members:
            if len(t.valid) > 3:
                break
            if m in DATA.PLAYERLIST:
                t.players.append(DATA.PLAYERS.get(DATA.PLAYERLIST[m]))
                t.valid.append(m)
            elif m.lower() in DATA.HEROLIST.keys():
                t.heroes.append(DATA.HEROES.get(DATA.HEROLIST[m.lower()]))
                t.valid.append(DATA.HEROLIST[m.lower()].replace('*',''))
            else:
                t.invalid.append(m)

    @staticmethod
    def score(t):
        t.score = Compare.killsWeight * t.kills + \
                        Compare.deathsWeight * t.deaths + \
                        Compare.winsWeight * t.wins + \
                        Compare.losesWeight * t.loses + \
                        Compare.assistsWeight * t.assists + \
                        Compare.farmWeight * t.farm + \
                        Compare.levelWeight * t.level


class Compare(object):
    key = ' vs '

    deathsWeight = -0.6
    winsWeight = 1.8
    killsWeight = 1
    losesWeight = -1.8
    assistsWeight = 0.4
    farmWeight = 0.3
    levelWeight = 0.3

    winComment = ''
    comment = ''
    unknownComment = ''

    def __init__(self, raw, l, r):
        self.raw = raw
        self.left = l
        self.right = r
        self.valid = True
