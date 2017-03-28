import json
from os import listdir, path
import sys
import logging

from CollectMatches import Collector

logger = logging

def getMatches(filePath):

    with open(filePath, "r") as f:
        match = f.read()

    return json.loads(match)

def correctNames(name):
    return str(name).replace("*Hero009*", "*Krul*").replace("*Hero010*", "*Skaarf*").replace("*Hero016*", "*Rona*").replace("*Sayoc*", "*Taka*")


class Player(object):
    def __init__(self, player):
        actor_stats = player["attributes"]["stats"]
        stats = player["player"]["attributes"]["stats"]
        self.deaths = actor_stats["deaths"] or 0
        self.kills = actor_stats["kills"] or 0
        self.assists = actor_stats["assists"] or 0
        self.minionKills = actor_stats["minionKills"] or 0
        self.farm = actor_stats["farm"] or 0
        self.wins = 1 if actor_stats["winner"] else 0
        self.loses = 1 if self.wins == 0 else 0
        self.afks = 1 if actor_stats["wentAfk"] else 0
        self.crystalMineCaptures = actor_stats["crystalMineCaptures"] or 0


        self.ID = player["player"]["id"]
        self.lossStreak = stats["lossStreak"] or 0
        self.level = stats["level"] or 0
        self.xp = stats["xp"] or 0
        self.lifetimeGold = stats["lifetimeGold"] or 0
        self.winStreak = stats["winStreak"] or 0
        self.wins_total = stats["wins"] or 0
        self.played = stats["played"] or 0
        self.played_ranked = stats["played_ranked"] or 0
        self.name = player["player"]["attributes"]["name"]
        self.samples = 1

    def merge(self, p):
        self.deaths += p.deaths
        self.kills += p.kills
        self.assists += p.assists
        self.minionKills += p.minionKills
        self.farm += p.farm
        self.wins += p.wins
        self.loses += p.loses
        self.afks += p.afks
        self.crystalMineCaptures += p.crystalMineCaptures

        self.lossStreak = max(self.lossStreak, p.lossStreak)
        self.level = max(self.level, p.level)
        self.xp = max(self.xp, p.xp)
        self.lifetimeGold = max(self.lifetimeGold, p.lifetimeGold)
        self.winStreak = max(self.winStreak, p.winStreak)
        self.wins_total = max(self.wins_total, p.wins_total)
        self.played = max(self.played, p.played)
        self.played_ranked = max(self.played_ranked, p.played_ranked)
        self.name = p.name if p.played > self.played else self.name
        self.samples += p.samples




class Side(object):
    def __init__(self, side):
        self.ID = side["attributes"]["stats"]["side"]
        self.wins = 1 if side["winner"] else 0
        self.loses = 1 if self.wins == 0 else 0
        self.samples = 1
        self.gold = side["attributes"]["stats"]["gold"] or 0
        self.aces = side["attributes"]["stats"]["acesEarned"] or 0
        self.heroKills = side["attributes"]["stats"]["heroKills"] or 0
        self.turretKills = side["attributes"]["stats"]["turretKills"] or 0
        self.krakenCaptures = side["attributes"]["stats"]["krakenCaptures"] or 0

    def merge(self, s):
        self.samples += s.samples
        self.wins += s.wins
        self.loses += s.loses
        self.gold += s.gold
        self.aces += s.aces
        self.heroKills += s.heroKills
        self.turretKills += s.turretKills
        self.krakenCaptures += s.krakenCaptures


class Hero(object):
    def __init__(self, hero):
        self.ID = correctNames(hero["attributes"]["actor"])
        self.wins = 1 if hero["attributes"]["stats"]["winner"] else 0
        self.loses = 1 if self.wins == 0 else 0
        self.kills = hero["attributes"]["stats"]["kills"] or 0
        self.deaths = hero["attributes"]["stats"]["deaths"] or 0
        self.assists = hero["attributes"]["stats"]["assists"] or 0
        self.farm = hero["attributes"]["stats"]["farm"] or 0
        self.samples = 1

        playerStats = hero["player"]["attributes"]["stats"]
        self.winStreak = playerStats["winStreak"]
        self.lossStreak = playerStats["lossStreak"]
        self.level = playerStats["level"]

    def merge(self, h):
        self.samples += h.samples
        self.wins += h.wins
        self.loses += h.loses
        self.kills += h.kills
        self.deaths += h.deaths
        self.assists += h.assists
        self.farm += h.farm

        self.winStreak += h.winStreak
        self.lossStreak += h.lossStreak
        self.level += h.level


