from datetime import datetime
import sys

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

def d(type, props, state={}, key=None, children=None):
    return {"type": type, "props": props, "state": state, "children": children}


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


def createDictTree():
    return d("div", None, None, None, [
        d("p", None, None, None, "Hello world"),
        d("p", None, None, None, "Hello world"),
        d("p", None, None, None, "Hello world"),
        d("p", None, None, None, "Hello world"),
        d("p", None, None, None, "Hello world"),
        d("div", None, None, None, [
            d("p", None, None, None, "Hello world"),
            d("p", None, None, None, "Hello world"),
            d("p", None, None, None, "Hello world"),
            d("p", None, None, None, "Hello world"),
            d("div", None, None, None, [
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
            ]),
            d("div", None, None, None, [
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
            ]),
            d("div", None, None, None, [
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),

            d("div", None, None, None, [
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("p", None, None, None, "Hello world"),
                d("div", None, None, None, [
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                ]),
                d("div", None, None, None, [
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                ]),
                d("div", None, None, None, [
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                    d("p", None, None, None, "Hello world"),
                ])
                ])
            ]),
        ])
    ])

test_iterations = int(sys.argv[1])

start = datetime.now()
for i in range(0, test_iterations):
    createTree() 
end = datetime.now()

print(end, start, end-start)


start = datetime.now()
for i in range(0, test_iterations):
    createDictTree() 
end = datetime.now()

print(end, start, end-start)
#need to test rerendering time
