from datetime import datetime

TEST_RUNS = 3000000

def set_method(oldElem, newElem):
    changes = {
        "create": None,
        "remove": None
    }
    hasChanged = False

    old_props_keys = set(oldElem["props"].keys())
    new_props_keys = set(newElem["props"].keys())

    changes["create"] = old_props_keys.difference(new_props_keys)
    changes["remove"] = new_props_keys.difference(old_props_keys)

    changes["create"].update(set(
        filter(
            lambda x: newElem["props"][x] != oldElem["props"][x], 
            new_props_keys.intersection(old_props_keys)
        )
    ))

    if (len(changes["create"]) > 0 or len(changes["remove"]) > 0):
        hasChanged = True

    return hasChanged, changes

def iter_method(oldElem, newElem):
    changes = {
        "create": {},
        "remove": []
    }
    hasChanged = False

    for newProp in newElem["props"].keys():
        # create
        if newProp not in oldElem["props"]:
            changes["create"][newProp] = newElem["props"][newProp]
            hasChanged = True

        # changed
        elif (
            (newElem["props"][newProp] != oldElem["props"][newProp]) 
            ):
            changes["create"][newProp] = newElem["props"][newProp]
            hasChanged = True
            # del oldElem["props"][newProp]

    for oldProp in oldElem["props"].keys():
        # remove
        if oldProp not in newElem["props"]:
            changes["remove"].append(oldProp)
            hasChanged = True 

    return hasChanged, changes

def fil(newProp, oldElem, newElem):
        if newProp not in oldElem["props"]:
            return True
        # changed
        elif (
            (newElem["props"][newProp] != oldElem["props"][newProp]) 
            ):
            return True

def fil2(oldProp, newElem):
        if oldProp not in newElem["props"]:
            return True

def filter_method(oldElem, newElem):
    hasChanged = False

    changes = {
        "create": list(filter(lambda x: fil(x, oldElem, newElem), newElem["props"].keys())),
        "remove": list(filter(lambda x: fil2(x, newElem), oldElem["props"].keys()))
    }

    return hasChanged, changes

def compre_method(oldElem, newElem):
    changes = {}
    hasChanged = False

    old_props_keys = oldElem["props"].keys()
    new_props_keys = newElem["props"].keys()

    changes["create"] = [i for i in new_props_keys if ((i not in old_props_keys) or (oldElem["props"][i] != newElem["props"][i]))]
    changes["remove"] = [i for i in old_props_keys if i not in new_props_keys]


    if (len(changes["create"]) > 0 or len(changes["remove"]) > 0):
        hasChanged = True
        
    return hasChanged, changes

def test():
    oldElem = {
        "props": {
            "style": "border: 1px solid black;",
            "id": "1",
            "data-x": "1" + "_p_tag",
            "data-aria": "1"
        }
    }

    newElem = {
        "props": {
            "style": "border: 1px solid black;",
            "data-x": "2" + "_p_tag",
            "data-aria": "2"
        }
    }

    start = datetime.now()
    for i in range(0, TEST_RUNS):
        hasChanged, changes = set_method(oldElem, newElem)
    end = datetime.now()

    print("SET METHOD :", str(end - start))
    print(changes, "\n")
    
    start = datetime.now()
    for i in range(0, TEST_RUNS):
        hasChanged, changes = iter_method(oldElem, newElem)
    end = datetime.now()
    
    print("ITER METHOD :", str(end - start))
    print(changes, "\n")

    start = datetime.now()
    for i in range(0, TEST_RUNS):
        hasChanged, changes = filter_method(oldElem, newElem)
    end = datetime.now()
    
    print("FILTER METHOD :", str(end - start))
    print(changes, "\n")

    start = datetime.now()
    for i in range(0, TEST_RUNS):
        hasChanged, changes = compre_method(oldElem, newElem)
    end = datetime.now()
    
    print("COMPRE METHOD :", str(end - start))
    print(changes, "\n")

test()
