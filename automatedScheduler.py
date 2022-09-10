from main import main_function
from recordManager import retrieve_formulas, json_to_tree, write_formulas
from stringConverter import translate_formula
from twitterPublisher import publish_tweet
from apscheduler.schedulers.blocking import BlockingScheduler
from random import seed, randint

# SUMMARY: this is the file that is always running on the host device. generates or retrieves a tautology to publish on Twitter
#   every 4 hours and generates tautologies in advance so as to keep a precise schedule

def publish_to_twitter():
    t_list = retrieve_formulas("tautologies")
    seed()
    # if there are no tautologies recorded, keep trying until one is generated
    if not t_list:
        output = None
        while output != 2:
            output = main_function("generate", randint(3,120))
        # load the updated list of tautologies
        t_list = retrieve_formulas("tautologies")
    tree_formula = json_to_tree(t_list[0])
    t_list.pop(0)
    line_formula = translate_formula(tree_formula)[0]
    # post the translated formula on Twitter
    publish_tweet(line_formula)
    # overwrites the tautology files with the remaining formulas
    write_formulas("tautologies", None, t_list)
    if len(t_list) < 3:
        # generate enough tautologies for the next day and record them
        new_tautologies = len(t_list)
        while new_tautologies < 6:
            result = main_function("generate", randint(3,120))
            if result == 2:
                new_tautologies += 1


scheduler = BlockingScheduler()
scheduler.add_job(publish_to_twitter, 'interval', hours=4)
scheduler.start()