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
        # TODO : Check the need for a deepcopy and the performance 
        # if action is a function
        if hasattr(action, '__call__'):
            update = action(deepcopy(self.state))
            # TODO : test this
            # Skip calling rerender event if update remains same as current state
            if (type(self.state) == type(update) and self.state == update):
                return
            else:
                self.state = update
        
        # if action is a dictionary
        elif type(action) is dict and type(self.state) is dict:
            for key in action.keys():
                self.state[key] = action[key]
        else:
            # TODO : test this
            # Skip calling rerender event if update remains same as current state
            if self.state == action:
                return
            self.state = action

        self.dispatcher()

    def get(self, key = None):
        """
            Getter function for state
        """
        if key and type(self.state) is dict and key in self.state.keys():
            return deepcopy(self.state[key])
        
        return deepcopy(self.state)
