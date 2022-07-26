class Component():
    def __init__(self,func,key,props,instanceId, deleteInstance):   # PROTOTYPE func-function callback, key-string, props-dictionary, instanceId-integer
        self.instanceId=instanceId  # HACK store time of creation as attribute, and use it while hashing to form a unique instanceId
        self.func=func
        self.props=props
        self.oldKey=None
        self.newKey=key
        self.name=func.__name__
        self.oldVDOMFrag=None
        self.newVDOMFrag=None
        self.deleteInstance = deleteInstance
        self.DOMRef=None
    '''
    Old:
    App id=1
        div
            p
            div
            Content 
            Content 
            Content id="suraj_the_scare_crow_macha_who_eats_dosa_and_curd_rice_every_day_.com"
    New:
    App id=1
        div
            p
            div
            Content id=234
            Content id=256
            Content id=789
            Content id="suraj....."
    
    state set => do the state update => diff(App) => create new VDOM 
    => RPE(div)
        => RPE(p)
        => RPE(div)
        => RPE(Content id=234) => create an instance id
        => RPE(Content id=789) 
        => RPE(Content id="suraj.....")

    App
        div
            p 
            div
            TripleContent key=0
                Content key=0 props={}
                Content key=1 props={}
                Content key=2 props={}
            TripleContent key=1
                Content key=0 props={}
                Content key=1 props={}
                Content key=2 props={}
                                                                        
    '''
    # CHECK Is an update function required? - keys,props,change while recreating VDOM
    def createFragment(self,props):
        self.props = props
        tempInstance = self.func(props)
        self.newVDOMFrag = tempInstance.newVDOMFrag
        self.deleteInstance(tempInstance.instanceId)

    def attachDOMRef(self,ref):
        self.DOMRef=ref