class Team(object):
    def __init__(self, team):
        self.ID = correctNames(("_").join(sorted([p["attributes"]["actor"] for p in team["participants"].values()])))
        if self.ID < 2:
            print team
        self.samples = 1
        self.wins = 1 if team["winner"] else 0
        self.loses = 1 if self.wins == 0 else 0

        stats = team["attributes"]["stats"]
        self.kills = stats["heroKills"]
        self.aces = stats["acesEarned"]
        self.gold = stats["gold"]
        self.krakenCaptures = stats["krakenCaptures"]

    def merge(self, t):
        self.samples += t.samples
        self.wins += t.wins
        self.loses += t.loses

        self.kills += t.kills
        self.aces += t.aces
        self.gold += t.gold
        self.krakenCaptures += t.krakenCaptures

class DATA(object):
    ITEMS = {}
    HEROES = {}
    TEAMS = {}
    SIDES = {}
    COUPLES = {}
    MATCHES = {}
    PLAYERS = {}
    HEROLIST = {}
    PLAYERLIST = {}
    TOTAL = 0

    @classmethod
    def initialize(cls, config, directory=None):
        if directory is None:
            match_dir = config.get("vainglory", "match_dir")
        else:
            match_dir = directory
        match_files = listdir(match_dir)
        total = len(match_files)
        cls.TOTAL = total
        for m in xrange(total):
            try:
                logger.debug("Consuming %s / %s" % (m + 1, total))
                filePath = path.join(match_dir, match_files[m])
                match = getMatches(filePath)
                DATA.consume(match)
            except Exception as e:
                logger.error("Error when loading and consuming the match %s " % match_files[m])
                logger.exception(e)
                continue

        for h in cls.HEROES.keys():
            key = h.lower().replace('*', '')
            cls.HEROLIST[key] = h

        for ID, p in cls.PLAYERS.iteritems():
            key = p.name
            cls.PLAYERLIST[key] = ID
        Collector.setup(config)
        logger.info("Game data is initialized!")

    @classmethod
    def getPlayerByLastMC(cls, playerName):
        matches = None
        try:
            matches = Collector.requestLastMatches(playerName, count=10)
        except Exception as e:
            logger.exception(e)
        logger.info(matches)
        return None

    @classmethod
    def consume(cls, m):
        ID = m["data"]["id"]
        cls.MATCHES[ID] = m["data"]
        for roster in m["rosters"].values():
            cls.sumTeam(roster)
            cls.sumSide(roster)

            t = Team(roster)

            if t.ID.count("_") < 2:
                logger.debug(ID)
                logger.debug(json.dumps(m))

    @classmethod
    def sumTeam(cls, roster):
        t = Team(roster)
        if t.ID not in cls.TEAMS:
            cls.TEAMS[t.ID] = t
        else:
            cls.TEAMS[t.ID].merge(t)

        for participant in roster["participants"].values():
            cls.sumHero(participant)
            cls.sumPlayer(participant)

    @classmethod
    def sumHero(cls, hero):
        h = Hero(hero)
        if h.ID not in cls.HEROES:
            cls.HEROES[h.ID] = h
        else:
            cls.HEROES[h.ID].merge(h)


    @classmethod
    def sumPlayer(cls, participant):
        p = Player(participant)
        if p.ID not in cls.PLAYERS:
            cls.PLAYERS[p.ID] = p
        else:
            cls.PLAYERS[p.ID].merge(p)


    @classmethod
    def sumSide(cls, side):
        s = Side(side)
        if s.ID not in cls.SIDES:
            cls.SIDES[s.ID] = s
        else:
            cls.SIDES[s.ID].merge(s)

    @classmethod
    def sumItem(cls, item):
        pass

    @classmethod
    def getHighestWinRate(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.wins / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero win rate ranking   ==========="
            for h in results:
                print "%s win rate: %s" % (h.ID, h.wins / float(h.samples))
            return
        return results

    @classmethod
    def getMostKills(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.kills / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero kills ranking   ==========="
            for h in results:
                print "%s kills: %s" % (h.ID, h.kills / float(h.samples))
            return
        return results

    @classmethod
    def getMostDeaths(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.deaths / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero deaths ranking   ==========="
            for h in results:
                print "%s deaths: %s" % (h.ID, h.deaths / float(h.samples))
            return
        return results

    @classmethod
    def getHighestFarming(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.farm / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero farms ranking   ==========="
            for h in results:
                print "%s farms: %s" % (h.ID, h.farm / float(h.samples))
            return
        return  results

    @classmethod
    def getHighestLoseRate(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.loses / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero loses ranking   ==========="
            for h in results:
                print "%s loses rate: %s" % (h.ID, h.loses / float(h.samples))
            return
        return results

    @classmethod
    def getMostAssists(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.assists / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero assists ranking   ==========="
            for h in results:
                print "%s assists: %s" % (h.ID, h.assists / float(h.samples))
            return
        return results

    @classmethod
    def getHotChoices(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.samples / float(cls.TOTAL), reverse=True)
        if show:
            print "=======   Hero Hot ranking   ==========="
            for h in results:
                print "%s chosen rate: %s" % (h.ID, h.samples / float(cls.TOTAL))
            return
        return results

    @classmethod
    def getHighestWinRateSide(cls, show=False):
        results = sorted(cls.SIDES.values(), key=lambda side: side.wins / float(side.samples), reverse=True)
        if show:
            print "=======   Highest win rate side ranking   ==========="
            for s in results:
                print "%s win rate: %s" % (s.ID, s.wins / float(s.samples))
            return
        return results

    @classmethod
    def getRichestSide(cls, show=False):
        results = sorted(cls.SIDES.values(), key=lambda side: side.gold / float(side.samples), reverse=True)
        if show:
            print "=======   Richest side ranking   ==========="
            for s in results:
                print "%s golds: %s" % (s.ID, s.gold / float(s.samples))
            return
        return results

    @classmethod
    def getMostAcesSide(cls, show=False):
        results = sorted(cls.SIDES.values(), key=lambda side: side.aces / float(side.samples), reverse=True)
        if show:
            print "=======   Side Races ranking   ==========="
            for s in results:
                print "%s aces: %s" % (s.ID, s.aces / float(s.samples))
            return
        return results

    @classmethod
    def getMostKillsSide(cls, show=False):
        results = sorted(cls.SIDES.values(), key=lambda side: side.heroKills / float(side.samples), reverse=True)
        if show:
            print "=======   Side heroKills ranking   ==========="
            for s in results:
                print "%s hero kills: %s" % (s.ID, s.heroKills / float(s.samples))
            return
        return results

    @classmethod
    def getHotSide(cls, show=False):
        results = sorted(cls.SIDES.values(), key=lambda side: side.samples / float(cls.TOTAL), reverse=True)
        if show:
            print "=======   Side Hot ranking   ==========="
            for s in results:
                print "%s chosen rate: %s" % (s.ID, s.samples / float(cls.TOTAL))
            return
        return results

    @classmethod
    def getWorstTurn(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.winStreak / float(hero.samples), reverse=True)
        if show:
            print "=======   Worst Turn Hero ranking   ==========="
            for h in results:
                print "%s win streak: %s" % (h.ID, h.winStreak / float(h.samples))
            return
        return results

    @classmethod
    def getBestTurn(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.lossStreak / float(hero.samples), reverse=True)
        if show:
            print "=======   Best Turn Hero ranking   ==========="
            for h in results:
                print "%s loss streak: %s" % (h.ID, h.lossStreak / float(h.samples))
            return
        return results

    @classmethod
    def getHighestLevelHero(cls, show=False):
        results = sorted(cls.HEROES.values(), key=lambda hero: hero.level / float(hero.samples), reverse=True)
        if show:
            print "=======   Hero Player Level ranking   ==========="
            for h in results:
                print "%s level: %s" % (h.ID, h.level / float(h.samples))
            return
        return results

    @classmethod
    def getHighestWinStreakPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.winStreak, reverse=True)
        if show:
            print "=======   Player Win Streak ranking   ==========="
            for p in results[:10]:
                print "%s win streak: %s" % (p.name, p.winStreak)
            return
        return results

    @classmethod
    def getHighestLossStreakPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.lossStreak, reverse=True)
        if show:
            print "=======   Player Loss Streak ranking   ==========="
            for p in results[:10]:
                print "%s loss streak: %s" % (p.name, p.lossStreak)
            return
        return results

    @classmethod
    def getHighestLevelPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.level, reverse=True)
        if show:
            print "=======   Player Level ranking   ==========="
            for p in results[:10]:
                print "%s level: %s" % (p.name, p.level)
            return
        return results

    @classmethod
    def getBiggestFan(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.samples, reverse=True)
        if show:
            print "=======   Player played matches ranking   ==========="
            for p in results[:10]:
                print "%s played matches: %s" % (p.name, p.samples)
            return
        return results

    @classmethod
    def getBiggestFan1(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.played, reverse=True)
        if show:
            print "=======   Player played matches1 ranking   ==========="
            for p in results[:10]:
                print "%s played matches1: %s" % (p.name, p.played)
            return
        return results

    @classmethod
    def getMostKillsPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.kills / float(player.samples), reverse=True)
        if show:
            print "=======   Player kills ranking   ==========="
            for p in results[:10]:
                print "%s kills: %s" % (p.name, p.kills / float(p.samples))
            return
        return results

    @classmethod
    def getMostDeathsPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.deaths / float(player.samples), reverse=True)
        if show:
            print "=======   Player deaths ranking   ==========="
            for p in results[:10]:
                print "%s deaths: %s" % (p.name, p.deaths / float(p.samples))
            return
        return results

    @classmethod
    def getBestPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.wins / float(player.samples), reverse=True)
        if show:
            print "=======   Player win rate ranking   ==========="
            for p in results[:10]:
                print "%s win rate: %s" % (p.name, p.wins / float(p.samples))
            return
        return results

    @classmethod
    def getWorstPlayer(cls, show=False):
        results = sorted(cls.PLAYERS.values(), key=lambda player: player.loses / float(player.samples), reverse=True)
        if show:
            print "=======   Player lose rate ranking   ==========="
            for p in results[:10]:
                print "%s lose rate: %s" % (p.name, p.loses / float(p.samples))
            return
        return results

    @classmethod
    def getHighestWinRateTeam(cls, show=False):
        results = sorted(cls.TEAMS.values(), key=lambda team: team.wins / float(team.samples), reverse=True)
        if show:
            print "=======   Team win rate ranking   ==========="
            for t in results[:10]:
                print "%s win rate: %s" % (t.ID, t.wins / float(t.samples))
            return
        return results

    @classmethod
    def getHighestLoseRateTeam(cls, show=False):
        results = sorted(cls.TEAMS.values(), key=lambda team: team.loses / float(team.samples), reverse=True)
        if show:
            print "=======   Team lose rate ranking   ==========="
            for t in results[:10]:
                print "%s lose rate: %s" % (t.ID, t.loses / float(t.samples))
            return
        return results

    @classmethod
    def getMostAcesTeam(cls, show=False):
        results = sorted(cls.TEAMS.values(), key=lambda team: team.aces / float(team.samples), reverse=True)
        if show:
            print "=======   Team aces rate ranking   ==========="
            for t in results[:10]:
                print "%s aces: %s" % (t.ID, t.aces / float(t.samples))
            return
        return results

    @classmethod
    def getHotestTeam(cls, show=False):
        results = sorted(cls.TEAMS.values(), key=lambda team: team.samples, reverse=True)
        if show:
            print "=======   Team chosen times ranking   ==========="
            for t in results[:10]:
                print "%s chosen: %s" % (t.ID, t.samples)
            print json.dumps(cls.HEROES['*Ringo*'].__dict__)
            print json.dumps(cls.PLAYERS[cls.PLAYERS.keys()[10]].__dict__)
            return
        return results





