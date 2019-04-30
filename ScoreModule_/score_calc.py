import score_class
import score_main
import pandas as pd
import numpy as np
import collections
import math
from math import sqrt
from selenium import webdriver
import time
import re
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException

def make_vision_score(matches, teams,csv):

    
    participants = matches['participants']
    team1, team2 = teams[0], teams[1]
    
    vision_states = [take_vision_infomations(player, participants,csv) for player in team1.get_all_player() + team2.get_all_player()]
    assert False not in vision_states, "Can't take vision information"
    
    vision_score_state = calculate_vision_score(team1, team2, csv)
#     assert vision_score_state, "Can't calculate vision score"
    
    return teams
        
def take_vision_infomations(player, participants, csv):
    try :
        vision_info = {}
        
        idx = player.get_idx()
        stat = participants[idx-1]['stats']
        
        extract_stats = ['visionScore', 'visionWardsBoughtInGame', 'wardsPlaced', 'wardsKilled']
        for s in extract_stats:
            vision_info[s] = stat[s]

        player.set_vision(vision_info)   
        return True
    except Exception as e:
        print('Failed in take_vision_infomations : '+ str(e))
        return False
    
def calculate_dot_weight_vision_score (value, csv):
#     
#     print(float(csv.get("RIFTHERALD")))
    weight = [float(csv["calc_vision_weight_1"]), float(csv["calc_vision_weight_2"]), float(csv["calc_vision_weight_3"]), float(csv["calc_vision_weight_4"]), float(csv["calc_vision_weight_5"])]
    vs = np.round(np.dot(value, weight),2)
    value.append(vs)
    return vs

def calculate_vision_score(team1, team2, csv):
    try :
        for p1, p2 in zip(team1.get_all_player(),  team2.get_all_player()):
            p1_value = list(p1.get_vision().values())
            p2_value = list(p2.get_vision().values())

            p1_value.append(p1_value[0]-p2_value[0])
            p2_value.append(p2_value[0]-p1_value[0])

            p1.set_VS(calculate_dot_weight_vision_score(p1_value, csv))
            p2.set_VS(calculate_dot_weight_vision_score(p2_value, csv))
            
    except Exception as e:
        print('Failed in calculate_vision_score : '+ str(e))
        return False
    
    return True



def make_fight_score(matches, teams,csv):

    participants = matches['participants']
    
    fight_states = [take_fight_infomations(team, participants) for team in teams]
    assert False not in fight_states, "Can't take fight information"
    
    fight_score_state = calculate_fight_score(teams, csv)
    assert fight_score_state, "Can't calculate fight score"
    
    return teams

def take_fight_infomations(team, participants):
#     extract_contents =  ['kills','deaths','assists','totalDamageDealtToChampions','totalHeal','totalDamageTaken','totalTimeCrowdControlDealt']
    try :
        nb_total_kill = 0

        for player in team.get_all_player():
            fight_info = {}
        
            idx = player.get_idx()
            stat = participants[idx-1]['stats']

            extract_stats =  ['kills','deaths','assists','totalDamageDealtToChampions','totalHeal','totalDamageTaken','totalTimeCrowdControlDealt']
            for s in extract_stats:
                fight_info[s] = stat[s]

            player.set_fight(fight_info)   

            nb_total_kill += fight_info['kills']

        for player in team.get_all_player():
            player.calculate_set_kda(nb_total_kill)
            
    except Exception as e:
        print('Failed in take_fight_infomations : '+ str(e))
        return False  
    return True

def calculate_dot_weight_fight_score(name, value,name2label, csv):

        
    fight_weigth=[[float(csv["1.1"]),float(csv["1.2"]),float(csv["1.3"]),float(csv["1.4"]),float(csv["1.5"]),float(csv["1.6"])],
                            [float(csv["2.1"]),float(csv["2.2"]),float(csv["2.3"]),float(csv["2.4"]),float(csv["2.5"]),float(csv["2.6"])],
                            [float(csv["3.1"]),float(csv["3.2"]),float(csv["3.3"]),float(csv["3.4"]),float(csv["3.5"]),float(csv["3.6"])],
                            [float(csv["4.1"]),float(csv["4.2"]),float(csv["4.3"]),float(csv["4.4"]),float(csv["4.5"]),float(csv["4.6"])],
                            [float(csv["5.1"]),float(csv["5.2"]),float(csv["5.3"]),float(csv["5.4"]),float(csv["5.5"]),float(csv["5.6"])],
                            [float(csv["6.1"]),float(csv["6.2"]),float(csv["6.3"]),float(csv["6.4"]),float(csv["6.5"]),float(csv["6.6"])]]
    
    weight = fight_weigth[int(name2label[name])-1]
    vs = np.round(np.dot(value, weight),2)
    return vs

def normalize_fight(li_value, csv):
    return [score_class.normalize_value(li_value[3], float(csv["fight_reg_1(min)"]), float(csv["fight_reg_1(max)"])), \
           score_class.normalize_value(li_value[4], float(csv["fight_reg_2(min)"]), float(csv["fight_reg_2(max)"])),\
            score_class.normalize_value(li_value[5], float(csv["fight_reg_3(min)"]), float(csv["fight_reg_3(max)"])),\
            score_class.normalize_value(li_value[6], float(csv["fight_reg_4(min)"]),float(csv["fight_reg_4(max)"])),\
            score_class.normalize_value(li_value[7], float(csv["fight_reg_5(min)"]), float(csv["fight_reg_5(max)"])),\
            li_value[8]]
    
def calculate_fight_score(teams, csv):
#     df_ability = pd.read_csv('/Users/champion_ability_v3.csv',nrows=143)
# "C:\Users\GameEYE\ScoreModule\champion_ability_v3.csv"
# "C:\Users\기석범\Desktop\ScoreModule\champion_ability_v3.csv"
    df_ability = pd.read_csv('champion_ability_v3.csv', nrows = 143, engine = 'python' ,encoding ='utf-8')
    # "C:\Users\기석범\Desktop\GameEyE\3월\15일\MODULE\champion_ability_v3.csv"
#     "C:\Users\me\0GameEye\Modules for PlayerScore_SB0313.ipynb"
# "C:\Users\기석범\Desktop\GameEyE\ScoreModule\score_calc.py"
    name2label = {}
    for c, l in zip(df_ability['챔피언'].values, df_ability['Label'].values):
        name2label[c] = l
#     try :
    for p1, p2 in zip(teams[0].get_all_player(),  teams[1].get_all_player()):

        p1_value = np.array(list(p1.get_fight().values()), dtype= np.float32)
        p2_value = np.array(list(p2.get_fight().values()), dtype= np.float32)

        minus_value = p1_value[:-2]-p2_value[:-2]
    #     p2_m_value = p2_value[:-2]-p1_value[:-2]

        p1_norm_value = normalize_fight(np.append(minus_value,p1_value[-2:]), csv)
        p2_norm_value = normalize_fight(np.append(-(minus_value),p2_value[-2:]), csv)

        p1.set_FS(calculate_dot_weight_fight_score(p1.get_basic()[0], p1_norm_value,name2label, csv))
        p2.set_FS(calculate_dot_weight_fight_score(p2.get_basic()[0], p2_norm_value,name2label, csv))

#     except Exception as e:
#         print('Failed in calculate_vision_score : '+ str(e))
#         return False
    
    return True

def make_object_score(timeline, teams,csv):
 
    frames = timeline['frames']    
    
    object_score_state = calculate_object_score(teams, frames, csv)
    assert object_score_state, "Can't calculate object score"
    
    return teams

def calculate_team_object_value(obj_list, csv):
    objscore_dic = {'RIFTHERALD':float(csv["RIFTHERALD"]), 'BARON_NASHOR':float(csv["BARON_NASHOR"]),'ELDER_DRAGON':float(csv["ELDER_DRAGON"]), 'FIRE_DRAGON':float(csv["FIRE_DRAGON"]),'EARTH_DRAGON':float(csv["EARTH_DRAGON"]),'AIR_DRAGON':float(csv["AIR_DRAGON"]), 'WATER_DRAGON':float(csv["WATER_DRAGON"])\
                    ,'OUTER_TURRET': float(csv["OUTER_TURRET"]) ,'INNER_TURRET' : float(csv["INEER_TURRET"]), 'BASE_TURRET' : float(csv["BASE_TURRET"]), "NEXUS_TURRET":float(csv["NEXUS_TURRET"]),
                    'INHIBITOR_BUILDING_MID_LANE' : float(csv["INHIBITOR_BUILDING_MID_LANE"]), 'INHIBITOR_BUILDING_BOT_LANE:':float(csv["INHIBITOR_BUILDING_BOT_LANE"]), 'INHIBITOR_BUILDING_TOP_LANE':float(csv["INHIBITOR_BUILDING_TOP_LANE"])}
    score = 0
    for i in obj_list:
        obj = i[1]
        if 'monsterSubType' in obj:
            score +=  objscore_dic[obj['monsterSubType']]
        elif 'towerType' in obj:
            tmp = obj['buildingType'] + "_"+obj['laneType']
            if not obj['towerType'] in objscore_dic:
                score += objscore_dic[tmp]
            else :
                score += objscore_dic[obj['towerType']]
        else:
            score += objscore_dic[obj['monsterType']]
    
    return score

