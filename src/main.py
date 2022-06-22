from numpy import diff
from js import document
from pyodide import create_proxy
from element import PieElement
from event_consts import CREATE,REMOVE,REPLACE,UPDATE

class Pie():
    """
    Element : 
        - type
        - props
        - state
        - children

    Tree : 

        {type: "div", props: {}, state: {}, children: [
            {type: "h1", props: {}, state: {}, children: "Hello world"}
            {type: "h1", props: {}, state: {}, children: "Hello world"}
            {type: "h1", props: {}, state: {}, children: "Hello world"}
            {type: "h1", props: {}, state: {}, children: "Hello world"}
            {type: "h1", props: {}, state: {}, children: "Hello world"}
        ]}
    """

    def __init__(self):
        self.VDOM = {} #change
        self.rootElement = None
        self.state = {}

    def set(self, name, data):
        self.state[name] = data

    def useState(self, name, initialState = None):
        self.state[name] = initialState
        func = lambda x: self.set(name, x)
        return self.state[name], func
    
        

    def changed(self, oldElement : PieElement, newElement: PieElement):
        return (oldElement.type != newElement.type)

    def diffTree():
        # call diff on the whole tree
        pass

    def diff(self, oldElement = None, newElement = None):
        """
        Function to perform diff on two nodes
        """
        if oldElement == None:
            return CREATE
        elif newElement == None:
            return REMOVE
        elif self.changed(oldElement, newElement):
            return REPLACE
        else:
            return UPDATE

    
    def patchPieElement(self, parent, oldElement, newElement):
        """
        Function to update child
            - create -> adding a new node
            - remove -> remove the node
            - replace -> type changes
        """
        pass


    def createPieElement(self, key, tagName, props, children):
        """
        Function to create vdom element
        """
        return PieElement(key=key, type=tagName, props=props, state={}, children=children)


    def createElement(self, element:PieElement):
        """
        Function to create an actual DOM element from the virtual DOM element
        """

        el = document.createElement(element.type)

        if element.children:
            if type(element.children) is str:
                el.appendChild(document.createTextNode(element.children))
            elif type(element.children) is list:
                for i in element.children:
                    el.appendChild(i)

        if element.props:
            for key in element.props.keys():
                if key[0:2] == "on":
                    el.addEventListener(key[2:], create_proxy(element.props[key]))
                else :
                    el.setAttribute(key, element.props[key])

        return el


    def render(self, element, root):
            """
            Function to handle the render
            """
            root.appendChild(self.createElement(element))