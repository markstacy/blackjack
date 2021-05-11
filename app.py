"""
Blackjack - a simple web-based application
for the clasic game - mas 05-10-2021
"""

import flask
from flask import request
import requests
import json

"""
global declarations
"""
app = flask.Flask(__name__)
app.config["DEBUG"] = True

game = None

"""
Blackjack class declaration
"""
class Blackjack():
    def __init__(self, players = 2):
        self.players = Players(self)
        self.id = ""
        self.responseCode = 0
        self.responseText = ""
        self.over = False
        for i in range(players):
            self._addPlayer()
        self.deck = []
        
    # add a player to the game
    def _addPlayer(self):
        self.players.addPlayer()
        
    # get the list of players in the game
    def getPlayers(self):
        return self.players.getPlayers()
    
    # get a player in the game by index (number)
    def getPlayer(self, number):
        return self.players.getPlayer(number)

    # get a count of players in the game 
    def getPlayerCount(self):
        return self.players.getPlayerCount()

    # set the deck id for this game
    def setId(self, id):
        self.id = id

    # get the deck id for this game
    def getId(self):
        return self.id
    
    # build the deck for this game
    def setDeck(self, deck):
        self.deck = deck["cards"]

    # draw the top card from the deck for this game
    def draw(self):
        if len(self.deck) > 0:
            return self.deck.pop(0)
        else:
            return None
    # how many remaing cards are im the deck for this game
    def getRemaining(self):
        return len(self.deck);
    
    # set the last api server server response code
    def setResponseCode(self, responseCode):
        self.responseCode = responseCode

    # get the last api server server response code
    def getResponseCode(self):
        return self.responseCode

    # set the last api server server response text
    def setResponseText(self, responseText):
        self.responseText = responseText
        
    # get the last api server server response text
    def getResponseText(self):
        return self.responseText
    
    def setOver(self, over):
        self.over = over

    # determine if the game is over   
    def isOver(self):
        if not self.over:
            over = True
            blackjack = False
            for player in self.players.getPlayers():
                if not blackjack and not player.isOut():
                    over = False
                elif player.hasBlackjack():
                    blackjack = True
            self.over = over or blackjack
        return self.over

    # do a reset of the the game   
    def reset(self):
        self.players.reset()
        self.id = ""
        self.remaining = 0
        self.responseCode = 0
        self.responseText = ""
        self.over = False
        self.deck.clear()
 
    # determine if we have a winner
    def winner(self):
        winner = None
        high = 0
        for player in self.players.getPlayers():
            s = player.getScore()
            if not player.isBusted():
                if s > high:
                    winner = player
                    high = s
                elif s == high:
                    winner = None
        return winner
                    
    # get a JSON representation of the state of this game
    def getStateJSON(self):
        TorF = ["False", "True"]
        state = '' # a json string representation of the state of the game

        state = '{"Over": '
        state += '"'+TorF[game.isOver()]+'"'
        state += ', "Player Count": "' +str(game.getPlayerCount())+'"'
        state += ', "Cards Remaining": "' +str(game.getRemaining())+'"'
        state += ', "DeckId": "' +str(game.getId())+'"'
        state += ', "LastResponseCode": "' +str(game.getResponseCode())+'"'
        state += ', "LastResponseText": "' +str(game.getResponseText())+'"'
        state += ', "Players": ['
        players = []
        for player in game.getPlayers():
            pstr = '{"Number": "'+str(player.getNumber())+'", '
            pstr += '"Card Count": "'+str(player.cardCount())+'", '
            pstr += '"Score": "'+str(player.getScore())+'", '
            pstr += '"Holding": "'+TorF[player.isHolding()]+'", '
            pstr += '"Busted": "'+TorF[player.isBusted()]+'", '
            pstr += '"Out": "'+TorF[player.isOut()]+'", '
            pstr += '"Cards": ['
            cards = []
            for card in player.getCards():
                cstr = '{"Value": "'+card["value"]+'", '
                cstr += '"Suit": "'+card["suit"]+'"}'
                cards.append(cstr)
                cstr = ''
            pstr += ', '.join(cards)
            pstr += ']}'
            players.append(pstr)
        state += ', '.join(players)
        state += ']}'

        return state

