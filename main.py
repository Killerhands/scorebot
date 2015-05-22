import json
from urllib2 import urlopen

NHLGameArray = []
NBAGameArray = []
NFLGameArray = []

Games = []
liveGames = []

class Game:
	def __init__(self, sport, gameID, hTeam, aTeam, sHome, sAway, status, startTime, dayOfWeek, winner):
		self.sport = sport
		self.id = gameID
		self.homeTeam = hTeam
		self.awayTeam = aTeam
		self.sHome = sHome
		self.sAway = sAway
		self.status = status
		self.startTime = startTime
		self.dayOfWeek = dayOfWeek
		self.winner = winner

		if self.status == 'final overtime':
			self.status = 'FINAL OT'

	def getHomeTeam(self):
		return self.homeTeam

	def getAwayTeam(self):
		return self.awayTeam

	def getWinner(self):
		return self.winner

	def getStatus(self):
		return self.status

	def getSport(self):
		return self.sport

	def __comp__(self, other):
                if self.homeTeam == other.homeTeam:
                        if self.awayTeam = other.awayTeam:
                                return True



#Return games currently being played
def GetLiveGames():
	global Games
	global liveGames

	liveGames = []
	for game in Games:
		if 'LIVE' in game.status:
			liveGames.append(game)

	return liveGames


#Return
def postLiveGameStatus(sport='ALL'):
	liveGames = GetLiveGames()

	liveGameStr = 'Live Games: '

	if sport == 'ALL':
		for game in liveGames:
			liveGameStr += '[%s] %s %s-%s %s ' % (game.sport, game.homeTeam, game.sHome, game.sAway, game.awayTeam)
	elif sport == 'NHL':
		for game in liveGames:
			if game.sport == 'NHL':
				liveGameStr += '[%s] %s %s-%s %s ' % (game.sport, game.homeTeam, game.sHome, game.sAway, game.awayTeam)
	elif sport == 'NFL':
		for game in liveGames:
			if game.sport == 'NFL':
				liveGameStr += '[%s] %s %s-%s %s ' % (game.sport, game.homeTeam,game.sHome, game.sAway, game.awayTeam)

	print liveGameStr



def getNHLScores():
	global NHLGameArray
	NHLFeed = urlopen('http://live.nhle.com/GameData/RegularSeasonScoreboardv3.jsonp')
	#Parse into Json
	gameStr = NHLFeed.read()
	gameJson = gameStr.strip('loadScoreboard(')
	gameJson = gameJson[:-1]
	gameJson = json.loads(gameJson)

	for game in gameJson['games']:
		htWin = game['htc']
		atWin = game['atc']
		gameStatus = game['bs']

		if 'FINAL' in gameStatus.upper():
			if htWin == '':
				winner = game['htv']
			else:
				winner = game['atv']
		newGame = Game(
			sport = 'NHL',
			gameID = game['id'], 
			hTeam = game['htv'], 
			aTeam = game['atv'],
			sHome = game['hts'],
			sAway = game['ats'],
			status = game['bs'],
			startTime = game['bs'],
			dayOfWeek = game['ts'],
			winner = winner,
			 )

		Games.append(newGame)
		for game in Games:
                        for NHLGame in NHLGameArray:
                                
		NHLGameArray.append(newGame)
	return NHLGameArray


def getNFLScores():
	global NFLGameArray
	NFLFeed = urlopen('http://www.nfl.com/liveupdate/scorestrip/scorestrip.json')
	#Parse into Json
	gameStr = NFLFeed.read()
	gameJson = gameStr.split('[')
	gameJson.pop(0)
	gameJson.pop(0)

	for game in gameJson:
		game = game.split(',')
		#for stuff in game:
	#		stuff = stuff.strip('"')
			#print stuff
		#print game

	for game in gameJson:
		game = game.split(',')
		hTeam = game[4].strip('"')
		aTeam = game[6].strip('"')
		sHome = game[5].strip('"')
		sAway = game[7].strip('"')

		if sHome == '':
			sHome = 0
		if sAway == '':
			sAway = 0


		if sHome > sAway:
			winner = hTeam
		elif sHome < sAway:
			winner = aTeam
		else:
			winner = 'N/A'
		newGame = Game(
			sport = 'NFL',
			gameID = 0, 
			hTeam = hTeam, 
			aTeam = aTeam,
			sHome = sHome,
			sAway = sAway,
			status = game[2].strip('"') + ' ' + game[3].strip('"'),
			startTime = game[2].strip('"'),
			dayOfWeek = game[0].strip('"'),
			winner = winner,
			 )

		Games.append(newGame)

		NFLGameArray.append(newGame)

#	for game in Games:
#		if game.sport == 'NFL':
#			print '[NFL] - %s %s-%s %s' % (game.homeTeam, game.sHome, game.sAway, game.awayTeam)
	return NFLGameArray





def postGameScores(sport):
	global Games
	currentGame = sport

	for game in Games:
		if game.sport == currentGame:
			hTeam = game.getHomeTeam()
			aTeam = game.getAwayTeam()
			gWinner = game.getWinner()
			if 'FINAL' in game.status.upper():
				print '[%s] %s %s-%s %s' % (game.sport, game.homeTeam, game.sHome, game.sAway, game.awayTeam)
			else:
				if 'LIVE' in game.status:
					print '[%s] %s %s-%s %s | Game Status: %s' % (game.sport, hTeam, aTeam, game.sHome, game.sAway, game.status)
				else:
					print '[%s] %s %s-%s %s | Game Status: %s' % (game.sport, hTeam, game.sHome, game.sAway, aTeam, game.status)


#NHLGames = getNHLScores()

#for game in NHLGames:
#	show = True
#	hTeam = game.getHomeTeam()
#	aTeam = game.getAwayTeam()
#	gWinner = game.getWinner()
#	if 'FINAL' in game.status:
#		print '[%s] %s %s-%s %s' % (game.sport, hTeam, game.sHome, game.sAway, aTeam)
#	else:
#		if 'LIVE' in game.status:
#			print '[%s] %s %s-%s %s | Game Status: %s' % (game.sport, hTeam, game.sHome, game.sAway, aTeam, game.status)
#		else:
#			print '[%s] %s 0-0 %s | Game Status: %s' % (game.sport, hTeam, aTeam, game.status)



def returnGameStatus(TeamA, TeamB):
	global Games
	gameFound = None
	teamOne = TeamA.upper()
	teamTwo = TeamB.upper()
	for game in Games:
		if game.homeTeam.upper() == teamOne and game.awayTeam.upper() == teamTwo:
			gameFound = game
			break
		if game.homeTeam.upper() == teamTwo and game.awayTeam.upper() == teamOne:
			gameFound = game
			break

	if gameFound is None:
		print "No Game Found!"
	else:
		print '[%s] %s %s-%s %s [%s]' % (gameFound.sport, gameFound.homeTeam, gameFound.sHome, gameFound.sAway, gameFound.awayTeam, gameFound.status)
		return game



#GetLiveGames()


getNHLScores()
#getNFLScores()
postGameScores('NHL')
postLiveGameStatus()

#returnGameStatus('penguins', 'senators')