def calculate_dot_weight_object_score (value, csv):
    weight = [float(csv["calc_obj_weight_1"]), float(csv["calc_obj_weight_2"])]
    vs = np.round(np.dot(value, weight),2)
    return vs

def calculate_kda(death, ka):
    if death == 0 :
        kda = (ka) *1.2
    else:
        kda = np.round( ka / death ,2)
    return kda


def take_object_information(frames, csv):
    # Ã³À½ ºÎºÐÀº ÀÌº¥Æ®¿¡¼­ ¿ÀºêÁ§Æ® ÀÌº¥Æ® ÃßÃâ
    conditions = ["ELITE_MONSTER_KILL" ] # , ,"BUILDING_KILL"
    conditions2 = ["BUILDING_KILL"]
    kill_conditions = ["CHAMPION_KILL"]

    object_list = []
    object_list2 = []
    kill_list = []
    
    for i in range(len(frames)):
        participant_frames = frames[i]['participantFrames']
        events = frames[i]['events']
        timestamp = frames[i]['timestamp']

        object_events = list(filter(lambda x : x['type'] in conditions, events))
        object_events2 = list(filter(lambda x: x['type'] in conditions2 , events))

        if len(object_events)>0:
            object_list = object_list + list(zip([i]*len(object_events),object_events))

        if len(object_events2)>0:
            object_list2 = object_list2 + list(zip([i]*len(object_events2),object_events2))

        kill_events = list(filter(lambda x : x['type'] in kill_conditions, events))

        if len(kill_events)>0:
            kill_list = kill_list + list(zip([i]*len(kill_events),kill_events))
    ob_idx = list(set(map(lambda x: x[0], object_list)))
    selected_kill_idx = list(filter(lambda x: x[0] in ob_idx, kill_list))
    
    # object_list = object_list + object_list2
    # object_list = object_list + object_list2
    
    # ÆÀ ¿ÀºêÁ§Æ® Á¡¼ö ÃøÁ¤
    team1_object_list = list(filter(lambda x: x[1]['killerId']<6, object_list))
    team2_object_list = list(filter(lambda x: x[1]['killerId']>5, object_list))

    team1_tmp = calculate_team_object_value(team1_object_list, csv)
    team2_tmp = calculate_team_object_value(team2_object_list, csv)

    team1_score = np.round(team1_tmp / (team1_tmp + team2_tmp) * 100,2)
    team2_score = np.round(team2_tmp / (team1_tmp + team2_tmp) * 100,2)
    
    # °³ÀÎÀÇ ¿ÀºêÁ§Æ® KDA ÃøÁ¤
    kill_assist = []
    death = []

    for obj in object_list:
        idx = obj[0]
        info = obj[1]

        selected_kill_idx = list(filter(lambda x: x[0] == idx, kill_list))
        filltered_by_distance = list(filter(lambda x: score_class.distance(x[1]['position'], info['position']) <= 2000, selected_kill_idx))

        for tmp in filltered_by_distance:
            kill_assist.append(tmp[1]['killerId'])
            kill_assist += tmp[1]['assistingParticipantIds']
            death.append(tmp[1]['victimId'])
    
    ka_cnt = collections.Counter()
    death_cnt = collections.Counter()
    ka_cnt.update(kill_assist)
    death_cnt.update(death)
    
    return team1_score, team2_score, ka_cnt, death_cnt

def calculate_object_score(teams, frames, csv):
    
    team1_score, team2_score, ka_cnt, death_cnt  = take_object_information(frames, csv)
    
    for p1, p2 in zip(teams[0].get_all_player(),  teams[1].get_all_player()):
        p1_idx = p1.get_idx()
        p2_idx = p2.get_idx()

        p1_kda = calculate_kda(death_cnt[p1_idx], ka_cnt[p1_idx])
        p2_kda = calculate_kda(death_cnt[p2_idx], ka_cnt[p2_idx])

        p1_norm_value = [team1_score , score_class.normalize_value(p1_kda, 0,7)]
        p2_norm_value = [team2_score , score_class.normalize_value(p2_kda, 0, 7)]
        
        p1.set_object({"team score" : team1_score, "kda" : p1_kda})
        p2.set_object({"team score" : team2_score, "kda" :p2_kda})

        p1.set_OS(calculate_dot_weight_object_score(p1_norm_value, csv))
        p2.set_OS(calculate_dot_weight_object_score(p2_norm_value, csv))
    return True
    

    


def crawl_other_score(watcher, my_region, player, target_match, champion_dict,csv):
    
    me  = watcher.summoner.by_id( my_region, player.get_summonerId())
    name = me['name']
    your_name = player.name

    # op gg crawling
#     driver_url = '/Users/chromedriver_win32(v.2.46)/chromedriver'
# "C:\Users\기석범\Desktop\ScoreModule\chromedriver_win32\chromedriver.exe"
# "C:\Users\기석범\Desktop\ScoreModule\chromedriver_win32(v.2.46)\chromedriver.exe"
    driver_url = 'chromedriver_win32(v.2.46)/chromedriver'
#     "C:\Users\chromedriver_win32\chromedriver.exe"
# "C:\Users\GameEYE\Downloads\chromedriver_win32\chromedriver.exe"

    driver = webdriver.Chrome(driver_url)

    driver.implicitly_wait(5)
    # url¿¡ Á¢±ÙÇÑ´Ù.
    opgg_url = 'http://www.op.gg/summoner/userName='+name 
    driver.get(opgg_url)
    game = None

    update = driver.find_element_by_css_selector("button#SummonerRefreshButton.Button.SemiRound.Blue")
    update.click()
    time.sleep(3)


    while not game:
        try:
            game = driver.find_element_by_css_selector("div[data-game-id='" + target_match + "']")

        except UnexpectedAlertPresentException: 
            alert  = driver.switch_to_alert()
            alert.accept()
            time.sleep(3)

        except NoSuchElementException:
            print( " more pages ")
            more = driver.find_element_by_css_selector("div[class='GameMoreButton Box']")
            more.click()
            time.sleep(3)


    btn_gamedetail = game.find_elements_by_css_selector("a.Button.MatchDetail")[0]
    btn_gamedetail.click()

    detail = game.find_element_by_css_selector("div.GameDetail")
    names = detail.find_elements_by_css_selector("td.ChampionImage.Cell")
    scores = detail.find_elements_by_css_selector("div.OPScore.Text")

    opscores = {}
    for n,s in zip(names, scores):
        opscores[n.text.split("\n")[0]] = float(s.text)

    driver.close()

    # your gg crwaling 
    re_pattern = re.compile('(champion\/)(\w+)(.png)')

    driver = webdriver.Chrome(driver_url)
    driver.implicitly_wait(3)

    yourgg_update_url = "http://your.gg/kr/summoner?s="+your_name

    try:
        driver.get(yourgg_update_url)

        update = driver.find_element_by_css_selector('div.gg-button-refresh')
        update.click()
        time.sleep(3)

    except NoSuchElementException:
        pass

    driver.get('http://your.gg/kr/game?s='+your_name+'&m='+target_match)

    detail = driver.find_element_by_css_selector('div.gg-game-detail')
    # names = detail.find_elements_by_css_selector('div.gg-game-detail-bio')
    names = detail.find_elements_by_css_selector('div.gg-user-thumb-img')
    scores = detail.find_elements_by_css_selector('div.gg-game-detail-contribution')

    yourggScores = {}
    for n,s in zip(names, scores):
        tmp_name = str(n.find_element_by_css_selector('img').get_attribute("src"))
        name = champion_dict['id2'][re_pattern.search(tmp_name).group(2).upper()]
        score = float(s.text.split("인분")[0])
        yourggScores[name.strip()] = score
    driver.close()

    #  combine
    
    print(opscores)
    print(yourggScores)
    
    crawling_score = {}
    for k,v in opscores.items():
        crawling_score[k] = [v, yourggScores[k]]
    
    return crawling_score