"""
Players class declaration
"""    
class Players():

    # initialize the player list           
    def __init__(self, game):
        self.players = []
        self.game = game

    # add a player
    def addPlayer(self):
        self.players.append(Player(len(self.players)+1, self.game))
                            
    # get a player
    def getPlayer(self, number):
        if len(self.players) >= number - 1:
            return self.players[number-1]
        else:
            return None
    
    # retrieve the player list                            
    def getPlayers(self):
        return self.players
                            
    # remove all players                            
    def clear(self):
        self.players.clear()
        
    # retrieve the player count                            
    def getPlayerCount(self):
        return len(self.players)
                            
    # reset the player list and current deck           
    def reset(self):
        for player in self.players:
            player.reset()
        self.deck = []
                
"""
Player class declaration
"""
class Player():
    
    # initialize the player
    def __init__(self, number, game):
        self.number = number
        self.game = game
        self.cards = []
        self.busted = False
        self.hold = False
        self.score = 0
        self.dirty = True
        
    # reset the player          
    def reset(self):
        self.cards.clear()
        self.busted = False
        self.hold = False
        self.score = 0
        self.dirty = False
        
    # get the player's number          
    def getNumber(self):
        return self.number
    
    # add a card to the player's hand          
    def addCard(self, card):
        self.cards.append(card)
        self.dirty = True
    
    # get the list of the player's cards
    def getCards(self):
        return self.cards
    
    # get the count of the player's cards
    def cardCount(self):
        return len(self.cards)
    
    # get the player's score
    def getScore(self):
        # is the current score correct? if not, recalculate
        if self.dirty:
            self.score = 0
            aces = 0
            # iterate through the hand
            for card in self.cards:
                # is the current card a number card? if so, add it to the total
                if card["value"].isdigit():
                    self.score += int(card["value"])
                # is the current card an ace? if so, add it to the total of aces in the hand
                elif card["value"][0] == 'A':
                    aces += 1
                # otherwise, it's a face card so add 10 to the total
                else:
                    self.score += 10
                    
            # if we have aces, determine whether we should use them as an 11 or a 1
            while aces > 0:
                aces -= 1
                if self.score + 11 + aces <= 21:
                    self.score += 11
                else:
                    self.score += 1
                    
            if self.score > 21:
                self._busted()
                self.game.setOver(True)
                
            self.dirty = False
            
        return self.score
        
    
    def stay(self):
        self.hold = True
        
    def _busted(self):
        self.busted = True
        
    def isHolding(self):
        return self.hold
    
    def isBusted(self):
        return self.busted
    
    def isOut(self):
        return self.isHolding() or self.isBusted()
    
    def hasBlackjack(self):
        return self.score == 21 and self.cardCount() == 2
    
"""
function to get the layout for a player's row
"""
def getLayout(player):
    # card layout
    global game
    score = player.getScore()
    ps = str(player.number)
    ss = str(score)
    if not game.isOver():
        href ='http://0.0.0.0:5000/hit?player='+ps
    else:
        href = "#"
    html = '<p><span class="msg">Player '+ps+'</span><p>'
    for card in player.getCards():
        html += '<a href="'+href+'"><img src="'+card["image"]+'" alt="'+card["value"]+' of '+card["suit"]+'"height=200 width=150></a>'
    
    # buttons
    if not game.isOver():
        if not player.isOut():
            if score < 21:
                html += '&nbsp&nbsp&nbsp&nbsp<a href="#"  class="myButton">Score:&nbsp<B>'+ss+'</B></a>'
                html += '&nbsp&nbsp&nbsp&nbsp<a href="http://0.0.0.0:5000/hit?player='+ps+'"class="myButton">Hit Me!</a>'
                html += '&nbsp&nbsp&nbsp&nbsp<a href="http://0.0.0.0:5000/stay?player='+ps+'" class="myButton">Stand</a>'
            elif player.hasBlackjack():
                html += '&nbsp&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton"><B>Blackjack!</B></a>'
            elif score == 21:
                html += '&nbsp&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton"><B>Holding ('+ss+')</B></a>'
        elif player.isBusted():
            html += '&nbsp&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton"><B>Busted! ('+ss+')</B></a>'
        elif player.isHolding():
            html += '&nbsp&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton"><B>Holding ('+ss+')</B></a>'
    else:
        winner = game.winner()
        if winner is None:
            html += '&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton">Tied</a>'            
        elif winner is player:
            html += '&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton">Winner!</a>'
        else:
            html += '&nbsp&nbsp&nbsp&nbsp<a href="#" class="myButton">Loser...</a>'
              
    return html


