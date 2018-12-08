#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 15:21:00 2018

@author: rose
"""
import os


class Board():
    def __init__(self):
        self.cells = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]

    def display(self):
        a = " %s | %s | %s \n " % (self.cells[1], self.cells[2], self.cells[3])
        a += "---------- \n"
        a += " %s | %s | %s \n " % (self.cells[4], self.cells[5], self.cells[6])
        a += "---------- \n"
        a += " %s | %s | %s \n " % (self.cells[7], self.cells[8], self.cells[9])
        return a
        
     
    def update_board(self, cell_no, player):
        if cell_no in [1,2,3,4,5,6,7,8,9] :
            if self.cells[cell_no] == " ":
                self.cells[cell_no] = player
                return True
            else:
                #print("Invalid input! Please enter again!")
                return False
        else:
            #print("Invalid input! Please enter again!")
            return False
            
            
            
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
        
    def is_tie(self):
        used_cells = 0
        for cell in self.cells:
            if cell != " ":
                used_cells += 1
        if used_cells == 9:
            return True
        else:
            return False
                
        
    def reset(self):
        self.cells = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
        

def print_header():
    return '''\nWelcome to Tic-Tac-Toe!\n"
             1 | 2 | 3 
            ------------
             4 | 5 | 6 
            ------------
             7 | 8 | 9 
            \nLet's Start!\n '''   
        
def refresh_screen():
        
        os.system("clear")
#        print_header()
#        print("\n")
    
        Board().display()


