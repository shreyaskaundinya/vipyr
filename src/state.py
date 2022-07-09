from js import console

class State:
    def __init__(self, initialState, dispatcher):
        self.state = initialState
        self.dispatcher = dispatcher
        # console.log("called init with ", initialState)
    
    def set(self, action):
        # console.log("CALLING STATE SET")
        if hasattr(action, "__call__"):
            self.state = action(self.state)

        if type(action) is dict and type(self.state) is dict:
            for key in action.keys():
                self.state[key] = action[key]
        else:
            self.state = action

        # console.log("called set with", self.state)
        self.dispatcher()

    def get(self):
        # console.log("called get => ", self.state)
        return self.state
