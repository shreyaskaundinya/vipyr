class PieElement():
    __slots__=['type','props','state','key','children']
    def __init__(self,type='',props={},state={},key=None,children=None):
        self.type=type
        self.props=props
        self.state=state
        self.key=key
        self.children=children
    def __str__(self):
        print(f"Type: {self.type}")
        print(f"Props: {self.props}")
        print(f"State: {self.state}")
        print(f"Number of children: {len(self.children)}")

