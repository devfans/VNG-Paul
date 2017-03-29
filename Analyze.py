# coding: utf-8

import logging
import os
import json
from PIL import Image, ImageDraw, ImageFont
import StringIO
# import uuid

from nn.evaluator import eval as nneval

from Compute import DATA

logger = logging

class InvalidCompareError(Exception): pass
class IndecentCompareError(Exception): pass


class Painter(object):
    @classmethod
    def setup(cls, config):
        cls.font = config.get('general', 'font')
        cls.nameFont = config.get('general', 'name_font')
        cls.nameSize = 55
        cls.totalSize = 40
        cls.size = 30
        cls.winnerPoints = [(248, 112), (248, 159), (248, 207)]
        cls.loserPoints = [(742, 112), (742, 159), (742, 207)]

        cls.color = (255,255,255, 255)
        cls.winnerColor = (255,180,0, 255)
        cls.loserColor = (186,0,219, 255)

        cls.scoreLength = 2


    def __init__(self, c):
        winner, loser = (c.left, c.right) #if c.left.WIN else (c.right, c.left)
        self.points = []

        if len(winner.valid) < 2:
            name = "Unknown" if len(winner.valid) < 1 else winner.valid[0]
            pos = self.calculatePosition(name, self.winnerPoints[1], self.nameSize, self.nameFont)
            self.points.append({"position": pos, "content": name, "size": self.nameSize, "color": self.winnerColor, "font": self.nameFont})
        elif len(winner.valid) < 3:
            for i in xrange(2):
                pos = self.calculatePosition(winner.valid[i], self.winnerPoints[i], self.nameSize, self.nameFont)
                self.points.append({"position": pos, "content": winner.valid[i], "size": self.nameSize, "color": self.winnerColor, "font": self.nameFont})
        else:
            for i in xrange(len(self.winnerPoints)):
                pos = self.calculatePosition(winner.valid[i], self.winnerPoints[i], self.nameSize, self.nameFont)
                self.points.append({"position": pos, "content": winner.valid[i], "size": self.nameSize, "color": self.winnerColor, "font": self.nameFont})


        tag, value = winner.getWins()
        self.points.append({"position": (77, 316), "content": tag})
        pos = self.calculatePosition(value, (431, 316), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = winner.getKills()
        self.points.append({"position": (77, 357), "content": tag})
        pos = self.calculatePosition(value, (431, 357), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = winner.getDeaths()
        self.points.append({"position": (77, 400), "content": tag})
        pos = self.calculatePosition(value, (431, 400), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = winner.getAssists()
        self.points.append({"position": (77, 441), "content": tag})
        pos = self.calculatePosition(value, (431, 441), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = winner.getFarm()
        self.points.append({"position": (77, 485), "content": tag})
        pos = self.calculatePosition(value, (431, 485), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = winner.getTotal()
        self.points.append({"position": (77, 591), "content": tag, "size": self.totalSize})
        pos = self.calculatePosition(value, (431, 591), self.totalSize, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value, "size": self.totalSize})

        #tag, value = c.getNN()
        #self.points.append({"position": (77, 644), "content": tag, "size": self.totalSize})
        #pos = self.calculatePosition(value, (431, 644), self.totalSize, self.font, fromEnd=True)
        #self.points.append({"position": pos, "content": value, "size": self.totalSize})

        if len(loser.valid) < 2:
            name = "Unknow" if len(loser.valid) < 1 else loser.valid[0]
            pos = self.calculatePosition(name, self.loserPoints[1], self.nameSize, self.nameFont)
            self.points.append({"position": pos, "content": name, "size": self.nameSize, "color": self.loserColor, "font": self.nameFont})
        elif len(loser.valid) < 3:
            for i in xrange(2):
                pos = self.calculatePosition(loser.valid[i], self.loserPoints[i], self.nameSize, self.nameFont)
                self.points.append({"position": pos, "content": loser.valid[i], "size": self.nameSize, "color": self.loserColor, "font": self.nameFont})
        else:
            for i in xrange(len(self.loserPoints)):
                pos = self.calculatePosition(loser.valid[i], self.loserPoints[i], self.nameSize, self.nameFont)
                self.points.append({"position": pos, "content": loser.valid[i], "size": self.nameSize, "color": self.loserColor, "font": self.nameFont})

        tag, value = loser.getWins()
        self.points.append({"position": (571, 316), "content": tag})
        pos = self.calculatePosition(value, (925, 316), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = loser.getKills()
        self.points.append({"position": (571, 357), "content": tag})
        pos = self.calculatePosition(value, (925, 357), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = loser.getDeaths()
        self.points.append({"position": (571, 400), "content": tag})
        pos = self.calculatePosition(value, (925, 400), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = loser.getAssists()
        self.points.append({"position": (571, 441), "content": tag})
        pos = self.calculatePosition(value, (925, 441), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = loser.getFarm()
        self.points.append({"position": (571, 485), "content": tag})
        pos = self.calculatePosition(value, (925, 485), self.size, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value})
        tag, value = loser.getTotal()
        self.points.append({"position": (571, 591), "content": tag, "size": self.totalSize})
        pos = self.calculatePosition(value, (925, 591), self.totalSize, self.font, fromEnd=True)
        self.points.append({"position": pos, "content": value, "size": self.totalSize})

        #tag, value = c.getNN()
        #self.points.append({"position": (571, 644), "content": tag, "size": self.totalSize})
        #pos = self.calculatePosition("%.2f" % (1 - float(value)), (925, 644), self.totalSize, self.font, fromEnd=True)
        #self.points.append({"position": pos, "content": "%.2f" % (1 - float(value)), "size": self.totalSize})




    def draw(self, draw):
        for point in self.points:
            font = point['font'] if 'font' in point else self.font
            size = point['size'] if 'size' in point else self.size
            color = point['color'] if 'color' in point else self.color
            fmt = ImageFont.truetype(font, size)
            draw.text(point['position'], point['content'], font=fmt, fill=color)

    def calculatePosition(self, text, point, size, font, fromEnd=False):
        canvas = Image.new('RGBA', (1000,1000), (255,255,255, 0))
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.truetype(font, size)
        w, h = draw.textsize(text, font)
        print("%s %s")

        if fromEnd:
            return (point[0] - w, point[1])
        return (point[0] - w/2, point[1] - h/2)



class VaingloryAI(object):
    @classmethod
    def setup(cls, config):
        cls.image_dir = config.get('general', 'image_dir')
        cls.background = os.path.join(cls.image_dir, config.get('general', 'background'))

        Painter.setup(config)
        cls.invalidCompare = u"😝Please enter a 1v1 or 3v3 matchup! Thanks!"

    @classmethod
    def feed(cls, inputText):
        RAW = str(inputText)
        f = RAW.lower().find(Compare.key)
        if f == -1:
            raise InvalidCompareError()

        l = Team(RAW[:f])
        r = Team(RAW[f+len(Compare.key):])

        c = Compare(RAW, l, r)
        return cls.analyze(c)

    @classmethod
    def analyze(cls, c):
        Team.compute(c.left)
        Team.compute(c.right)
        VS = (len(c.left.members), len(c.right.members))
        if VS != (1, 1) and VS != (3, 3):
            raise IndecentCompareError()
        nnPrediction = True
        try:
            c.leftTeamPrediction = nneval(c.left.players + c.left.heroes + c.right.players + c.right.heroes)
        except Exception as e:
            nnPrediction = False
            logger.info("NN prediction failed")
            print(str(e))
            logger.exception(e)
            
        if c.left.score > c.right.score:
            c.left.WIN = True
            if not nnPrediction:
                c.winComment = c.left.getName() + ' will win.'
            elif c.leftTeamPrediction >= 0.5:
                c.winComment = c.left.getName() + ' will win.'
            else:
                p = int((1.0 - c.leftTeamPrediction) * 100)
                c.winComment = '{} scored lower but our analysis gives them a {}% of winning.'.format(c.right.getName(), p)
        elif c.left.score < c.right.score:
            c.right.WIN = True
            if not nnPrediction:
                c.winComment = c.right.getName() + ' will win.'
            elif c.leftTeamPrediction < 0.5:
                c.winComment = c.right.getName() + ' will win.'
            else:
                p = int(c.leftTeamPrediction * 100)
                c.winComment = '{} scored lower but our analysis gives them a {}% of winning.'.format(c.left.getName(), p)
        elif c.left.score == 0:
            c.winComment = "VaingloryAI think you're kidding."
        else:
            c.winComment = "VaingloryAI will always win, because VaingloryAI could be a fool sometimes."

        c.invalid = c.left.invalid + c.right.invalid
        if len(c.invalid) > 0:
            c.unknownComment = '<VaingloryAI can not recognize %s' % ', '.join(c.invalid) + '>'
        c.detailComment = "No details for now"
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
        except (InvalidCompareError, IndecentCompareError) as e:
            return cls.invalidCompare, None, False
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
        return 'KILL SCORE', self.trimScore(self.kills)

    def getDeaths(self):
        return 'DEATH SCORE', self.trimScore(self.deaths)

    def getAssists(self):
        return 'ASSIST SCORE', self.trimScore(self.assists)

    def getWins(self):
        return 'WIN SCORE', self.trimScore(self.wins)

    def getTotal(self):
        return 'TOTAL SCORE', self.trimScore(self.score)

    def getFarm(self):
        return 'FARMING SCORE', self.trimScore(self.farm)

    def trimScore(self, score):
        return "%.2f" % float(score)

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
            
            if m.lower() in DATA.HEROLIST.keys():
                t.heroes.append(DATA.HEROES.get(DATA.HEROLIST[m.lower()]))
                t.valid.append(DATA.HEROLIST[m.lower()].replace('*',''))
            else:
                # player = DATA.getPlayerByLastMC(m)
                player = None
                if player is not None:
                    t.players.append(player)
                    t.valid.append(m)
                elif m in DATA.PLAYERLIST:
                    t.players.append(DATA.PLAYERS.get(DATA.PLAYERLIST[m]))
                    t.valid.append(m)
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
    leftTeamPrediction = -1.0

    winComment = ''
    comment = ''
    unknownComment = ''

    def __init__(self, raw, l, r):
        self.raw = raw
        self.left = l
        self.right = r
        self.valid = True
        
    def getNN(self):
        logger.info('PREDICTION {}'.format(self.leftTeamPrediction))
        return 'PREDICTION', "%.2f" % float(self.leftTeamPrediction)
        
