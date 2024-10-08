"""
This is a file to have a helper class.
This will store all the redundant data which shouldn't really be
inside the mongoDB database.
"""

class Helper:
    experiments:dict = {
        0: "Introduction.".upper(),
        1: "HOLOCAUST TWIN.",
        2: "The Harlow Monkey Experiments.".upper(),
        3: "San Quentin testicular transplants.".upper(),
        4: "Freezing experiments.".upper(),
        5: "Mustard gas experiment.".upper(),
        6: "Head injury experiments.".upper(),
        7: "CANNIBAL ISLAND.",
        8: "LOBOTOMY.",
        9: "ferret brain experiment.".upper(),
        10: "Dog's Head Experiment.".upper(),
    }
    
    attempt:dict = {
        "easy": 0,
        "medium": 1,
        "hard": 2
    }
    
    reverse_attempt:dict = {
        0: "easy",
        1: "medium",
        2: "hard"
    }

    secret_experiement:dict = {
        16: "ESCAPE DAY"
    }
    
    @staticmethod
    def answer_validator(attempt:dict)->bool:
        if int(attempt["experiment"]) in Helper.experiments.keys() and int(attempt["etype"]) in [0,1,2]:
            return True
        return False
    
def authenticator(userdata, context):
    context.update({"authenticated": True, "avatar_img": userdata["_id"]})
    return context
