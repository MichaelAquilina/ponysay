#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay.py - POC of ponysay in python
Copyright (C) 2012 Elis "etu" Axelsson, Mattias "maandree" Andrée

License: WTFPL
'''

import argparse
import os
import sys
import random
from subprocess import Popen, PIPE


'''
The version of ponysay
'''
VERSION = '2.0-alpha'


'''
The directory where ponysay is installed, this is modified when building with make
'''
INSTALLDIR = '/usr'


'''
The user's home directory
'''
HOME = os.environ['HOME']


'''
The directories where pony files are stored, ttyponies/ are used if the terminal is Linux VT (also known as TTY)
'''
ponydirs = []
if os.environ['TERM'] == 'linux':  _ponydirs = [HOME + '/.local/share/ponysay/ttyponies/',  INSTALLDIR + '/share/ponysay/ttyponies/']
else:                              _ponydirs = [HOME + '/.local/share/ponysay/ponies/',     INSTALLDIR + '/share/ponysay/ponies/'   ]
for ponydir in _ponydirs:
    if os.path.isdir(ponydir):
        ponydirs.append(ponydir)


'''
The directories where quotes files are stored
'''
quotedirs = []
_quotedirs = [HOME + '/.local/share/ponysay/quotes/',  INSTALLDIR + '/share/ponysay/quotes/']
for quotedir in _quotedirs:
    if os.path.isdir(quotedir):
        quotedirs.append(quotedir)



'''
Argument parsing
'''
parser = argparse.ArgumentParser(description = 'Ponysay, like cowsay with ponies')

parser.add_argument('-v', '--version', action = 'version',    version = '%s %s' % ('ponysay', VERSION))
parser.add_argument('-l', '--list',    action = 'store_true', dest = 'list',     help = 'list pony files')
parser.add_argument('-L', '--altlist', action = 'store_true', dest = 'linklist', help = 'list pony files with alternatives')
parser.add_argument(      '--quoters', action = 'store_true', dest = 'quoters',  help = 'list ponies with quotes (visible in -l and -L)')  # for shell completions
parser.add_argument(      '--onelist', action = 'store_true', dest = 'onelist',  help = 'list pony files in one columns')                  # for shell completions
parser.add_argument('-f', '--pony',    action = 'append',     dest = 'pony',     help = 'select a pony (either a file name or a pony name)')
parser.add_argument('message', nargs = '?', help = 'message to ponysay')

args = parser.parse_args()


'''
This is the mane class of ponysay
'''
class ponysay():
    '''
    Starts the part of the program the arguments indicate
    '''
    def __init__(self, args):
        if   args.list:      self.list()
        elif args.linklist:  self.linklist()
        elif args.quoters:   self.quoters()
        elif args.onelist:   self.onelist()
        else:                self.print_pony(args)
    
    
    '''
    Returns one .pony-file with full path, names is filter for names, also accepts filepaths
    '''
    def __getponypath(self, names = None):
        ponies = {}
        
        if not names == None:
            for name in names:
                if os.path.isfile(name):
                    return name
        
        for ponydir in ponydirs:
            for ponyfile in os.listdir(ponydir):
                pony = ponyfile[:-5]
                if pony not in ponies:
                    ponies[pony] = ponydir + ponyfile
        
        if names == None:
            names = list(ponies.keys())
        
        return ponies[names[random.randrange(0, len(names))]]
    
    
    '''
    Returns a set with all ponies that have quotes and are displayable
    '''
    def __quoters(self):
        quotes = []
        quoteshash = set()
        _quotes = []
        for quotedir in quotedirs:
            _quotes += [item[:item.index('.')] for item in os.listdir(INSTALLDIR + '/share/ponysay/quotes/')]
        for quote in _quotes:
            if not quote == '':
                if not quote in quoteshash:
                    quoteshash.add(quote)
                    quotes.append(quote)
        
        ponies = set()
        for ponydir in ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        if ('+' + p + '+') in ('+' + quote + '+'):
                            if not p in ponies:
                                ponies.add(p)
        
        return ponies
    
    
    '''
    Returns a list with all (pony, quote file) pairs
    '''
    def __quotes(self):
        quotes = []
        for quotedir in quotedirs:
            quotes += [quotedir + item for item in os.listdir(quotedir)]
        rc = []
        
        for ponydir in ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        q = quote[quote.rindex('/') + 1:]
                        if ('+' + p + '+') in ('+' + q + '+'):
                            rc.append((p, quote))
        
        return rc
    
    
    '''
    Lists the available ponies
    '''
    def list(self):
        termsize = Popen(['stty', 'size'], stdout=PIPE).communicate()[0].decode('utf8', 'replace')[:-1].split(' ')
        termsize = [int(item) for item in termsize]
        
        quoters = self.__quoters()
        
        for ponydir in ponydirs: # Loop ponydirs
            print('\033[1mponyfiles located in ' + ponydir + '\033[21m')
            
            ponies = os.listdir(ponydir)
            ponies = [item[:-5] for item in ponies] # remove .pony from file name
            ponies.sort()
            
            width = len(max(ponies, key = len)) + 2 # Get the longest ponyfilename lenght + 2 spaces
            
            x = 0
            for pony in ponies:
                spacing = ' ' * (width - len(pony))
                print(('\033[1m' + pony + '\033[21m' if (pony in quoters) else pony) + spacing, end='') # Print ponyfilename
                x += width
                if x > (termsize[1] - width): # If too wide, make new line
                    print()
                    x = 0
                    
            print('\n');
    
    
    '''
    Lists the available ponies with alternatives inside brackets
    '''
    def linklist(self):
        termsize = Popen(['stty', 'size'], stdout=PIPE).communicate()[0].decode('utf8', 'replace')[:-1].split(' ')
        termsize = [int(item) for item in termsize]
        
        quoters = self.__quoters()
        
        for ponydir in ponydirs: # Loop ponydirs
            print('\033[1mponyfiles located in ' + ponydir + '\033[21m')
            
            files = os.listdir(ponydir)
            files = [item[:-5] for item in files] # remove .pony from file name
            files.sort()
            pairs = [(item, os.readlink(ponydir + item + '.pony') if os.path.islink(ponydir + item + '.pony') else '') for item in files]
            
            ponymap = {}
            for pair in pairs:
                if pair[1] == '':
                    if pair[0] not in ponymap:
                        ponymap[pair[0]] = []
                else:
                    target = pair[1][:-5]
                    if '/' in target:
                        target = target[target.rindex('/') + 1:]
                    if target in ponymap:
                        ponymap[target].append(pair[0])
                    else:
                        ponymap[target] = [pair[0]]
            
            width = 0
            ponies = []
            widths = []
            for pony in ponymap:
                w = len(pony)
                item = '\033[1m' + pony + '\033[21m' if (pony in quoters) else pony
                syms = ponymap[pony]
                if len(syms) > 0:
                    w += 2 + len(syms)
                    item += ' ('
                    first = True
                    for sym in syms:
                        w += len(sym)
                        if not first:
                            item += ' '
                        else:
                            first = False
                        item += '\033[1m' + sym + '\033[21m' if (sym in quoters) else sym
                    item += ')'
                ponies.append(item)
                widths.append(w)
                if width < w:
                    width = w
            
            width += 2;
            x = 0
            index = 0
            for pony in ponies:
                spacing = ' ' * (width - widths[index])
                index += 1
                print(pony + spacing, end='') # Print ponyfilename
                x += width
                if x > (termsize[1] - width): # If too wide, make new line
                    print()
                    x = 0
            
            print('\n');
    
    
    '''
    Lists with all ponies that have quotes and are displayable
    '''
    def quoters(self):
        last = ""
        ponies = []
        for pony in self.__quoters():
            ponies.append(pony)
        ponies.sort()
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    '''
    Lists the available ponies one one column without anything bold
    '''
    def onelist(self):
        last = ""
        ponies = []
        for ponydir in ponydirs: # Loop ponydirs
            ponies += os.listdir(ponydir)
        ponies = [item[:-5] for item in ponies] # remove .pony from file name
        ponies.sort()
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    def print_pony(self, args):
        if args.message == None:
            msg = sys.stdin.read().strip()
        else:
            msg = args.message
        
        pony = self.__getponypath(args.pony)
        
        os.system('cowsay -f ' + pony + ' \'' + msg + '\'')




'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    ponysay(args)
