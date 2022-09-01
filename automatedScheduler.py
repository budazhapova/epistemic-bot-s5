from tkinter.tix import TList
from main import main_function
from recordManager import retrieve_formulas, json_to_tree, write_formulas
from stringConverter import translate_formula
from twitterPublisher import publish_tweet
from apscheduler.schedulers.background import BackgroundScheduler

def publish_to_twitter():
    t_list = retrieve_formulas("tautologies")
    # if there are no tautologies recorded, keep trying until one is generated
    if not t_list:
        output = None
        while output != 2:
            output = main_function("generate")
        # load the updated list of tautologies
        t_list = retrieve_formulas("tautologies")
    tree_formula = json_to_tree(t_list[0])
    t_list.pop(0)
    line_formula = translate_formula(tree_formula)
    # post the translated formula on Twitter
    publish_tweet(line_formula)
    # overwrites the tautology files with the remaining formulas
    write_formulas("tautologies", None, t_list)
    if len(t_list) < 3:
        # generate enough tautologies for the next day and record them
        new_tautologies = len(t_list)
        while new_tautologies < 6:
            result = main_function("generate")
            if result == 2:
                new_tautologies += 1


scheduler = BackgroundScheduler()
scheduler.add_job(publish_to_twitter(), 'interval', hours=4)
scheduler.start()

# TODO: TEST WITH SHORTER INTERVAL