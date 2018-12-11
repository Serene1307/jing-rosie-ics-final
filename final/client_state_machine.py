"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import solution_encrypt as encrypt
import random
import TicTacToe
import os


'''Our secure messaging works in a way that when "I" am connected with a peer, "I" will get my group public keys immediately 
so as to encrypt my message based on my own private key, and meanwhile, send my public key along with my message
to other group members so that they could decrypt my message; When "I" receive a message from the group chat, "I" first
retrieve the peer public key which comes with the message (unique to the sender) so that I could use this key along 
with my group private key to decrypt the peer's message.'''

'''
Our TicTacToe game works in this way:
After peer and I connect in a game, we first roll a dice to determine who goes first in the game.
Then the game starts. Each of us takes turns to take a position in the grid by entering a number between 1 and 9.
The board is shown as follows:
        
    1 | 2 | 3 
    ----------
    4 | 5 | 6 
    ----------
    7 | 8 | 9 
    
Possible results of the game are (1) I win; (2) peer wins; (3)tie
After one game is complete, the system would ask whether the players want to play again
'''

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        # set my own private key
        self.public_base = 0
        self.public_clock =0
        self.private_key =  random.randint(1,1000)
        self.public_key = 0
        self.peer_public_key = 0
        self.group_public_key = 0
        self.group_private_key = 0
        self.shared_key = 0
        self.offset = 0
        # store results of dice rolls for me and peer 
        self.result = ''  
        self.roll_first = ''
        self.peer_result = ''  
        # store info for TicTacToe game        
        self.go_first = ''
        self.board = TicTacToe.Board()
        self.xo = ''
        self.my_position = ''
        self.peer_position = ''
    
        
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    # connect and play game
    def game_to(self, peer):
        msg = json.dumps({"action":"game", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot game to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        # when we are connected, we immediately request the base, clock and my group public/private key.
                        mysend(self.s, json.dumps({"action":"exchange_key"}))
                        received = json.loads(myrecv(self.s))["keys"]
                        self.group_public_key = received [0]
                        self.group_private_key = received [1]
                        self.public_base = received [2]
                        self.public_clock = received [3]
                        self.public_key = (self.public_base ** self.private_key) % self.public_clock
                        self.state = S_CHATTING
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                               
                # I invite peer to a game 
                elif my_msg[0] == "g":
                    os.system("clear")
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.game_to(peer) == True:
                        self.state = S_GAMING_DICE
                        self.out_msg += 'Connect to ' + peer + '. Game away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        self.out_msg += '''\nWelcome to Tic-Tac-Toe!\n
                        1 | 2 | 3 
                        ----------
                        4 | 5 | 6 
                        ----------
                        7 | 8 | 9 
                        \nLet's Start!\n\n '''
                        self.out_msg += "Please enter D to roll a dice.\n"
                        self.out_msg += "Whoever gets a larger number goes first!\n"
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
            
                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    # when we are connected, we immediately request the group public key.
                    mysend(self.s, json.dumps({"action":"exchange_key"}))
                    received = json.loads(myrecv(self.s))["keys"]
                    self.group_public_key = received [0]
                    self.group_private_key = received [1]
                    self.public_base = received [2]
                    self.public_clock = received [3]
                    self.public_key = (self.public_base ** self.private_key) % self.public_clock
                    self.state = S_CHATTING                    
                    
                
                # peer invite me to a game 
                if peer_msg["action"] == "game":
                    os.system("clear")
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Game away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.out_msg += '''\nWelcome to Tic-Tac-Toe!\n
                        1 | 2 | 3 
                        ----------
                        4 | 5 | 6 
                        ----------
                        7 | 8 | 9 
                        \nLet's Start!\n\n '''
                    self.state = S_GAMING_DICE
                    self.out_msg += "Please enter D to roll a dice.\n"
                    self.out_msg += "Whoever gets a larger number goes first!\n"
               

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================



        elif self.state == S_CHATTING:
            
            if len(my_msg) > 0:     # my stuff going out
                # use the Diffie-Hellman key exchange formula
                self.shared_key = (self.group_public_key **  self.private_key) % self.public_clock
                # calculate the offset to encrypt my message
                self.offset = int(self.shared_key) %26
                my_encrypted_msg = encrypt.generate_encrypted_msg(self.offset, my_msg)
                 # when I am sending out my message, I will send out my public key as well, so group members can decrypt my message
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_encrypted_msg,"from_name_public_key":self.public_key}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    
                peer_msg = json.loads(peer_msg)
              
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
                    # first we retrieve the peer's public key
                    self.peer_public_key = peer_msg["from_name_public_key"] 
                    #  get the peer's encrypted message based on my group own private key
                    self.shared_key = (self.peer_public_key **  self.group_private_key) % self.public_clock
                    # calculate the offset to encrypt my message
                    self.offset = int(self.shared_key) %26
                    encrypted_msg = peer_msg["message"]
                    # then calculate the offset according to the group public key
                    
                    decrypted_msg = encrypt.decrypt_msg(self.offset, encrypted_msg)
                    self.out_msg += peer_msg["from"] + decrypted_msg


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                
#==============================================================================
# Start GAMING, 'q' for quit
# This is event handling instate "S_GAMING_DICE"
# Peer and I will roll a dice. Whoever gets a bigger number starts first.
# The one that starts first is "X". The one that starts later is "O"
#==============================================================================
        elif self.state == S_GAMING_DICE:
            
            # roll a dice to determine who goes first         
            if len(my_msg) > 0:
                if my_msg == "q":
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    
                # enter "d" or "D" to roll a dice
                elif my_msg == "d" or my_msg == "D":
                    self.result = str(random.randint(1,6))
                    self.out_msg += "You got " + self.result + ".\n"
                    mysend(self.s, json.dumps({"action":"dice","from": self.me, "result":self.result}))
                    # when peer hasn't rolled yet
                    if self.peer_result == '':
                        self.roll_first = True
                        self.out_msg += "Waiting for " + self.peer + " to roll...\n"
                    # when peer already rolled
                    else:
                        self.roll_first = False
                        # if peer rolled larger number than me, peer goes first
                        if self.peer_result > self.result:
                            self.out_msg += self.peer + " got " + self.peer_result + ".\n"
                            self.out_msg += self.peer + " goes first!\n"
                            self.state = S_GAMING_WAITING
                            self.go_first = False
                            self.xo = "O"
                            os.system("clear")
                            self.out_msg += "You are O. " + self.peer + " is X.\n"
                            self.out_msg += '''  
                            1 | 2 | 3 
                            ----------
                            4 | 5 | 6 
                            ----------
                            7 | 8 | 9 
                            \n'''
                            self.out_msg += "Waiting for " + self.peer + " to make a move...\n"
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''
                        # if we both roll the same number, roll again
                        elif self.result == self.peer_result:
                            self.out_msg += "opps, same results. Throw again!\n"
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''
                        # if I rolled larger number than peer, I goes first
                        else:
                            self.out_msg += self.peer + " got " + self.peer_result + ".\n"
                            self.out_msg += "You go first!\n"
                            self.state = S_GAMING_MOVING
                            self.go_first = True 
                            self.xo = "X" 
                            os.system("clear")
                            self.out_msg += "You are X. " + self.peer + " is O.\n" 
                            self.out_msg += '''  
                            1 | 2 | 3 
                            ----------
                            4 | 5 | 6 
                            ----------
                            7 | 8 | 9 
                            \n'''
                            self.out_msg += "Please choose a number from 1 - 9. > \n" 
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''                                 
                    
                   
            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)

                if peer_msg["action"] == "game":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += "You are disconnected from " + self.peer + "\n"
                
                # receive peer's dice result
                elif peer_msg["action"] == "dice":
                    self.peer_result = peer_msg["result"]
                    self.out_msg += peer_msg["from"] + " got " + self.peer_result + "\n"
                    # if I haven't rolled yet
                    if self.result == "":
                        self.roll_first = False
                        self.out_msg += "Waiting for you to roll...\n"
                    # if I already rolled
                    else:
                        self.roll_first = True
                        
                        # compare my dice result and peer's dice result and determine who goes first
                        if self.result < self.peer_result:
                            self.out_msg += "You got " + self.result + ".\n"
                            self.out_msg += peer_msg["from"] + " goes first!\n"
                            self.state = S_GAMING_WAITING
                            self.go_first = False
                            self.xo = "O"
                            os.system("clear")
                            self.out_msg += "You are O. " + self.peer + " is X.\n"
                            self.out_msg += '''  
                            1 | 2 | 3 
                            ----------
                            4 | 5 | 6 
                            ----------
                            7 | 8 | 9 
                            \n'''
                            self.out_msg += "Waiting for " + self.peer + " to make a move...\n"
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''
                        elif self.result == self.peer_result:
                            self.out_msg += "opps, same results. Throw again!\n"
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''
                        else:
                            self.out_msg += "You got " + self.result + ".\n"
                            self.out_msg += "You go first!\n"
                            self.state = S_GAMING_MOVING
                            self.go_first = True
                            self.xo = "X"
                            os.system("clear")
                            self.out_msg += "You are X. " + self.peer + " is O.\n"
                            self.out_msg += '''  
                            1 | 2 | 3 
                            ----------
                            4 | 5 | 6 
                            ----------
                            7 | 8 | 9 
                            \n'''
                            self.out_msg += "Please choose a number from 1 - 9. > \n"
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''
                        
                
            if self.state == S_LOGGEDIN:
                self.out_msg += menu    
                
