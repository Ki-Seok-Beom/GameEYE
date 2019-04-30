# Load Python Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from time import time
import tensorflow
from tensorflow import keras
from datetime import datetime
import progressbar
from multiprocessing import Pool
import time
import sys
import os
import collections
import math
from math import sqrt
import csv as csvpackage
import re

from functools import reduce
from itertools import groupby
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException




# Ŭ???? ????
class Player():
    eye_score = 0
    vision_score = 0
    fight_score = 0
    object_score = 0
#
    growth_score = 0
    roaming_score = 0
    care_score = 0
    final_score = 0
#
    
    def __init__ (self, idx, summonerId, name,  lane, champ="", object_infos = "",fight="",vision = "",growth="",roaming="",care="",final=""):
        self.idx = idx
        self.summonerId = summonerId
        self.name = name
        self.champ = champ
        self.lane = lane
        
        self.object_infos = object_infos
        self.fight = fight
        self.vision = vision
        
        self.growth = growth
        self.roaming = roaming
        self.care = care
        
        self.final = final
    
    def get_idx(self):
        return self.idx
    
    def get_summonerId(self):
        return self.summonerId
    
    def get_basic(self):
        return [self.champ, self.lane, self.name]
        
    def get_vision(self):
        return self.vision
    
    def get_fight(self):
        return self.fight
#
    def get_final(self):
        return self.final
    def get_all(self):
        return [self.name, self.champ, self.object_score, self.fight_score, \
                self.vision_score,self.growth_score, self.roaming_score,self.care_score, self.final_score]
#

    def idx2champ(self, idx):
        return self.champ
    
    def set_champ(self, champ):
        self.champ = champ
    
    def set_vision(self, vision):
        self.vision = vision
    
    def set_fight(self, fight):
        self.fight = fight
    
    def set_object(self, object_infos):
        self.object_infos = object_infos
#        
    def set_growth(self, growth):
        self.growth = growth
        
    def set_roaming(self, roaming):
        self.roaming = roaming
    
    def set_care(self, care):
        self.care = care
        
    def set_final(self, final):
        self.final = final
#
    def set_GS(self, growth_score):
        self.growth_score = growth_score
    
    def set_RS(self, roaming_score):
        self.roaming_score = roaming_score
    
    def set_CS(self, care_score):
        self.care_score = care_score
        
    def set_LS(self, final_score):
        self.final_score = final_score
#

    def set_VS(self, vision_score):
        self.vision_score = vision_score
    
    def set_FS(self, fight_score):
        self.fight_score = fight_score
    
    def set_OS(self, object_score):
        self.object_score = object_score
        
    def calculate_set_kda(self, total_kill):
        kills = self.fight['kills']
        assists = self.fight['assists']
        deaths = self.fight['deaths']
        
        if deaths == 0 :
            self.fight['kda'] = np.round((kills + assists) *1.2,2)
        else:
            self.fight['kda'] = np.round((kills + assists) / deaths,2)
            
        self.fight['kp'] = np.round(((kills + assists) / total_kill) * 100,2)
#         print('kp', self.fight['kp'], 'kda', self.fight['kda'])
    
    def print_idx(self):
        print(self.idx)
   
    def print_champ(self):
        print(self.idx, self.champ)
        
    def print_basic(self):
        print(self.idx, self.champ, self.lane, self.name)
    
    def print_vision_all(self):
        print(self.idx, self.champ, self.lane, self.vision_score, self.vision)
        
    def print_fight_all(self):
        print(self.idx, self.champ, self.lane, self.fight_score, self.fight)

    def print_object_all(self):
        print(self.idx, self.champ, self.lane, self.object_score, self.object_infos)
#
    def print_all(self):
        print(self.idx, self.champ, self.lane, self.object_score, self.fight_score, self.vision_score,self.growth_score, self.roaming_score,self.care_score, self.final_score)
#
    
        
class Team():
    
    def __init__(self, win, top, jun, mid, bot, sup):
        if win == 'Fail':
            self.win = False
        else:
            self.win = True
#         self.win = win
        self.top = top
        self.jun = jun
        self.mid = mid
        self.bot = bot
        self.sup = sup   
        self.sumoners = [top, jun, mid, bot, sup]
    def get_win(self):
        return self.win
        
    def get_champions(self):
        return [s.get_basic()[0] for s in self.sumoners]
    
    def get_names(self):
        return [s.get_basic()[-1] for s in self.sumoners]
        
    def get_all_player(self):
        return self.sumoners
        
    def print_lane(self):
        self.top.print_idx()
        self.jun.print_idx()
        self.mid.print_idx()
        self.bot.print_idx()
        self.sup.print_idx()
    
    def print_basic(self):
        print ("Win", self.win)
        for player in self.sumoners:
            player.print_basic()
#    
    def print_player_all(self):
        for player in self.sumoners:
            player.print_all()
            
    def get_player_all(self):
        for player in self.sumoners:
            player.get_all()
#


# ??ƿ??Ƽ ???
def reduceByKey(func, iterable): 
    """Reduce by key.
    Equivalent to the Spark counterpart
    Inspired by http://stackoverflow.com/q/33648581/554319
    1. Sort by key
    2. Group by key yielding (key, grouper)
    3. For each pair yield (key, reduce(func, last element of each grouper))
    """
    get_first = lambda p: p[0]
    get_second = lambda p: p[1]
    # iterable.groupBy(_._1).map(l => (l._1, l._2.map(_._2).reduce(func)))
    return map(
    lambda l: (l[0], reduce(func, map(get_second, l[1]))),
            groupby(sorted(iterable, key=get_first), get_first)
        )