def Calc_Growth(teams, timeline, matches, watcher, csv ,my_region):

    timeline = timeline['frames']
#     print("dd : ",len(timeline))
#     print("dd",timeline)
    Team1_Growth = []
    Team2_Growth = []
    i = 0
    j = 0
    
    T1 = []
    T2 = []
    for player in teams[0].get_all_player():
    # player = team1.top
        idx = player.get_idx()
        T1.append(idx)
    
    for player in teams[1].get_all_player():
    # player = team1.top
        idx = player.get_idx()
        T2.append(idx)

    def Growth_GAP(timeline,x,y) :     
        result = ((timeline[len(timeline)-1]['participantFrames'][str(x)]['totalGold']- timeline[len(timeline)-1]['participantFrames'][str(y)]['totalGold']) +
        (timeline[math.ceil((len(timeline)-1)/2)]['participantFrames'][str(x)]['totalGold'] - timeline[math.ceil((len(timeline)-1)/2)]['participantFrames'][str(y)]['totalGold']) +
        (timeline[len(timeline)-1]['participantFrames'][str(x)]['xp']- timeline[len(timeline)-1]['participantFrames'][str(y)]['xp']) +
        (timeline[math.ceil((len(timeline)-1)/2)]['participantFrames'][str(x)]['xp'] - timeline[math.ceil((len(timeline)-1)/2)]['participantFrames'][str(y)]['xp']))
#         print(result)
        return result
    '''
    x : Team1_player, y : Tema2_player 
    Team1ÇÃ·¹ÀÌ¾î¿Í  Team2ÇÃ·¹ÀÌ¾îÀÇ ÇØ´ç °ÔÀÓ ÇÁ·¹ÀÓÀÇ 1/2ÁöÁ¡¿¡¼­ÀÇ °ñµåÂ÷, XpÂ÷¿Í 2/2ÁöÁ¡¿¡¼­ÀÇ °ñµåÂ÷, XP°ÝÂ÷ÀÇ ¼öÄ¡ ÇÕÀ» ÅëÇÑ ¼ºÀå°ÝÂ÷ °è»ê
    '''

    def reg(x):
        result = round((x-(float(csv["growth_reg(min)"])))/(float(csv["growth_reg(max)"])-(float(csv["growth_reg(min)"])))*100)
        if result > 100 :
            result = 100
        if result < 0 :
            result = 0
        return result
    '''
    Á¤±ÔÈ­
    '''

    for i in range(0,5):
        Growth1 = Growth_GAP(timeline,T1[i],T2[i])
        Final_Growth1 = reg(Growth1)
        Growth2 = Growth_GAP(timeline,T2[i],T1[i])
        Final_Growth2 = reg(Growth2)
        Team1_Growth.append(Final_Growth1)
        Team2_Growth.append(Final_Growth2)
    '''
    Team1 Team2 10¸íÀÇ ÇÃ·¹ÀÌ¾îµé¿¡ ´ëÇÑ ¼ºÀåÄ¡ °è»ê ÈÄ °ª ºÎ¿©
    '''    
    
    
    i = 0
    
    for player in teams[0].get_all_player():

        idx = player.get_idx()

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

        growth_info = {}
        stat = player_info['stats']
        growth_info['Growth_Score'] = Team1_Growth[i]

        player.set_champ(champ)
        player.set_growth(growth_info)
        player.set_GS(50+(Team1_Growth[i])/2)
        i = i + 1

    j = 0
    '''
    1ÆÀ Á¡¼ö ºÎ¿©
    '''
    for player in teams[1].get_all_player():

        idx = player.get_idx()

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

        growth_info = {}
        stat = player_info['stats']
        growth_info['Growth_Score'] = Team2_Growth[j]

        player.set_champ(champ)
        player.set_growth(growth_info)
        player.set_GS(50+(Team2_Growth[j])/2)
        j = j + 1
    '''
    2ÆÀ Á¡¼ö ºÎ¿©
    '''    
    return teams

def Calc_Careforce(timeline, teams, matches,watcher, csv,my_region) :
    
    timeline = timeline['frames']
    T1 = []
    T2 = []
    for player in teams[0].get_all_player():
  
        idx = player.get_idx()
        T1.append(idx)
    
    for player in teams[1].get_all_player():
   
        idx = player.get_idx()
        T2.append(idx)

    def reg(value, range_max, range_min):
        result = round((value-(range_min))/(range_max-(range_min))*100)
        if result > 100 :
            result = 100
        if result < 0 :
            result = 0
        return result


    for i in range(len(timeline)) :
        for j in range(len(timeline[i]['events'])):
            laneType = 'laneType' in timeline[i]['events'][j]
            if (laneType == True) and (timeline[i]['events'][j]['laneType'] == 'BOT_LANE') and (timeline[i]['events'][j]['towerType'] == 'OUTER_TURRET'):
                timestamp = timeline[i]['events'][j]['timestamp']
                time = math.ceil(timestamp/1000/60)
                frame = i
    '''
    ¶óÀÎÀü ´Ü°è¿¡¼­ÀÇ ÇÁ·¹ÀÓ °ª ±¸ÇÏ±â
    '''            

    Team1_AD_Kill = 0
    Team1_AD_Death = 0
    Team1_AD_Assist = 0
    #Kill
    
    def function_kill(frame, player):
        kill = 0
        for i in range(frame):
            for j in range(len(timeline[i]['events'])):
                if (timeline[i]['events'][j]['type']=='CHAMPION_KILL'):
                    if timeline[i]['events'][j]['killerId'] == player:
                        kill = kill +1
        return kill
    def function_death(frame, player):
        death = 0
        for i in range(frame):
            for j in range(len(timeline[i]['events'])):
                if (timeline[i]['events'][j]['type']=='CHAMPION_KILL'):
                    if timeline[i]['events'][j]['victimId'] == player:
                        death = death +1
        return death
    def function_assist(frame, player):
        assist = 0
        for i in range(frame):
            for j in range(len(timeline[i]['events'])):
                if (timeline[i]['events'][j]['type']=='CHAMPION_KILL'):
                    if (player in timeline[i]['events'][j]['assistingParticipantIds']) :
                        assist = assist +1
        return assist
    
    
    
    Team1_AD_Kill = function_kill(frame, T1[3])
    Team1_AD_Death = function_death(frame, T1[3])
    Team1_AD_Assist = function_assist(frame, T1[3])

    if Team1_AD_Death == 0 :
        value = (Team1_AD_Kill + Team1_AD_Assist)*1.2
    else :
        value = (Team1_AD_Kill + Team1_AD_Assist) /Team1_AD_Death

    reg_Team1_AD_KDA1 = reg(value, float(csv["kda_reg(max)"]), float(csv["kda_reg(min)"]))

    '''
    1ÆÀ ¶óÀÎÀü¿¡¼­ÀÇ ¿øµô KDA
    '''                
    #¶óÀÎÀü KDA_¼­Æý
    Team1_Sup_Kill = 0
    Team1_Sup_Death = 0
    Team1_Sup_Assist = 0
    
    Team1_Sup_Kill = function_kill(frame, T1[4])
    Team1_Sup_Death = function_death(frame, T1[4])
    Team1_Sup_Assist = function_assist(frame, T1[4])
    

    if Team1_Sup_Death == 0 :
        value = (Team1_Sup_Kill + Team1_Sup_Assist)*1.2
    else :
        value = (Team1_Sup_Kill + Team1_Sup_Assist) /Team1_Sup_Death

    reg_Team1_SUP_KDA1 = reg(value, float(csv["kda_reg(max)"]), float(csv["kda_reg(min)"]))

    '''
    1ÆÀ ¶óÀÎÀü¿¡¼­ÀÇ ¼­Æý KDA
    '''                

    Team2_AD_Kill = 0
    Team2_AD_Death = 0
    Team2_AD_Assist = 0
    
    Team2_AD_Kill = function_kill(frame, T2[3])
    Team2_AD_Death = function_death(frame, T2[3])
    Team2_AD_Assist = function_assist(frame, T2[3])

    if Team2_AD_Death == 0 :
        value = (Team2_AD_Kill + Team2_AD_Assist)*1.2
    else :
        value = (Team2_AD_Kill + Team2_AD_Assist) /Team2_AD_Death

#     print("KDA Value : ", value)
    reg_Team2_AD_KDA1 = reg(value, float(csv["kda_reg(max)"]), float(csv["kda_reg(min)"]))
