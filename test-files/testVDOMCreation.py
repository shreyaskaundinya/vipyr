from datetime import datetime

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


def h(type, props, state={}, key=None, children=None):
    return PieElement(type, props, state, key, children)



def createTree():
    return h("div", None, None, None, [
        h("p", None, None, None, "Hello world"),
        h("p", None, None, None, "Hello world"),
        h("p", None, None, None, "Hello world"),
        h("p", None, None, None, "Hello world"),
        h("p", None, None, None, "Hello world"),
        h("div", None, None, None, [
            h("p", None, None, None, "Hello world"),
            h("p", None, None, None, "Hello world"),
            h("p", None, None, None, "Hello world"),
            h("p", None, None, None, "Hello world"),
            h("div", None, None, None, [
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
            ]),
            h("div", None, None, None, [
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
            ]),
            h("div", None, None, None, [
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),

            h("div", None, None, None, [
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("p", None, None, None, "Hello world"),
                h("div", None, None, None, [
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                ]),
                h("div", None, None, None, [
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                ]),
                h("div", None, None, None, [
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                    h("p", None, None, None, "Hello world"),
                ])
                ])
            ]),
        ])
    ])

start = datetime.now()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
x = createTree()
end = datetime.now()

print(end, start, end-start)
