from js import document, console
from pyodide import create_proxy

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


CREATE = "CREATE"
REMOVE = "REMOVE"
REPLACE = "REPLACE"
UPDATE = "UPDATE"

class Pie():
    """
    Element : 
        - type
        - props
        - state
        - children

    Tree : 

        {
            type: "div", 
            props: {}, 
            state: {}, 
            children: [
                {
                    type: "h1", 
                    props: {}, 
                    state: {}, 
                    children: "Hello world"
                },
                {
                    type: "div", 
                    props: {}, 
                    state: {}, 
                    children: [
                        {
                            type: "p", 
                            props: {}, 
                            state: {}, 
                            children: "p1"
                        },
                        {
                            type: "p", 
                            props: {}, 
                            state: {}, 
                            children: "p2"
                        },
                        {
                            type: "p", 
                            props: {}, 
                            state: {}, 
                            children: "p3"
                        },
                    ]
                }
            ]
        }
    """

    def __init__(self):
        self.currVDOM = None 
        self.prevVDOM = None    #check if both currVDOM and prevVDOM needed
        self.renderElement = None 
        self.root = None    #variable to store root DOM element
        self.store = {}
        #self.proxies={}

    def dispatchEvent(self):
        # create new VDOM
        self.prevVDOM=self.currVDOM
        self.currVDOM=self.renderElement()
        #self.root.removeChild(self.root.firstElementChild)
        #self.root.appendChild(self.createElement(self.currVDOM))
        # reconciliation
        # console.log("CALLING RECONCILE")
        self.reconcile(None, self.root.firstChild, self.prevVDOM, self.currVDOM)
        """
        self.diffTree(self.prevVDOM,self.currVDOM, self.rootElement)
        render
        """ 

    def useState(self, name, initialState = None):
        # if state already return it, else create the new state
        try:
            return self.store[name]
        except:
            self.store[name] = State(initialState, self.dispatchEvent)
            return self.store[name]
    

    def compareTag(self, oldElem, newElem):
        return (oldElem and newElem and oldElem["type"] != newElem["type"])

    def isFunc(self, item):
        return hasattr(item, "__call__")

    def compareProps(self, oldElem, newElem, DOM):
        """
            Function to compare props and return those to be changed
            
            Cases :
                - Creating new prop
                - Changing value of existing prop
                - Removing a prop
            
            # create
            oldProp={"style":"blue","onclick":"lol"}
            newProp={"style":"red","onclick":"lol","newattr":"gullu"}

            # change
            oldProp={"style":"blue","onclick":"lol"}
            newProp={"style":"red","onclick":"lol"}
            
            # remove
            oldProp={"style":"blue","onclick":"lol"}
            newProp={"style":"red"}
        """
        hasChanged = False
        changes = {
            "create": {},
            "remove": []
        }

        if oldElem["props"] == None and newElem["props"]:
            changes["create"] = newElem["props"]
            hasChanged = True
        
        elif newElem["props"] == None and oldElem["props"]:
            changes["remove"] = oldElem["props"].keys()
            hasChanged= True

        elif newElem["props"] == None and oldElem["props"] == None:
            return hasChanged, changes
        
        else :
            #1) common keys
            #   - values of the keys are different
            #2) keys present in new but not in old
            #3) keys present in old but not new
            console.log(newElem["type"], "props : ")
            for newProp in newElem["props"].keys():
                # create
                if newProp not in oldElem["props"]:
                    changes["create"][newProp] = newElem["props"][newProp]
                    hasChanged = True

                # changed
                elif (
                    (newElem["props"][newProp] != oldElem["props"][newProp]) 
                    or 
                    (
                        (self.isFunc(newElem["props"][newProp]) and self.isFunc(oldElem["props"][newProp]))
                        and 
                        (newElem["props"][newProp]() != DOM.getAttribute('value'))
                    )
                    ):
                    changes["create"][newProp] = newElem["props"][newProp]
                    hasChanged = True
                    # del oldElem["props"][newProp]

            for oldProp in oldElem["props"].keys():
                # remove
                if oldProp not in newElem["props"]:
                    changes["remove"].append(oldProp)
                    hasChanged = True
       
        for i in changes["create"].keys():
            console.log(i)
    
        return hasChanged, changes

    def compareKey(self, oldElem, newElem):
        return (oldElem["key"] != newElem["key"])

    def reconcile(self, parentDOM, DOM, oldElem = None, newElem = None):
        ##
        if oldElem == None and newElem == None: #needed to end reconciliation
            return
        
        if oldElem == None:
            # create
            parentDOM.appendChild(self.createElement(newElem))
            return

        if newElem == None:
            # remove
            parentDOM.removeChild(DOM)
            return

        """
        Cases : 
            1. new is str, old is str
            2. new is str, old is element
            3. new is element, old is str
            4. new is element, old is element
        """
        # text node handling
        if type(newElem) is str:
            if oldElem != newElem:
                parentDOM.removeChild(DOM)
                parentDOM.appendChild(document.createTextNode(newElem))
            return
        elif type(oldElem) is str:
            parentDOM.removeChild(DOM)
            parentDOM.appendChild(document.createElement(newElem))
            return

        # if two tags are different, rerender the whole subtree
        if self.compareTag(oldElem, newElem):
            #remove child
            parentDOM.removeChild(DOM)
            #create and append child
            parentDOM.appendChild(self.createElement(newElem))
            return
        else:
            # if props are different, make necessary changes to the DOM node
            propsHaveChanged, propChanges = self.compareProps(oldElem, newElem, DOM)
            if propsHaveChanged:
                for key in propChanges["create"].keys():    #create and change props
                    # console.log(newElem["type"], key)
                    if key[0:2] == "on":
                        DOM.removeEventListener(key[2:], oldElem['props'][key])
                        newElem['props'][key] = create_proxy(newElem['props'][key])
                        DOM.addEventListener(key[2:], newElem['props'][key])
                        pass
                    elif hasattr(newElem['props'][key], "__call__"):
                        DOM.setAttribute(key, newElem['props'][key]())
                    else :
                        DOM.setAttribute(key, newElem['props'][key])

                for key in propChanges["remove"]:
                    DOM.removeAttribute(key)

            if newElem["children"] == None:
                # remove all
                for child in DOM.children:
                    DOM.removeChild(child)
                return
            
            if oldElem["children"] == None:
                # append all
                for child in newElem["children"]:
                    if type(child) is str:
                        DOM.appendChild(document.createTextNode(child))
                    DOM.appendChild(self.createElement(child))
                return
                    
            if type(oldElem["children"]) is str or type(newElem["children"]) is str:
                self.reconcile(DOM, DOM.firstChild, oldElem["children"], newElem["children"])
                return

            if hasattr(newElem['children'], "__call__"):
                # assumes a function call returns a string
                for i in DOM.children:
                    DOM.removeChild(i)
                DOM.innerText = ""
                DOM.appendChild(document.createTextNode(newElem['children']()))
                return
                
            
            """
            Cases :
                1. Old is no children, New has no children
                2. Old has no children, New has children
                3. Old has children, New has no children
                1. Old and new have same number of children
                    - no changes in children
                    - changes in children
                2. Old has more children
                    - remove excess children
                3. New has more children
                    - add additional children
                        - text node
                        - element node
            """
            len_old = len(oldElem['children'])
            len_new = len(newElem['children'])

            if len_old == len_new:
                for i in range(len_old):
                    # console.log(DOM.children,len(oldElem['children']),len(newElem['children']))
                    # console.log(oldElem['children'][i])
                    var1=DOM.children[i]
                    var2=oldElem['children'][i]
                    var3=newElem['children'][i]
                    self.reconcile(DOM, var1, var2, var3)
                        
            else:     
                # old element has more number of children
                if len_old > len_new:

                    for i in range(len_new):
                        self.reconcile(DOM, DOM.children[i], oldElem["children"][i], newElem["children"][i])
                            
                    # remove the excess elements
                    for i in range(len_new,len_old):
                        DOM.removeChild(DOM.children[i])

                # new has more number of elements
                else:

                    for i in range(len_old):
                        self.reconcile(DOM, DOM.children[i], oldElem["children"][i], newElem["children"][i])

                    # add new elements
                    for i in range(len_old,len_new):
                        if type(newElem['children'][i]) is str:
                            DOM.appendChild(document.createTextNode(newElem['children'][i]))
                        else:
                            DOM.appendChild(self.createElement(newElem['children'][i]))

    
    def patchPieElement(self, parent, oldElement, newElement):
        """
        Function to update child
            - create -> adding a new node
            - remove -> remove the node
            - replace -> type changes
        """
        pass
        
    def createPieElement(self, key, tag, props, children):
        """
        Function to create vdom element
        """
        #return PieElement(key=key, type=tagName, props=props, state={}, children=children)
        if type(tag) is str:
            return {'key':key,'type':tag,'props':props,'children':children}
        else:
            return tag(props)

    def createElement(self, element):
        """
        Function to create an actual DOM element from the virtual DOM element
        """
        el = document.createElement(element['type'])

        if element['children']:
            if hasattr(element['children'], "__call__"):
                # assumes a function call returns a string
                el.appendChild(document.createTextNode(element['children']()))
            elif type(element['children']) is str:
                el.appendChild(document.createTextNode(element['children']))
            elif type(element['children']) is list:
                for i in element['children']:
                    if type(i) is str:  
                        el.appendChild(document.createTextNode(element['children']))
                    else:
                        el.appendChild(self.createElement(i))

        if element['props']:
            for key in element['props'].keys():
                if key[0:2] == "on":
                    element["props"][key] = create_proxy(element['props'][key])
                    el.addEventListener(key[2:], element['props'][key])
                elif hasattr(element['props'][key], "__call__"):
                    el.setAttribute(key, element['props'][key]())
                else :
                    el.setAttribute(key, element['props'][key])

        return el


    def render(self, element, root):    #is it possible to render to appropriate node instead of root?
            """
            Function to handle the render
            """
            self.renderElement = element
            self.root = root
            self.currVDOM = self.renderElement()
            root.appendChild(self.createElement(self.currVDOM))