#     print("KDA Á¤±ÔÈ­ Á¡¼ö : ", reg_Team2_AD_KDA1) 
    '''
    2ÆÀ ¶óÀÎÀü ¿øµô KDA
    '''                
    #¶óÀÎÀü KDA_¼­Æý
    Team2_Sup_Kill = 0
    Team2_Sup_Death = 0
    Team2_Sup_Assist = 0
    
    Team2_Sup_Kill = function_kill(frame, T2[4])
    Team2_Sup_Death = function_death(frame, T2[4])
    Team2_Sup_Assist = function_assist(frame, T2[4])

    if Team2_Sup_Death == 0 :
        value = (Team2_Sup_Kill + Team2_Sup_Assist)*1.2
    else :
        value = (Team2_Sup_Kill + Team2_Sup_Assist) /Team2_Sup_Death

    reg_Team2_Sup_KDA1 = reg(value, float(csv["kda_reg(max)"]), float(csv["kda_reg(min)"]))
    '''
    2ÆÀ ¶óÀÎÀü ¼­Æý KDA
    '''
    Team1_AD_Gold_1 = timeline[frame]['participantFrames'][str(T1[3])]['totalGold']
    Team1_Sup_Gold_1 = timeline[frame]['participantFrames'][str(T1[4])]['totalGold']
    Team2_AD_Gold_1 = timeline[frame]['participantFrames'][str(T2[3])]['totalGold']
    Team2_Sup_Gold_1 = timeline[frame]['participantFrames'][str(T2[4])]['totalGold']
    x = (Team1_AD_Gold_1-Team2_AD_Gold_1) + (Team1_Sup_Gold_1-Team2_Sup_Gold_1)
    Team1_Gold1 = reg(x, float(csv["gold_reg(max)"]), float(csv["gold_reg(min)"]))
    y = (Team2_AD_Gold_1-Team1_AD_Gold_1) + (Team2_Sup_Gold_1-Team1_Sup_Gold_1)
    Team2_Gold1 = reg(y, float(csv["gold_reg(max)"]), float(csv["gold_reg(min)"]))

    Team1_AD_CS_1 = timeline[frame]['participantFrames'][str(T1[3])]['minionsKilled'] + timeline[len(timeline)-1]['participantFrames'][str(T1[3])]['jungleMinionsKilled'] 
    Team1_Sup_CS_1 = timeline[frame]['participantFrames'][str(T1[4])]['minionsKilled'] + timeline[len(timeline)-1]['participantFrames'][str(T1[4])]['jungleMinionsKilled'] 
    Team2_AD_CS_1 = timeline[frame]['participantFrames'][str(T2[3])]['minionsKilled'] + timeline[len(timeline)-1]['participantFrames'][str(T2[4])]['jungleMinionsKilled'] 
    Team2_Sup_CS_1 = timeline[frame]['participantFrames'][str(T2[3])]['minionsKilled'] + timeline[len(timeline)-1]['participantFrames'][str(T2[4])]['jungleMinionsKilled'] 



    x = (Team1_AD_CS_1-Team2_AD_CS_1) + (Team1_Sup_CS_1-Team2_Sup_CS_1)
#     print(x)
    Team1_CS1 = reg(x, float(csv["cs_reg(max)"]), float(csv["cs_reg(min)"]))
#     print(Team1_CS1)
    y = (Team2_AD_CS_1-Team1_AD_CS_1) + (Team2_Sup_CS_1-Team1_Sup_CS_1)
#     print(y)
    Team2_CS1 = reg(y, float(csv["cs_reg(max)"]), float(csv["cs_reg(min)"]))

    Team1_Sup_Vision = matches['participants'][T1[4]-1]['stats']['visionScore']
#     print("1ÆÀ ½Ã¾ß Á¡¼ö", Team1_Sup_Vision)
    Team2_Sup_Vision = matches['participants'][T2[4]-1]['stats']['visionScore']
#     print("2ÆÀ ½Ã¾ß Á¡¼ö", Team2_Sup_Vision)


    x = (Team1_Sup_Vision-Team2_Sup_Vision)
    Team1_Ward = reg(x, float(csv["ward_reg(max)"]), float(csv["ward_reg(min)"]))
#     print(Team1_Ward)
    y = (Team2_Sup_Vision-Team1_Sup_Vision)
    Team2_Ward = reg(y, float(csv["ward_reg(max)"]), float(csv["ward_reg(min)"]))
#     print(Team2_Ward) 

    Team1_FT = 0
    Team2_FT = 0
    for i in range(0,2) :
        if matches['teams'][i]['firstTower'] ==True :
            if i == 0 :
                Team1_FT = float(csv["towerscore"])
            if i == 1 :
                Team2_FT = float(csv["towerscore"])

    Team1_Sup_Win = 0
    Team2_Sup_Win = 0
    for i in range(0,2) :
        if matches['teams'][i]['win'] =='Win' :
            if i == 0 :
                Team1_Sup_Win = float(csv["winscore"])
            if i == 1 :
                Team2_Sup_Win = float(csv["winscore"])

    Team1_Deal = matches['participants'][T1[3]-1]['stats']['totalDamageDealtToChampions']
#     print(Team1_Deal)

    Team2_Deal = matches['participants'][T1[4]-1]['stats']['totalDamageDealtToChampions']
#     print(Team2_Deal)
    #¼­Æý µô·®
    Team1_Sup_Deal = matches['participants'][T2[3]-1]['stats']['totalDamageDealtToChampions']
#     print("¼­Æý : ",Team1_Sup_Deal)

    Team2_Sup_Deal = matches['participants'][T2[4]-1]['stats']['totalDamageDealtToChampions']
#     print("¼­Æý : ",Team2_Sup_Deal)

    x = Team1_Deal
    Team1_Deal1 = reg(x, float(csv["deal_reg(max)"]), float(csv["deal_reg(min)"]))
#     print(Team1_Deal1)
    y = (Team2_Deal)
    Team2_Deal2 = reg(y, float(csv["deal_reg(max)"]), float(csv["deal_reg(min)"]))
#     print(Team2_Deal2) 

    Team1_Sup_D = reg(Team1_Sup_Deal, float(csv["deal_reg(max)"]), float(csv["deal_reg(min)"]))
#     print("¼­Æý µô :",Team1_Sup_D)
    Team2_Sup_D = reg(Team2_Sup_Deal, float(csv["deal_reg(max)"]), float(csv["deal_reg(min)"]))
#     print("¼­Æý µô :",Team2_Sup_D)

    Team1_AD_Care = (reg_Team1_AD_KDA1+reg_Team1_SUP_KDA1)+Team1_Gold1+Team1_CS1+Team1_FT+Team1_Sup_Win+Team1_Ward+Team1_Deal1+Team1_Sup_D
#     print(Team1_AD_Care)
#     print("...\n")
#     print(reg_Team1_AD_KDA1,reg_Team1_SUP_KDA1,Team1_Gold1,Team1_CS1,Team1_FT,Team1_Sup_Win,Team1_Ward,Team1_Deal1,Team1_Sup_D)
    Team2_AD_Care = (reg_Team2_AD_KDA1+reg_Team2_Sup_KDA1)+Team2_Gold1+Team2_CS1+Team2_FT+Team2_Sup_Win+Team2_Ward+Team2_Deal2+Team2_Sup_D


    Team1_AD_C = reg(Team1_AD_Care, float(csv["care_reg(max)"]), float(csv["care_reg(min)"]))
    Team2_AD_C = reg(Team2_AD_Care, float(csv["care_reg(max)"]), float(csv["care_reg(min)"])) 
#     print("À½",Team1_AD_C,Team2_AD_C)
    Team1 = round((Team1_AD_Care / (Team1_AD_Care+Team2_AD_Care))*100)
    Team2 = round((Team2_AD_Care / (Team1_AD_Care+Team2_AD_Care))*100)

    Careforce1 = [0,0,0,0,0]
    Careforce2 = [0,0,0,0,0]

    Careforce1[4]= Team1
    Careforce2[4]= Team2
    
    i = 0
    for player in teams[0].get_all_player():
    # player = team1.top
        idx = player.get_idx()

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

        care_info = {}
        stat = player_info['stats']
        care_info['Careforce_Score'] = Careforce1[i]

        player.set_champ(champ)
        player.set_care(care_info)
        player.set_CS(Careforce1[i])
        i = i+1

    j = 0
    for player in teams[1].get_all_player():
    # player = team1.top
        idx = player.get_idx()

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

        care_info = {}
        stat = player_info['stats']
        care_info['Careforce_Score'] = Careforce2[j]

        player.set_champ(champ)
        player.set_care(care_info)
        player.set_CS(Careforce2[j])
        j = j+1
        
    return teams

