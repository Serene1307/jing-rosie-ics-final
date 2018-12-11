#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 15:21:00 2018

@author: rose
"""
import os


class Board():
    # initiate the board
    def __init__(self):
        self.cells = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
        
    #display the board
    def display(self):
        a = " %s | %s | %s \n " % (self.cells[1], self.cells[2], self.cells[3])
        a += "---------- \n"
        a += " %s | %s | %s \n " % (self.cells[4], self.cells[5], self.cells[6])
        a += "---------- \n"
        a += " %s | %s | %s \n " % (self.cells[7], self.cells[8], self.cells[9])
        return a
        
    # update board 
    def update_board(self, cell_no, player):
        if cell_no in [1,2,3,4,5,6,7,8,9] :
            # if cell not taken
            if self.cells[cell_no] == " ":
                self.cells[cell_no] = player
                return True
            # if the cell is already taken
            else:
                return False
        # if the number entered is not within 1-9
        else:
            return False
            
            
    # determine whether player is winner       
    def is_winner(self, player):
        if self.cells[1] == player and self.cells[2] == player and self.cells[3] == player:
            return True
     
        if self.cells[4] == player and self.cells[5] == player and self.cells[6] == player:
            return True
        
        if self.cells[7] == player and self.cells[8] == player and self.cells[9] == player:
            return True
        
        if self.cells[1] == player and self.cells[4] == player and self.cells[7] == player:
            return True
        
        if self.cells[2] == player and self.cells[5] == player and self.cells[8] == player:
            return True
        
        if self.cells[3] == player and self.cells[6] == player and self.cells[9] == player:
            return True
        
        if self.cells[1] == player and self.cells[5] == player and self.cells[9] == player:
            return True
        
        if self.cells[3] == player and self.cells[5] == player and self.cells[7] == player:
            return True
    
    #determine whether it is a tie game    
    def is_tie(self):
        used_cells = 0
        for cell in self.cells:
            if cell != " ":
                used_cells += 1
        if used_cells == 9:
            return True
        else:
            return False
        
   