"""
function to get the HTML for the game
"""
def getHTML():
    global game
                            
    score1 = game.getPlayer(1).getScore()
    score2 = game.getPlayer(2).getScore()

    buttoncss = '.myButton {box-shadow: 0px 10px 14px -7px #276873;background:lineargradient(to bottom, #599bb3 5%, #408c99 100%);background-color:#599bb3;border-radius:8px;display:inline-block;cursor:pointer;color:#ffffff;font-family:Arial;font-size:20px;font-weight:bold;padding:13px 32px;text-decoration:none;text-shadow:0px 1px 0px #3d768a;}.myButton:hover {background:linear-gradient(to bottom, #408c99 5%, #599bb3 100%);background-color:#408c99;}.myButton:active {position:relative;top:1px;}'
    msgcss = '.msg{color:#f0f0f0;font-family:Arial;font-size:20px;font-weight:bold;padding:13px 32px;}'
    html = '<head><style>body {background-color: green;}'+buttoncss+msgcss+'</style></head><body>'
    msg = ""
    done = ""
    if game.getResponseCode() > 299:
        msg = ' The card server reported an error. Code: '+str(game.getResponseCode())+' Message: '+game.getResponseText()
    html += '<a href="http://0.0.0.0:5000/deal" class="myButton">Deal!</a> <span class="msg">'+str(game.getRemaining())+' cards remaining in deck.'+msg+'</span>'

    for player in game.getPlayers():
        html += getLayout(player)
        
    return html
    
"""
route and function for the "GET" for '/' (home)
"""
@app.route('/', methods=['GET'])
def home():
    html = '<head><style>body {background-color: green;}</style></head>'
    html += '<p><p><p><center><h1><a href="http://0.0.0.0:5000/deal">Black Jack!</a></h1></center></p></p></p>'
    html += '<p><p><center>a rudimentary api for the game of blackjack</center></p></P><p><p><center>by Mark Stacy</center>'
    return html

"""
route and function for the "GET" for '/deal' (Deal button)
"""
@app.route('/deal', methods=['GET'])
def deal():
    global game
    
    game.reset()
    url = "https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1"
    r = requests.request("GET", url)
    game.setResponseCode(r.status_code)
    game.setResponseText(r.reason)
    if r.status_code < 300:
        j = r.json()
        game.setId(j["deck_id"])
        url = 'https://deckofcardsapi.com/api/deck/'+game.getId()+'/draw/?count=52'
        r = requests.request("GET", url)
        game.setResponseCode(r.status_code)
        game.setResponseText(r.reason)
        if r.status_code < 300:
            j = r.json()
            game.setDeck(j)
            num = 0
            while num < 4:
                card = game.draw()
                if card is not None:
                    if num % 2 == 0:
                        game.getPlayer(1).addCard(card)
                    else:
                        game.getPlayer(2).addCard(card)
                num += 1
    return getHTML()

"""
route and function for the "GET" for /hit (a player's 'Hit' button)
"""
@app.route('/hit', methods=['GET'])
def hit():
    global game
    player = game.getPlayer(int(request.args.get('player')))
    if player is not None:
        card = game.draw()
        if card is not None:
            player.addCard(card)
            return getHTML()
    flask.abort(404)


"""
route and function for the "GET" for /stay (a player's Stand button)
"""
@app.route('/stay', methods=['GET'])
def stay():
    global game
    player = game.getPlayer(int(request.args.get('player')))
    if player is not None:
        player.stay()
        return getHTML()
    flask.abort(404)

@app.errorhandler(404)
def player_not_found(error):
    return "<center><H1>404 - Bad request</H1></center>", 404
    
"""
route and function for the "GET" for /state (a non-integrated api)
"""
@app.route('/state', methods=['GET'])
def state():
    global game
    return game.getStateJSON()

"""
route and function for the "GET" for /resume (a non-integrated api)
"""
@app.route('/resume', methods=['GET'])
def resume():
    return getHTML()

# instatiate the game
game = Blackjack()

# run Flask
app.run(port=5000, threaded=True, host=('0.0.0.0'))