if __name__ == "__main__":
    match_dir = "Matches"
    DATA.initialize(None, match_dir)
    if DATA.TOTAL == 0:
        print "No match data found!"
        sys.exit(1)

    DATA.getHighestWinRate(True)
    DATA.getHighestLoseRate(True)
    DATA.getMostKills(True)
    DATA.getMostDeaths(True)
    DATA.getMostAssists(True)
    DATA.getHighestFarming(True)
    DATA.getHotChoices(True)
    DATA.getHighestWinRateSide(True)
    DATA.getMostAcesSide(True)
    DATA.getMostKillsSide(True)
    DATA.getRichestSide(True)
    DATA.getHotSide(True)

    DATA.getWorstTurn(True)
    DATA.getBestTurn(True)
    DATA.getHighestLevelHero(True)
    DATA.getWorstPlayer(True)
    DATA.getBestPlayer(True)
    DATA.getMostDeathsPlayer(True)
    DATA.getMostKillsPlayer(True)
    DATA.getHighestLevelPlayer(True)
    DATA.getHighestWinStreakPlayer(True)
    DATA.getHighestLossStreakPlayer(True)
    DATA.getBiggestFan(True)
    DATA.getBiggestFan1(True)

    DATA.getHotestTeam(True)
    DATA.getHighestWinRateTeam(True)
    DATA.getHighestLoseRateTeam(True)
    DATA.getMostAcesTeam(True)
