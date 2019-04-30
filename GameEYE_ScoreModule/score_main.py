import score_calc as s_calc
import score_class as s_class
import sys

# from score_class import make_matches

# from score_calc import make_vision_score
# from score_calc import make_object_score
# from score_calc import Calc_Growth
# from score_calc import Calc_Careforce
# from score_calc import Calc_Roaming,alc_FinalScore
# from score_calc import crawl_other_score, compare

def main(target_match):
    
    api_key = 'RGAPI-891dfb1c-f002-45dc-9545-ae5e5675e76a'
    my_region = 'KR'
    # target_match = "3577231010" # target gameId # 3560163449 game of winners tempo #3577231010
    # global champion_dict

    #
    watcher,champion_dict,csv  = s_class.init(api_key,my_region)
    
    matches, timeline, teams = s_class.make_matches(watcher, my_region, target_match,champion_dict)
    print("1")

    teams = s_calc.make_vision_score(matches, teams,csv)
    print("1")

    teams = s_calc.make_fight_score(matches, teams,csv)
    print("1")

    teams = s_calc.make_object_score(timeline, teams,csv)
    print("1")

    teams = s_calc.Calc_Growth(teams, timeline, matches, watcher, csv, my_region)
    print("1")

    teams = s_calc.Calc_Careforce(timeline, teams, matches, watcher, csv, my_region)
    print("1")

    teams = s_calc.Calc_Roaming(teams, timeline, matches, watcher, csv, my_region)
    print("1")

    teams = s_calc.Calc_FinalScore(teams,csv)
    print("1")

    crawling_score = s_calc.crawl_other_score(watcher, my_region, teams[0].top, target_match, champion_dict, csv)

    compare_df = s_calc.compare(teams, crawling_score,target_match)
    print("Finish")
    
    return True

if __name__ == "__main__":
    # target_match = input("Target GameId를 입력하시오 : ")
    # main(target_match)

    target_match = (sys.argv[1])
    print(target_match)
    main(target_match)