#==============================================================================
# Start GAMING, 'q' for quit
# This is event handling instate "S_GAMING_MOVING" and "S_GAMING_WAITING"
# When playing TicTacToe, there are two states:
# whether you are making a move, or you are waiting for your peer to make a move
#==============================================================================     
        # If it's my turn to make a move
        elif self.state == S_GAMING_MOVING:
            
            if len(my_msg) > 0:
                # quit the game
                if my_msg == "q":
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ""
                else:
                    # if enter alphabet
                    if my_msg.isalpha() == True:
                        self.out_msg += "Invalid input! Please enter again!\n"                        
                    # if I enter a valid move number, update my move on my board                         
                    elif self.board.update_board(int(my_msg), self.xo) == True:
                        os.system("clear")
                        self.out_msg += "You are " + self.xo + ".\n"
                        print(self.board.display())
                        # check whether I win
                        if self.board.is_winner(self.xo) == True:
                            self.out_msg += "You win!\n"
                            mysend(self.s,json.dumps({"action":"move","from": self.xo, "position": my_msg, "status":"win"}))
                            self.state = S_GAMING_AGAIN
                            self.out_msg += "Play again?(Y/N)\n"
                            self.board = TicTacToe.Board()
                        # check whether it is a tie
                        elif self.board.is_tie() == True:
                            self.out_msg += "It's a tie!\n"
                            mysend(self.s,json.dumps({"action":"move","from": self.xo, "position": my_msg, "status":"tie"}))
                            self.state = S_GAMING_AGAIN
                            self.out_msg += "Play again?(Y/N)\n"
                            self.board = TicTacToe.Board()
                        # send me move to peer, continue playing
                        else:
                            mysend(self.s,json.dumps({"action":"move","from": self.xo, "position": my_msg, "status":""}))
                            self.state = S_GAMING_WAITING
                            self.out_msg += "Waiting for " + self.peer + " to move..."
                    # if I enter an invalid move number(either the cell has already been taken or the number is not within 1-9)
                    else:
                        self.out_msg += "Invalid input! Please enter again!\n"
                        
                    
            if len(peer_msg) > 0:   
                peer_msg = json.loads(peer_msg)
                #print(peer_msg)
                if peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += "You are disconnected from " + self.peer + "\n"
            
            if self.state == S_LOGGEDIN:
                self.out_msg += menu                 
                
        # If it's my peer's turn to make a move, I will be waiting
        elif self.state == S_GAMING_WAITING:                         
            if len(my_msg) > 0:
                # quit the game 
                if my_msg == "q":
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ""
                    
            if len(peer_msg) > 0:    
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += "You are disconnected from " + self.peer + '\n'
                # receiving peer's move and update peer's move on my board
                elif peer_msg["action"] == "move":
                    position = peer_msg["position"]
                    xo = peer_msg["from"]
                    if self.board.update_board(int(position), xo) == True:
                        os.system("clear")
                        self.out_msg += "You are " + self.xo + ".\n"
                        print(self.board.display())
                        # check whether peer wins
                        if peer_msg["status"] == "win":
                            self.out_msg += "You lose!\n"
                            self.out_msg += "Play again?(Y/N)\n"
                            self.state = S_GAMING_AGAIN
                            self.board = TicTacToe.Board()
                        # check whether it is a tie
                        elif peer_msg["status"] == "tie":
                            self.out_msg += "It's a tie!\n"
                            self.out_msg += "Play again?(Y/N)\n"
                            self.state = S_GAMING_AGAIN 
                            self.board = TicTacToe.Board()
                        # continue the game
                        else:
                            self.state = S_GAMING_MOVING
                            self.out_msg += "Please choose a number from 1 - 9. > \n"
                    else:
                        self.out_msg += "Waiting for " + self.peer + " to move..."
                
                        
            if self.state == S_LOGGEDIN:
                self.out_msg += menu        
            
            