# 
def Calc_Roaming(teams, timeline, matches, watcher, csv, my_region) :
    mainmatch = timeline
    timeline = timeline['frames']
    T1 = []
    T2 = []
    for player in teams[0].get_all_player():
    # player = team1.top
        idx = player.get_idx()
        T1.append(idx)
    
    for player in teams[1].get_all_player():
    # player = team1.top
        idx = player.get_idx()
        T2.append(idx)

    def roaming_reg(x):
        value = round((x-(float(csv["roaming_reg(min)"])))/(float(csv["roaming_reg(max)"])-(float(csv["roaming_reg(min)"])))*100)
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        return value
    
    i = 0
    j = 0
    Team_liner = 0
    Total_value1 = 0
    Total_value2 = 0
    Total_minus_value2 = 0
    Total_minus_value1 = 0
    minus_value1 = 0
    minus_value2 = 0
    value1 = 0
    value2 = 0
    player_i = 0


    def Calc(x,y,liner, player1, player2, present_time, past_time) :
        val1 = 0
        if (math.ceil(sqrt(pow((x-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((y-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and ((mainmatch['frames'][i]['events'][j]['killerId']==liner) \
            or (liner in mainmatch['frames'][i]['events'][j]['assistingParticipantIds'])) :
            
            # print(x,y,liner, player1, player2, present_time, past_time)
            
            val1 = (((mainmatch['frames'][present_time]['participantFrames'][player1]['xp']-mainmatch['frames'][present_time]['participantFrames'][player2]['xp'])-\
            (mainmatch['frames'][past_time]['participantFrames'][player1]['xp']-mainmatch['frames'][past_time]['participantFrames'][player2]['xp']))+\
            ((mainmatch['frames'][present_time]['participantFrames'][player1]['totalGold']-mainmatch['frames'][present_time]['participantFrames'][player2]['totalGold'])-\
            (mainmatch['frames'][past_time]['participantFrames'][player1]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][player2]['totalGold'])))
            print("val1 = ",val1)
        return val1

    def Calc_Bot(x,y,liner1,liner2, player1, player2, present_time, past_time) :
        val1 = 0
        if (math.ceil(sqrt(pow((x-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((y-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and ((mainmatch['frames'][i]['events'][j]['killerId']==liner1) \
            or (liner1 in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) or (mainmatch['frames'][i]['events'][j]['killerId']==liner2) or (liner2 in mainmatch['frames'][i]['events'][j]['assistingParticipantIds'])) :
                     
            # print(x,y,liner1,liner2, player1, player2)
            # print(x,y,liner1,liner2, player1, player2, present_time, past_time)
            val1 = (((mainmatch['frames'][present_time]['participantFrames'][player1]['xp']-mainmatch['frames'][present_time]['participantFrames'][player2]['xp'])-\
            (mainmatch['frames'][past_time]['participantFrames'][player1]['xp']-mainmatch['frames'][past_time]['participantFrames'][player2]['xp']))+\
            ((mainmatch['frames'][present_time]['participantFrames'][player1]['totalGold']-mainmatch['frames'][present_time]['participantFrames'][player2]['totalGold'])-\
            (mainmatch['frames'][past_time]['participantFrames'][player1]['totalGold']-mainmatch['frames'][past_time]['participantFrames'][player2]['totalGold'])))
            print("bot va1 = 0 : ",val1)
        return val1

    
    for player in teams[0].get_all_player():

        idx = player.get_idx()
        Total_value1 = 0
        Total_minus_value1 = 0

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]
        # print("챔피언 : ",champ,"idx : ", idx)
        for i in range(1,16) :
            print(i)
            for j in range(len(mainmatch['frames'][i]['events'])) :
                if (mainmatch['frames'][i]['events'][j]['type']=='CHAMPION_KILL'):

                    if mainmatch['frames'][i]['events'][j]['killerId']==idx or idx in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']:
                        
                        
                        time = mainmatch['frames'][i]['events'][j]['timestamp']
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1
                        print("1팀 time : ",time)

                        #변수설정
                        victim = mainmatch['frames'][i]['events'][j]['victimId']
                        if victim == T2[0]:
                            Team_liner = T1[0]
                        if victim == T2[1]:
                            Team_liner = T1[1]
                        if victim == T2[2]:
                            Team_liner = T1[2]
                        if victim == T2[3]:
                            Team_liner = T1[3]
                        if victim == T2[4]:
                            Team_liner = T1[4]
                        if player_i == 0 :
                            calc_value1 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T1[2], str(Team_liner), str(victim), present_time, past_time)
                            calc_value1 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T1[3], T1[4], str(Team_liner), str(victim), present_time, past_time)
                        if player_i == 1 :
                            calc_value1 = Calc(float(csv["top_x"]), float(csv["top_y"]), T1[0], str(Team_liner), str(victim), present_time, past_time)
                            calc_value1 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T1[2], str(Team_liner), str(victim), present_time, past_time)
                            calc_value1 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T1[3], T1[4], str(Team_liner), str(victim), present_time, past_time)
                        if player_i == 2 :
                            print("드븐 +++점수: ",present_time)
                            calc_value1 = Calc(float(csv["top_x"]), float(csv["top_y"]), T1[0], str(Team_liner), str(victim), present_time, past_time)
                            calc_value1 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T1[3], T1[4], str(Team_liner), str(victim), present_time, past_time)
                            print("드븐 값 : ",calc_value1)   
                        if (player_i == 3) or (player_i == 4) :
                            calc_value1 = Calc(float(csv["top_x"]), float(csv["top_y"]), T1[0], str(Team_liner), str(victim), present_time, past_time)
                            calc_value1 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T1[2], str(Team_liner), str(victim), present_time, past_time)  
                                               

                        Total_value1 = Total_value1 + abs(calc_value1)
          
                        calc_value1 = 0

                    #적 라이너에게 죽었을 경우, Minus가치 계산
                    if mainmatch['frames'][i]['events'][j]['victimId']==idx:
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1
                        print("1팀 time : ",time)

                        killerId = mainmatch['frames'][i]['events'][j]['killerId']
                        if killerId == T2[0]:
                            Team_liner = T1[0]
                        if killerId == T2[1]:
                            Team_liner = T1[1]
                        if killerId == T2[2]:
                            Team_liner = T1[2]
                        if killerId == T2[3]:
                            Team_liner = T1[3]
                        if killerId == T2[4]:
                            Team_liner = T1[4]

                        if player_i == 0 :
                            calc_minus_value1 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T2[2], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value1 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T2[3], T2[4], str(killerId), str(Team_liner), present_time, past_time)
                        if player_i == 1 :
                            calc_minus_value1 = Calc(float(csv["top_x"]), float(csv["top_y"]), T2[0], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value1 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T2[2], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value1 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T2[3], T2[4], str(killerId), str(Team_liner), present_time, past_time)
                        if player_i == 2 :
                            print("드븐 마이너스 점수 : ",present_time)
                            calc_minus_value1 = Calc(float(csv["top_x"]), float(csv["top_y"]), T2[0], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value1 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T2[3], T2[4], str(killerId), str(Team_liner), present_time, past_time)
                            print("드븐 값 : ",calc_value1)   

                        if (player_i == 3) or (player_i == 4) :
                            calc_minus_value1 = Calc(float(csv["top_x"]), float(csv["top_y"]), T2[0], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value1 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T2[2], str(killerId), str(Team_liner), present_time, past_time)    
           
                        Total_minus_value1 = Total_minus_value1 + abs(calc_minus_value1)
          
                        calc_minus_value1 = 0

###################################

        Total_value1 = Total_value1 - Total_minus_value1
      
        roaming = roaming_reg(Total_value1)
        roaming_info = {}
        stat = player_info['stats']
        roaming_info['Roaming_Score'] = roaming

        player.set_champ(champ)
        player.set_roaming(roaming_info)
        player.set_RS(roaming)
        i = i + 1
        player_i = player_i+1
        Total_value1 = 0

    player_i = 0
    for player in teams[1].get_all_player():

        idx = player.get_idx()
        Total_value2 = 0
        Total_minus_value2 = 0

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

    ####################################
        for i in range(1,16) :
            for j in range(len(mainmatch['frames'][i]['events'])) :
                if (mainmatch['frames'][i]['events'][j]['type']=='CHAMPION_KILL'):

                    if mainmatch['frames'][i]['events'][j]['killerId']==idx or idx in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']:

                        time = mainmatch['frames'][i]['events'][j]['timestamp']
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1

                        #변수설정
                        victim = mainmatch['frames'][i]['events'][j]['victimId']
                        if victim == T1[0]:
                            Team_liner = T2[0]
                        if victim == T1[1]:
                            Team_liner = T2[1]
                        if victim == T1[2]:
                            Team_liner = T2[2]
                        if victim == T1[3]:
                            Team_liner = T2[3]
                        if victim == T1[4]:
                            Team_liner = T2[4]
                                                 
                        if player_i == 0 :
                            calc_value2 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T2[2], str(Team_liner), str(victim), present_time, past_time)
                            calc_value2 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T2[3], T2[4], str(Team_liner), str(victim), present_time, past_time)
                        if player_i == 1 :
                            calc_value2 = Calc(float(csv["top_x"]), float(csv["top_y"]), T2[0], str(Team_liner), str(victim), present_time, past_time)
                            calc_value2 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T2[2], str(Team_liner), str(victim), present_time, past_time)
                            calc_value2 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T2[3], T2[4], str(Team_liner), str(victim), present_time, past_time)
                        if player_i == 2 :
                            print("카타리나 : ")
                            calc_value2 = Calc(float(csv["top_x"]), float(csv["top_y"]), T2[0], str(Team_liner), str(victim), present_time, past_time)
                            calc_value2 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T2[3], T2[4], str(Team_liner), str(victim), present_time, past_time)
                        if (player_i == 3) or (player_i == 4) :
                            calc_value2 = Calc(float(csv["top_x"]), float(csv["top_y"]), T2[0], str(Team_liner), str(victim), present_time, past_time)
                            calc_value2 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T2[2], str(Team_liner), str(victim), present_time, past_time)    

                        Total_value2 = Total_value2 + abs(calc_value2)
                        
                        
                      
                        calc_value2 = 0
        #         if (mainmatch['frames'][i]['events'][j]['type']=='CHAMPION_KILL'):
                    #적 라이너에게 죽었을 경우, Minus가치 계산
                    if mainmatch['frames'][i]['events'][j]['victimId']==idx:
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1

                        killerId = mainmatch['frames'][i]['events'][j]['killerId']
                        if killerId == T1[0]:
                            Team_liner = T2[0]
                        if killerId == T1[1]:
                            Team_liner = T2[1]
                        if killerId == T1[2]:
                            Team_liner = T2[2]
                        if killerId == T1[3]:
                            Team_liner = T2[3]
                        if killerId == T1[4]:
                            Team_liner = T2[4]
                        
                        if player_i == 0 :
                            calc_minus_value2 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T1[2], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value2 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T1[3], T1[4], str(killerId), str(Team_liner), present_time, past_time)
                        if player_i == 1 :
                            calc_minus_value2 = Calc(float(csv["top_x"]), float(csv["top_y"]), T1[0], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value2 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T1[2], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value2 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T1[3], T1[4], str(killerId), str(Team_liner), present_time, past_time)
                        if player_i == 2 :
                            calc_minus_value2 = Calc(float(csv["top_x"]), float(csv["top_y"]), T1[0], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value2 = Calc_Bot(float(csv["bot_x"]), float(csv["bot_y"]), T1[3], T1[4], str(killerId), str(Team_liner), present_time, past_time)
                        if (player_i == 3) or (player_i == 4) :
                            calc_minus_value2 = Calc(float(csv["top_x"]), float(csv["top_y"]), T1[0], str(killerId), str(Team_liner), present_time, past_time)
                            calc_minus_value2 = Calc(float(csv["mid_x"]), float(csv["mid_y"]), T1[2], str(killerId), str(Team_liner), present_time, past_time)    

                        Total_minus_value2 = Total_minus_value2 + abs(calc_minus_value2)
                        
                     
                            
                        calc_minus_value2 = 0

    ###################################
        Total_value2 = Total_value2 - Total_minus_value2
     
        roaming = roaming_reg(Total_value2)
        roaming_info = {}
        stat = player_info['stats']
        roaming_info['Roaming_Score'] = roaming

        player.set_champ(champ)
        player.set_roaming(roaming_info)
        player.set_RS(roaming)
        j = j + 1
        player_i = player_i+1
        Total_value2 = 0
    return teams
# 
'''
def Calc_Roaming(teams, timeline, matches,watcher,csv,my_region) :
    
    mainmatch = timeline
    timeline = timeline['frames']
    T1 = []
    T2 = []
    for player in teams[0].get_all_player():
    # player = team1.top
        idx = player.get_idx()
        T1.append(idx)
    
    for player in teams[1].get_all_player():
    # player = team1.top
        idx = player.get_idx()
        T2.append(idx)

    
    def roaming_reg(x):
        value = round((x-(float(csv["roaming_reg(min)"])))/(float(csv["roaming_reg(max)"])-(float(csv["roaming_reg(min)"])))*100)
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        return value

#     T1 = []
#     T2 = []
#     for player in team1.get_all_player():
#     # player = team1.top
#         idx = player.get_idx()
#         T1.append(idx)
#     for player in team2.get_all_player():
#     # player = team1.top
#         idx = player.get_idx()
#         T2.append(idx)

    i = 0
    j = 0
    Team_liner = 0
    Total_value1 = 0
    Total_value2 = 0
    Total_minus_value2 = 0
    Total_minus_value1 = 0
    minus_value1 = 0
    minus_value2 = 0
    value1 = 0
    value2 = 0
    player_i = 0
    for player in teams[0].get_all_player():

        idx = player.get_idx()

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

    ####################################
        for i in range(1,15) :
            for j in range(len(mainmatch['frames'][i]['events'])) :
                if (mainmatch['frames'][i]['events'][j]['type']=='CHAMPION_KILL'):

                    if mainmatch['frames'][i]['events'][j]['killerId']==idx or idx in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']:

                        time = mainmatch['frames'][i]['events'][j]['timestamp']
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1

                        #º¯¼ö¼³Á¤
                        victim = mainmatch['frames'][i]['events'][j]['victimId']
                        if victim == T2[0]:
                            Team_liner = T1[0]
                        if victim == T2[1]:
                            Team_liner = T1[1]
                        if victim == T2[2]:
                            Team_liner = T1[2]
                        if victim == T2[3]:
                            Team_liner = T1[3]
                        if victim == T2[4]:
                            Team_liner = T1[4]

                        #Å¾ÀÏ°æ¿ì
                        #¾Æ·¡ 3°³ ¹­¾î¼­...ÁÂÇ¥µµ ÆÄ¶ó¹ÌÅÍ·Î...Å¾,Á¤±Û,¹Ìµå,¿øµô,¼­Æý...³ª´²¼­ °è»ê
                        def Calc_Team1_Top_K() :
                            val1 = 0
                            if (math.ceil(sqrt(pow((float(csv["top_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["top_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T1[0] or T1[0] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                val1 = (((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(victim)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(victim)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(victim)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(victim)]['totalGold'])))

                            return val1

                        #¹ÌµåÀÏ°æ¿ì
                        def Calc_Team1_Mid_K() : 
                            val1 = 0
                            if (math.ceil(sqrt(pow((float(csv["mid_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["mid_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T1[2] or T1[2] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                val1 = (((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(victim)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(victim)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(victim)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(victim)]['totalGold'])))
                            return val1

                        #¹ÙÅÒÀÏS°æ¿ì
                        def Calc_Team1_Bot_K() :
                            val1 = 0
                            if (math.ceil(sqrt(pow((float(csv["bot_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["bot_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T1[3] or (T1[3] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds'])) or (mainmatch['frames'][i]['events'][j]['killerId']==T1[4]) or (T1[4] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                val1 = (((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(victim)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(victim)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(victim)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(victim)]['totalGold'])))
                            return val1

                        if player_i == 0 :
                            calc_value1 = Calc_Team1_Mid_K()
                            calc_value1 = Calc_Team1_Bot_K()
                        if player_i == 1 :
                            calc_value1 = Calc_Team1_Top_K()
                            calc_value1 = Calc_Team1_Mid_K()
                            calc_value1 = Calc_Team1_Bot_K()
                        if player_i == 2 :
                            calc_value1 = Calc_Team1_Top_K()
                            calc_value1 = Calc_Team1_Bot_K()
                        if (player_i == 3) or (player_i ==4) :
                            calc_value1 = Calc_Team1_Top_K()
                            calc_value1 = Calc_Team1_Mid_K()


                        Total_value1 = Total_value1 + abs(calc_value1)
                        calc_value1 = 0

                    #Àû ¶óÀÌ³Ê¿¡°Ô Á×¾úÀ» °æ¿ì, Minus°¡Ä¡ °è»ê
                    if mainmatch['frames'][i]['events'][j]['victimId']==idx:
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1
                        killerId = mainmatch['frames'][i]['events'][j]['killerId']
                        if killerId == T2[0]:
                            Team_liner = T1[0]
                        if killerId == T2[1]:
                            Team_liner = T1[1]
                        if killerId == T2[2]:
                            Team_liner = T1[2]
                        if killerId == T2[3]:
                            Team_liner = T1[3]
                        if killerId == T2[4]:
                            Team_liner = T1[4]


                        #Å¾ÀÏ°æ¿ì
                        def Calc_Team1_Top_D() :
                            minus_val1 = 0
                            if (math.ceil(sqrt(pow((float(csv["top_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["top_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T2[0] or T2[0] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                minus_val1 = (((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold'])))
                            return minus_val1
                        #¹ÌµåÀÏ°æ¿ì
                        def Calc_Team1_Mid_D() :
                            minus_val1 = 0
                            if (math.ceil(sqrt(pow((float(csv["mid_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["mid_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T2[2] or T2[2] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                minus_val1 = (((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold'])))
                            return minus_val1
                        #¹ÙÅÒÀÏ°æ¿ì
                        def Calc_Team1_Bot_D() :
                            minus_val1 = 0
                            if (math.ceil(sqrt(pow((float(csv["bot_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["bot_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T2[3] or T2[3] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) or (mainmatch['frames'][i]['events'][j]['killerId']==T1[4] or T1[4] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                minus_val1 = (((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold'])))
                            return minus_val1

                        if player_i == 0 :
                            calc_minus_value1 = Calc_Team1_Mid_D()
                            calc_minus_value1= Calc_Team1_Bot_D()
                        if player_i == 1 :
                            calc_minus_value1 = Calc_Team1_Top_D()
                            calc_minus_value1 = Calc_Team1_Mid_D()
                            calc_minus_value1 = Calc_Team1_Bot_D()
                        if player_i == 2 :
                            calc_minus_value1 = Calc_Team1_Top_D()
                            calc_minus_value1 = Calc_Team1_Bot_D()
                        if (player_i == 3) or (player_i ==4) :
                            calc_minus_value1 = Calc_Team1_Top_D()
                            calc_minus_value1 = Calc_Team1_Mid_D()

                        Total_minus_value1 = Total_minus_value1 + abs(calc_minus_value1)
                        calc_minus_value1 = 0




    ###################################


        Total_value1 = Total_value1 - Total_minus_value1
    
        roaming = roaming_reg(Total_value1)

        roaming_info = {}
        stat = player_info['stats']
        roaming_info['Roaming_Score'] = roaming

        player.set_champ(champ)
        player.set_roaming(roaming_info)
        player.set_RS(roaming)
        i = i + 1
        player_i = player_i+1
        Total_value1 = 0

    player_i = 0
    for player in teams[1].get_all_player():

        idx = player.get_idx()

        players_info = matches['participants']
        player_info = players_info[idx-1]

        champ = score_class.Find_Champion_Info(watcher, my_region, str(player_info['championId']), 'key', 1)["name"]

    ####################################
        for i in range(1,15) :
            for j in range(len(mainmatch['frames'][i]['events'])) :
                if (mainmatch['frames'][i]['events'][j]['type']=='CHAMPION_KILL'):

                    if mainmatch['frames'][i]['events'][j]['killerId']==idx or idx in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']:

                        time = mainmatch['frames'][i]['events'][j]['timestamp']
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1

                        #º¯¼ö¼³Á¤
                        victim = mainmatch['frames'][i]['events'][j]['victimId']
                        if victim == T1[0]:
                            Team_liner = T2[0]
                        if victim == T1[1]:
                            Team_liner = T2[1]
                        if victim == T1[2]:
                            Team_liner = T2[2]
                        if victim == T1[3]:
                            Team_liner = T2[3]
                        if victim == T1[4]:
                            Team_liner = T2[4]
                        #Å¾ÀÏ°æ¿ì
                        def Calc_Team2_Top_K() :
                            val2 = 0
                            if (math.ceil(sqrt(pow((float(csv["top_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["top_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T2[0] or T2[0] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                val2 = (((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(victim)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(victim)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(victim)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(victim)]['totalGold'])))
                            return val2
                        #¹ÌµåÀÏ°æ¿ì
                        def Calc_Team2_Mid_K() :
                            val2 = 0
                            if (math.ceil(sqrt(pow((float(csv["mid_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["mid_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T2[2] or T2[2] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                val2 = (((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(victim)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(victim)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(victim)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(victim)]['totalGold'])))
                            return val2
                        #¹ÙÅÒÀÏ°æ¿ì
                        def Calc_Team2_Bot_K() :
                            val2 = 0
                            if (math.ceil(sqrt(pow((float(csv["bot_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["bot_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T2[3] or (T2[3] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds'])) or (mainmatch['frames'][i]['events'][j]['killerId']==T2[4]) or (T2[4] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                val2 = (((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(victim)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(victim)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(victim)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(victim)]['totalGold'])))
                            return val2
                        if player_i == 0 :
                            calc_value2 = Calc_Team2_Mid_K()
                            calc_value2 = Calc_Team2_Bot_K()

                        if player_i == 1 :
                            calc_value2 = Calc_Team2_Top_K()
                            calc_value2 = Calc_Team2_Mid_K()
                            calc_value2 = Calc_Team2_Bot_K()

                        if player_i == 2 :
                            calc_value2 = Calc_Team2_Top_K()
                            calc_value2 = Calc_Team2_Bot_K()

                        if (player_i == 3) or (player_i == 4) :
                            calc_value2 = Calc_Team2_Top_K()
                            calc_value2 = Calc_Team2_Mid_K()



                        Total_value2 = Total_value2 + abs(calc_value2)
                        calc_value2 = 0
        #         if (mainmatch['frames'][i]['events'][j]['type']=='CHAMPION_KILL'):
                    #Àû ¶óÀÌ³Ê¿¡°Ô Á×¾úÀ» °æ¿ì, Minus°¡Ä¡ °è»ê
                    if mainmatch['frames'][i]['events'][j]['victimId']==idx:
                        time = math.ceil((mainmatch['frames'][i]['events'][j]['timestamp'])/1000/60)
                        present_time = time
                        past_time=time-1
                        killerId = mainmatch['frames'][i]['events'][j]['killerId']
                        if killerId == T1[0]:
                            Team_liner = T2[0]
                        if killerId == T1[1]:
                            Team_liner = T2[1]
                        if killerId == T1[2]:
                            Team_liner = T2[2]
                        if killerId == T1[3]:
                            Team_liner = T2[3]
                        if killerId == T1[4]:
                            Team_liner = T2[4]


                        #Å¾ÀÏ°æ¿ì
                        def Calc_Team2_Top_D() :
                            minus_val2 = 0
                            if (math.ceil(sqrt(pow((float(csv["top_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["top_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T1[0] or T1[0] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                minus_val2 = (((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold'])))
                            return minus_val2
                        #¹ÌµåÀÏ°æ¿ì
                        def Calc_Team2_Mid_D() :
                            minus_val2 = 0
                            if (math.ceil(sqrt(pow((float(csv["mid_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["mid_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T1[2] or T1[2] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                minus_val2 = (((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold'])))
                            return minus_val2
                        #¹ÙÅÒÀÏ°æ¿ì
                        def Calc_Team2_Bot_D() :
                            minus_val2 = 0
                            if (math.ceil(sqrt(pow((float(csv["bot_x"])-mainmatch['frames'][i]['events'][j]['position']['x']),2) + pow((float(csv["bot_y"])-mainmatch['frames'][i]['events'][j]['position']['y']),2))) < 2300 ) and (mainmatch['frames'][i]['events'][j]['killerId']==T1[3] or T1[3] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) or (mainmatch['frames'][i]['events'][j]['killerId']==T1[4] or T1[4] in mainmatch['frames'][i]['events'][j]['assistingParticipantIds']) :

                                minus_val2 = (((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['xp'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['xp']-mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['xp']))*2+
                                ((mainmatch['frames'][present_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][present_time]['participantFrames'][str(Team_liner)]['totalGold'])-
                                (mainmatch['frames'][past_time]['participantFrames'][str(killerId)]['totalGold']- mainmatch['frames'][past_time]['participantFrames'][str(Team_liner)]['totalGold'])))
                            return minus_val2
                        if player_i == 0 :
                            calc_minus_value2 = Calc_Team2_Mid_D()
                            calc_minus_value2 = Calc_Team2_Bot_D()

                        if player_i == 1 :
                            calc_minus_value2 = Calc_Team2_Top_D()
                            calc_minus_value2 = Calc_Team2_Mid_D()
                            calc_minus_value2 = Calc_Team2_Bot_D()

                        if player_i == 2 :
                            calc_minus_value2 = Calc_Team2_Top_D()
                            calc_minus_value2 = Calc_Team2_Bot_D()

                        if (player_i == 3) or (player_i ==4) :
                            calc_minus_value2 = Calc_Team2_Top_D()
                            calc_minus_value2 = Calc_Team2_Mid_D()


                        Total_minus_value2 = Total_minus_value2 + abs(calc_minus_value2)
                        calc_minus_value2 = 0



    ###################################
        Total_value2 = Total_value2 - Total_minus_value2
      
        roaming = roaming_reg(Total_value2)

        roaming_info = {}
        stat = player_info['stats']
        roaming_info['Roaming_Score'] = roaming

        player.set_champ(champ)
        player.set_roaming(roaming_info)
        player.set_RS(roaming)
        j = j + 1
        player_i = player_i+1
        Total_value2 = 0
    return teams
'''

def Calc_FinalScore(teams,csv):
    

    teams = [cal_finalscore_team(team, csv) for team in teams]

    return teams

def cal_finalscore_team(team, csv):

    players = team.get_all_player()
    line = np.array([player.get_all()[2:-1] for player in players])
    # print(line)
    # final_tmp = [[csv[key] for key in csv.keys() if 'final' in key] + [0]]
    # sup_tmp = [[csv[key] for key in csv.keys() if 'sup' in key]]
    
    final_weight2=[[float(csv["final_weight_top_1"]),float(csv["final_weight_top_2"]),float(csv["final_weight_top_3"]),float(csv["final_weight_top_4"]),float(csv["final_weight_top_5"]),float(csv["final_weight_top_6"])],
                            [float(csv["final_weight_jun_1"]),float(csv["final_weight_jun_2"]),float(csv["final_weight_jun_3"]),float(csv["final_weight_jun_4"]),float(csv["final_weight_jun_5"]),float(csv["final_weight_jun_6"])],
                            [float(csv["final_weight_mid_1"]),float(csv["final_weight_mid_2"]),float(csv["final_weight_mid_3"]),float(csv["final_weight_mid_4"]),float(csv["final_weight_mid_5"]),float(csv["final_weight_mid_6"])],
                            [float(csv["final_weight_bot_1"]),float(csv["final_weight_bot_2"]),float(csv["final_weight_bot_3"]),float(csv["final_weight_bot_4"]),float(csv["final_weight_bot_5"]),float(csv["final_weight_bot_6"])],
                            [float(csv["final_weight_sup_1"]),float(csv["final_weight_sup_2"]),float(csv["final_weight_sup_3"]),float(csv["final_weight_sup_4"]),float(csv["final_weight_sup_5"]),float(csv["final_weight_sup_6"])]]
    
#####
    final_weight_=[[float(csv["final_weight_top_1"]),float(csv["final_weight_top_2"]),float(csv["final_weight_top_3"]),float(csv["final_weight_top_4"]),float(csv["final_weight_top_5"]),float(csv["final_weight_top_6"])],
                            [float(csv["final_weight_jun_1"]),float(csv["final_weight_jun_2"]),float(csv["final_weight_jun_3"]),float(csv["final_weight_jun_4"]),float(csv["final_weight_jun_5"]),float(csv["final_weight_jun_6"])],
                            [float(csv["final_weight_mid_1"]),float(csv["final_weight_mid_2"]),float(csv["final_weight_mid_3"]),float(csv["final_weight_mid_4"]),float(csv["final_weight_mid_5"]),float(csv["final_weight_mid_6"])],
                            [float(csv["final_weight_sup_1"]),float(csv["final_weight_sup_2"]),float(csv["final_weight_sup_3"]),float(csv["final_weight_sup_4"]),float(csv["final_weight_sup_5"]),float(csv["final_weight_sup_6"])]]
    
    final_weight_top=[float(csv["final_weight_top_1"]),float(csv["final_weight_top_2"]),float(csv["final_weight_top_3"]),float(csv["final_weight_top_4"]),float(csv["final_weight_top_5"]),float(csv["final_weight_top_6"])]
    final_weight_jun=[float(csv["final_weight_jun_1"]),float(csv["final_weight_jun_2"]),float(csv["final_weight_jun_3"]),float(csv["final_weight_jun_4"]),float(csv["final_weight_jun_5"]),float(csv["final_weight_jun_6"])]
    final_weight_mid=[float(csv["final_weight_mid_1"]),float(csv["final_weight_mid_2"]),float(csv["final_weight_mid_3"]),float(csv["final_weight_mid_4"]),float(csv["final_weight_mid_5"]),float(csv["final_weight_mid_6"])]
    final_weight_bot=[float(csv["final_weight_bot_1"]),float(csv["final_weight_bot_2"]),float(csv["final_weight_bot_3"]),float(csv["final_weight_bot_4"]),float(csv["final_weight_bot_5"]),float(csv["final_weight_bot_6"])]
    final_weight_sup=[float(csv["final_weight_sup_1"]),float(csv["final_weight_sup_2"]),float(csv["final_weight_sup_3"]),float(csv["final_weight_sup_4"]),float(csv["final_weight_sup_5"]),float(csv["final_weight_sup_6"])]
    final = []
    final.append(final_weight_top)
    final.append(final_weight_jun)
    final.append(final_weight_mid)
    final.append(final_weight_bot)
    final.append(final_weight_sup)
    print(final)
    final_weight_ = np.array(final_weight_,dtype=np.float64)
    final_weight_sup = np.array(final_weight_sup, dtype= np.float64)
    # result = np.round(np.append(np.dot(final_weight_top, line[0,:].T), np.dot(final_weight_jun, line[1,:].T), np.dot(final_weight_mid, line[2,:].T),\
    #                             np.dot(final_weight_bot, line[3,:].T), np.dot(final_weight_sup, line[4,:].T)))

    # result = np.round(np.append(np.dot(final_weight_top, line[0,:].T), np.dot(final_weight_jun, line[1,:].T)),1)
   
    # print(result)
    result = []
    for i in range(0,5):
        result.append(np.round(np.dot(final[i], line[i,:].T),1))
    print(result)
    # print("line : ",line[:4,:].T)
    # print("line : ",line[-1:,:].T)
    # print("final_weight_ : ",final_weight_)
    # print("final_weight_sup : ",final_weight_sup)
    # print(" :",np.dot(final_weight_, line[:4,:].T))
    # print(" :",np.dot(final_weight_sup, line[-1:,:].T))
    # result = np.round(np.append(np.dot(final_weight_, line[:4,:].T) , np.dot(final_weight_sup, line[-1:,:].T)), 1)
    # print("result :", result)
#####

    # print(final_weight2)
    # final_weight = np.array(final_weight2, dtype=np.float64 )
    # print("1")
    # print(final_weight)
    # print(line.T)
    # ll = line.T
# '''
# n,n에 있는 값만 뽑기
# '''
    # print(np.dot(final_weight,ll))
    # result = np.round(np.dot(final_weight,line.T), 1)
    # print(result)
    # print(result)
    # final_weight = np.array(final_tmp,dtype=np.float64)
    # sup_weight = np.array(sup_tmp, dtype= np.float64)

    # result = np.round(np.append(np.dot(final_weight, line[:4,:].T) , np.dot(sup_weight, line[-1:,:].T)), 1)
    
    
    for player, s in list(zip(players, result)):
        player.set_LS(s)
        
    return team

def compare(teams,crawling_score,input_Id):
    
    final_score ={}
    for player in teams[0].get_all_player() + teams[1].get_all_player():
        tmp = player.get_all()
        final_score[tmp[1]] = [tmp[0]] + tmp[2:]
    
    df = pd.DataFrame(final_score)
    df_c = pd.DataFrame(crawling_score)
    pd_concat = pd.concat([df, df_c], sort = False)
    compare_df = pd_concat.T
    compare_df.columns = ["소환사명", "오브젝트", "전투력", "시야", "성장력","로밍가치","원딜케어력","GameEyE","OP.GG","YOUR.GG"]

    compare_df.to_csv(path_or_buf = input_Id+".csv", header = True, index = True,  encoding = 'CP949')
    
    return True