def normalize_value(value, min_value, max_value):
    result = np.round(( (value - min_value) / (max_value - min_value))*100, 2) 

    if value > max_value:
#         print(result, max_value)
        result = 100
    elif value < min_value:
        result = 0
    return result

# ????Ϳ????

def Find_Champion_Info(watcher, region, champ, mode, verbose=1): 
    '''
    This function is searching champion information comfortably
    
    :param string region:                               The region to execute this request on
    :param long champ:                            The Champion key or name
    :param string mode "name" or "id" :        Input param mode
    :param int verbose :                                Information depth  - 1 : name and id  / 2 : full information
    
    :returns: Champion Information
    '''
    champion_data = watcher.data_dragon.champions('9.4.1', locale='ko_KR')['data']
    infos = "information"
    if mode == "name":
        for k,v in champion_data.items():
            if v['name'] == champ:
                infos = v
    elif mode == "key":
        for k,v in champion_data.items():
            if v['key'] == champ:
                infos = v
    else:
        print(" The mode is wrong. ")
        return 0

    if verbose == 1:
        out = {'name' : infos['name'], 'key' : infos['key'], 'id' : infos['id']}
    elif verbose == 2:
        out = infos
    
    return out

def distance(position, position2 = {'x':0,'y':14980}):
    return np.sqrt(np.power((position['x'] - position2['x']),2) + np.power((position['y'] - position2['y']),2))

def make_team(win, Identities,participants, team_1, champion_dict):
    # spell ????Ÿ??11
    
    jungle_participants = sorted(team_1, key = lambda x: x[1]['jungleMinionsKilled'], reverse=True)
    used_player = [jungle_participants[0][1]['participantId']]
    
    sorted_distance = sorted(jungle_participants[1:], key = lambda x: x[1]['dis'])
    jun_idx = jungle_participants[0][1]['participantId']
    jun = Player(jun_idx, Identities[jun_idx-1]['player']['summonerId'], Identities[jun_idx-1]['player']['summonerName'], "JUNGLE", champ = champion_dict['key2'][participants[jun_idx-1]['championId']])
                
    top_idx = sorted_distance[0][1]['participantId']
    top = Player(top_idx, Identities[top_idx-1]['player']['summonerId'], Identities[top_idx-1]['player']['summonerName'], "TOP", champ = champion_dict['key2'][participants[top_idx - 1]['championId']])
                
    mid_idx = sorted_distance[1][1]['participantId']
    mid = Player(mid_idx, Identities[mid_idx-1]['player']['summonerId'], Identities[mid_idx-1]['player']['summonerName'],  "MID", champ = champion_dict['key2'][participants[mid_idx -1]['championId']])

    diff_bottom = sorted(sorted_distance[-2:], key = lambda x: x[1]['minionsKilled'], reverse= True)
    bot_idx = diff_bottom[0][1]['participantId']
    bot = Player(bot_idx, Identities[bot_idx-1]['player']['summonerId'], Identities[bot_idx-1]['player']['summonerName'], "BOT",champ = champion_dict['key2'][participants[bot_idx-1]['championId']])
    
    sup_idx = diff_bottom[1][1]['participantId']
    sup = Player(sup_idx, Identities[sup_idx-1]['player']['summonerId'], Identities[sup_idx-1]['player']['summonerName'], "SUP", champ = champion_dict['key2'][participants[sup_idx-1]['championId']])
        
    return Team(win, top, jun, mid, bot, sup)

def add_distance_value(participantFrames):
    for idx, info in participantFrames.items():
        position = info['position']
        dis = distance(position)
        info['dis'] = dis
    return participantFrames


def make_matches(watcher, my_region, target_match,champion_dict):
    timeline = watcher.match.timeline_by_match(my_region, target_match)
    # ???????3????ġ?? ??? ??ġ üũ, ? ??ü ????
    participants_3minute = timeline['frames'][3]['participantFrames']
    participants_add_distance = add_distance_value(participants_3minute)

    matches = watcher.match.by_id(my_region,target_match )
    team1 = make_team(matches['teams'][0]['win'],matches['participantIdentities'],matches['participants'], list(filter(lambda x: x[1]['participantId']<6, participants_add_distance.items())),champion_dict)
    team2 = make_team(matches['teams'][1]['win'],matches['participantIdentities'],matches['participants'], list(filter(lambda x: x[1]['participantId']>5, participants_add_distance.items())),champion_dict)
    # ???????3????ġ?? ??? ??ġ üũ, ? ??ü ????
    
    return matches, timeline, [team1, team2]

from riotwatcher import RiotWatcher, ApiError

def init(api_key, my_region):

    watcher = RiotWatcher(api_key, v4=True)

    # ?̸? -> IDs
#     me = watcher.summoner.by_name(my_region, name)
    champion_data = watcher.data_dragon.champions('9.4.1', locale='ko_KR')['data']
    id2name = {}
    key2name = {}
    for k,v in champion_data.items():
        id2name[v['id'].upper()] = v['name']
        key2name[int(v['key'])] = v['name']
        
    id2name['SYLAS'] = '사일러스'
    key2name[517] = '사일러스'
    
    champion_dict = {'id2': id2name, "key2":key2name}
    

    file = './score3.csv'
    with open(file) as fh:
        f = {}
        rd = csvpackage.DictReader(fh,delimiter = ',')
        for row in rd:
            csv = row
            
    return watcher,champion_dict, csv