#==============================================================================
# This is event handling instate "S_GAMING_AGAIN"
# Ask users whether want to play again
#==============================================================================     
        elif self.state == S_GAMING_AGAIN:
            
            if len(my_msg) > 0:
                # if don't want to play again
                if my_msg == "n" or my_msg == "N":
                    mysend(self.s, json.dumps({"action":"game_again","from": self.me, "status": "no"}))
                    self.out_msg += "You are disconnected from " + self.peer + '\n'
                    self.state = S_LOGGEDIN
                    self.peer = ''
                # if want to play again
                elif my_msg == "y" or my_msg == "Y":
                    mysend(self.s, json.dumps({"action":"game_again","from": self.me, "status": "yes"}))                     
                    os.system("clear")
                    self.out_msg += '''\nWelcome to Tic-Tac-Toe!\n
                        1 | 2 | 3 
                        ----------
                        4 | 5 | 6 
                        ----------
                        7 | 8 | 9 
                        \nLet's Start!\n\n'''
                    self.state = S_GAMING_DICE    
                    self.out_msg += "Please enter D to roll a dice.\n"
                    self.out_msg += "Whoever gets a larger number goes first!\n"
                    
            if len(peer_msg) > 0:    
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "game_again":
                    # if peer doesn't want to play again
                    if peer_msg["status"] == "no":
                        self.state = S_LOGGEDIN
                        self.out_msg += "You are disconnected from " + self.peer
                    # if peer wants to play again
                    elif peer_msg["status"] == "yes":                
                        os.system("clear")
                        self.out_msg += '''\nWelcome to Tic-Tac-Toe!\n
                            1 | 2 | 3 
                            ----------
                            4 | 5 | 6 
                            ----------
                            7 | 8 | 9 
                            \nLet's Start!\n\n '''
                        self.state = S_GAMING_DICE
                        self.out_msg += "Please enter D to roll a dice.\n"
                        self.out_msg += "Whoever gets a larger number goes first!\n"
                    
            if self.state == S_LOGGEDIN:
                self.out_msg += menu         
                    
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
    
        
        return self.out_msg
