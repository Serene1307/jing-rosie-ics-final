"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import solution_encrypt as encrypt
import random
import chat_server as cs

# =============================================================================
# def is_prime (integer):
#     for i in range (2, 32768):
#         if integer % i == 0 and i != integer:
#             return False 
#         elif i >= integer//2:
#             
#             return True
#         else:
#             continue
# prime = []
# for i in range(2, 32768):
#     if is_prime (i):
#         prime.append(i)
# =============================================================================
public_clock = 23
public_base = 5

#group key 存放在哪里 怎么access 怎么server无法access
class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.grp = cs.Server().group()
        # set my own private key
        self.private_key =  random.randint(1,1000)
        self.public_key = public_base ** self.private_key % public_clock
        peer_public_key = ""
        # dice 
        self.result = ''   # store my dice result
        self.roll_first = ''
        self.peer_result = ''  # store peer's dice result
        # TTT         
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
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        my_key = self.public_key
                        mysend(self.s, json.dumps({"action":"exchange_key", "from":"[" + self.me + "]", "message":my_key}))
                        peer_public_key = json.loads(peer_msg)["message"]
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
                        
                        
            ################# invite peer to a game ##################
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
              ##########################################################

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
                    self.state = S_CHATTING
                
            ############### peer invite me to a game ###########
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
             ##################################################  

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            
            if len(my_msg) > 0:     # my stuff going out
                
                # use the Diffie-Hellman key exchange formula
                shared_key = peer_public_key **  self.private_key % public_clock
                # calculate the offset to encrypt my message
                offset = int(shared_key) %26
                my_msg = encrypt.generate_encrypted_msg(offset, my_msg)
              
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg[0] == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
               
                #  get the group encrypted message
                encrypted_msg = peer_msg["message"] 
                # then calculate the offset according to the group public key
                shared_key = peer_public_key **  self.private_key % public_clock
                offset = int(shared_key) % 26
                decrypted_msg = encrypt.decrypt_msg(offset, encrypted_msg)
                
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
     
                    self.out_msg += peer_msg["from"] + decrypted_msg


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                
#==============================================================================
# Start GAMING, 'q' for quit
# This is event handling instate "S_GAMING"
#==============================================================================
        elif self.state == S_GAMING_DICE:
            
         ########## roll a dice to determine who goes first########
         
            if len(my_msg) > 0:
                if my_msg == "q":
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ""

                if my_msg == "d" or "D":
                    self.result = str(random.randint(1,6))
                    self.out_msg += "You got " + self.result + ".\n"
                    mysend(self.s, json.dumps({"action":"dice","from": self.me, "result":self.result}))
                    if self.roll_first == False:
                        if self.peer_result > self.result:
                            self.out_msg += self.peer + " got " + self.peer_result + ".\n"
                            self.out_msg += self.peer + " goes first!\n"
                            self.state = S_GAMING_WAITING
                            self.go_first = False
                            self.xo = "O"
                            os.system("clear")
                            self.out_msg += "You are O. " + self.peer + " is X.\n"
                            self.out_msg += "Waiting for " + self.peer + " to make a move...\n"
                        elif self.result == self.peer_result:
                            self.out_msg += "opps, same results. Throw again!\n"
                            self.result = ''
                            self.peer_result = ''
                            self.roll_first = ''
                        else:
                            self.out_msg += self.peer + " got " + self.peer_result + ".\n"
                            self.out_msg += "You go first!\n"
                            self.state = S_GAMING_MOVING
                            self.go_first = True 
                            self.xo = "X" 
                            os.system("clear")
                            self.out_msg += "You are X. " + self.peer + " is O.\n" 
                            self.out_msg += "Please choose 1 - 9. > \n"                                  
                    
                   
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                #print(peer_msg)
                if peer_msg["action"] == "game":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += "You are disconnected from " + self.peer + "\n"
                elif peer_msg["action"] == "dice":
                    self.peer_result = peer_msg["result"]
                    self.out_msg += peer_msg["from"] + " got " + self.peer_result + "\n"
                    if self.result == "":
                        self.roll_first = False
                        self.out_msg += "Waiting for you to roll...\n"
                    else:
                        self.roll_first = True
                        if self.result < self.peer_result:
                            self.out_msg += "You got " + self.result + ".\n"
                            self.out_msg += peer_msg["from"] + " goes first!\n"
                            self.state = S_GAMING_WAITING
                            self.go_first = False
                            self.xo = "O"
                            os.system("clear")
                            self.out_msg += "You are O. " + self.peer + " is X.\n"
                            self.out_msg += "Waiting for " + self.peer + " to make a move...\n"
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
                            self.out_msg += "Please choose 1 - 9. > \n"
                        
                
            if self.state == S_LOGGEDIN:
                self.out_msg += menu    
                
#============================================================================                
        elif self.state == S_GAMING_MOVING:
            #os.system("clear")  
            #self.board = TicTacToe.Board()
            #print(self.board)
            #print(self.board.display())
            #os.system("clear")
            if len(my_msg) > 0:
                if my_msg == "q":
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ""
                else:    
                    mysend(self.s, json.dumps({"action":"move","from": self.xo, "position": my_msg}))   
                    if self.board.update_board(int(my_msg), self.xo) == True:
                        os.system("clear")
                        print(self.board.display())
                        self.state = S_GAMING_WAITING
                        self.out_msg += "Waiting for " + self.peer + " to move..."
                    else:
             
                        self.out_msg += "Invalid input! Please enter again!\n"
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                #print(peer_msg)
                if peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += "You are disconnected from " + self.peer + "\n"
            
            if self.state == S_LOGGEDIN:
                self.out_msg += menu                 
                
        
        elif self.state == S_GAMING_WAITING:
            #os.system("clear")  
            
            if len(my_msg) > 0:
                if my_msg == "q":
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ""
                    
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                #print(peer_msg)
                if peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += "You are disconnected from " + self.peer
                elif peer_msg["action"] == "move":
                    position = peer_msg["position"]
                    xo = peer_msg["from"]
                    if self.board.update_board(int(position), xo) == True:
                        os.system("clear")
                        print(self.board.display())
                        self.state = S_GAMING_MOVING
                        self.out_msg += "Please choose 1 - 9. > \n"
                    else:
                        self.out_msg += "Waiting for " + self.peer + " to move..."
                        
            if self.state == S_LOGGEDIN:
                self.out_msg += menu        
            
            pass
        
        
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
    
        
        return self.out_msg
