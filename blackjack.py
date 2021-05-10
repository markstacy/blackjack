import flask
from flask import request
import requests
import json


app = flask.Flask(__name__)
app.config["DEBUG"] = True

game = None

class Blackjack():
    def __init__(self, players = 2):
        self.players = Players()
        self.id = ""
        self.responseCode = 0
        self.responseText = ""
        self.over = False
        for i in range(players):
            self._addPlayer()
        self.deck = []
        
    def _addPlayer(self):
        self.players.addPlayer()
        
    def getPlayers(self):
        return self.players.getPlayers()
    
    def getPlayer(self, number):
        return self.players.getPlayer(number)
    
    def getPlayerCount(self):
        return self.players.getPlayerCount(self)
    
    def setId(self, id):
        self.id = id
        
    def getId(self):
        return self.id
    
    def setDeck(self, deck):
        for card in deck["cards"]:
            self.deck.append(card)
        
    def draw(self):
        if len(self.deck) > 0:
            return self.deck.pop(0)
        else:
            return None
            
    def getRemaining(self):
        return len(self.deck);
        
    def setResponseCode(self, responseCode):
        self.responseCode = responseCode
        
    def getResponseCode(self):
        return self.responseCode

    def setResponseText(self, responseText):
        self.responseText = responseText
        
    def getResponseText(self):
        return self.responseText
    
    def setOver(self, over):
        self.over = over
        
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
    
    def reset(self):
        self.players.reset()
        self.id = ""
        self.remaining = 0
        self.responseCode = 0
        self.responseText = ""
        self.over = False
        self.deck.clear()
        
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
                    
        
class Players():
    def __init__(self):
        self.players = []

    def addPlayer(self):
        self.players.append(Player(len(self.players)+1))
                            
    def getPlayer(self, number):
        if len(self.players) >= number - 1:
            return self.players[number-1]
        else:
            return None
                            
    def getPlayers(self):
        return self.players
                            
    def clear(self):
        self.players.clear()
        
    def getPlayerCount(self):
        return 
                            
    def reset(self):
        for player in self.players:
            player.reset()
        self.deck = []
                            
class Player():
    
    def __init__(self, number):
        self.number = number
        self.cards = []
        self.busted = False
        self.hold = False
        self.score = 0
        self.dirty = True
        
    def reset(self):
        self.cards.clear()
        self.busted = False
        self.hold = False
        self.score = 0
        self.dirty = False
        
    def getNumber(self):
        return self.number
    
    def addCard(self, card):
        self.cards.append(card)
        self.dirty = True
        
    def getCards(self):
        return self.cards
    
    def cardCount(self):
        return len(self.cards)
    
    def getScore(self):
        global game
        if self.dirty:
            self.score = 0
            aces = 0
            for card in self.cards:
                if card["value"].isdigit():
                    self.score += int(card["value"])
                elif card["value"][0] == 'A':
                    aces += 1
                else:
                    self.score += 10
            while aces > 0:
                aces -= 1
                if self.score + 11 + aces <= 21:
                    self.score += 11
                else:
                    self.score += 1
            if self.score > 21:
                self._busted()
                game.setOver(True)
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
    
def getLayout(player):
    # card layout
    global game
    score = player.getScore()
    ps = str(player.number)
    ss = str(score)
    if not game.isOver():
        href ='http://localhost:5000/hit?player='+ps
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
                html += '&nbsp&nbsp&nbsp&nbsp<a href="http://localhost:5000/hit?player='+ps+'"class="myButton">Hit Me!</a>'
                html += '&nbsp&nbsp&nbsp&nbsp<a href="http://localhost:5000/stay?player='+ps+'" class="myButton">Stand</a>'
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
    html += '<a href="http://localhost:5000/deal" class="myButton">Deal!</a> <span class="msg">'+str(game.getRemaining())+' cards remaining in deck.'+msg+'</span>'

    for player in game.getPlayers():
        html += getLayout(player)
        
    return html
    

@app.route('/', methods=['GET'])
def home():
    return '<h1><a href="http://localhost:5000/deal">Black Jack!</a></h1><p>A prototype API for the game of<b>Blackjack!</b>"</p>'

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

@app.route('/hit', methods=['GET'])
def hit():
    global game
    player = game.getPlayer(int(request.args.get('player')))
    card = game.draw()
    if card is not None:
        player.addCard(card)
    return getHTML()

@app.route('/stay', methods=['GET'])
def stay():
    global game
    game.getPlayer(int(request.args.get('player'))).stay()
    return getHTML()

game = Blackjack()

app.run()