class Component():
    def __init__(self,func,key,props,instanceId):   # PROTOTYPE func-function callback, key-string, props-dictionary, instanceId-integer
        self.instanceId=instanceId  # HACK store time of creation as attribute, and use it while hashing to form a unique instanceId
        self.func=func
        self.props=props
        self.key=None
        self.name=func.__name__
        self.VDOMFrag=None
        self.DOMRef=None

    # CHECK Is an update function required? - keys,props,change while recreating VDOM
    def createFragment(self):
        self.VDOMFrag = self.func(self.props)

    def attachDOMRef(self,ref):
        self.DOMRef=ref