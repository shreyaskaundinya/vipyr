from js import console
from copy import deepcopy

class State:
    def __init__(self, initialState, dispatcher):
        self.state = initialState
        self.dispatcher = dispatcher
    
    def set(self, action):
        """
            Setter function for state
        """
        
        """
            Cases : 
                Based on state type:
                    - dict
                    - list
                    - set
                    - tuple -> immutable
                    - number, string, float, bool -> immutable
                    - others
                Based on action type:
                    - function action
                    - dictionary update
                    - value update (immutable)
                    - array
        """
        
        # if action is a function
        if hasattr(action, "__call__"):
            self.state = action(deepcopy(self.state))
        
        # if action is a dictionary
        elif type(action) is dict and type(self.state) is dict:
            for key in action.keys():
                self.state[key] = action[key]
        else:
            self.state = action

        # console.log("called set with", self.state)
        self.dispatcher()

    def get(self, key = None):
        """
            Getter function for state
        """
        if key and type(self.state) is dict and key in self.state.keys():
            return deepcopy(self.state[key])
        
        return deepcopy(self.state)
