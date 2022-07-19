from js import document, console
from pyodide import create_proxy, to_js

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


CREATE = "CREATE"
REMOVE = "REMOVE"
REPLACE = "REPLACE"
UPDATE = "UPDATE"
from datetime import datetime

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
        console.clear()

    def dispatchEvent(self):
        start = datetime.now()
        # create new VDOM
        self.prevVDOM=self.currVDOM
        self.currVDOM=self.renderElement()

        # rerender whole tree
        #self.root.removeChild(self.root.firstElementChild)
        #self.root.appendChild(self.createElement(self.currVDOM))

        # reconciliation
        self.reconcile(None, self.root.firstChild, self.prevVDOM, self.currVDOM)
        
        end = datetime.now()

        console.log("RECONCILATION TOOK : ", to_js(str(end-start)))

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
            return False, changes
        else :            
            # props in new not in old => create
            # props in old not in new => remove
            # props in old and new but changed => change
            
            # SET APPROACH
            """old_props_keys = set(oldElem["props"].keys())
            new_props_keys = set(newElem["props"].keys())

            changes["create"] = old_props_keys.difference(new_props_keys)
            changes["remove"] = new_props_keys.difference(old_props_keys)

            changes["create"].update(set(
                filter(
                    lambda x: newElem["props"][x] != oldElem["props"][x], 
                    new_props_keys.intersection(old_props_keys)
                )
            ))

            if (len(changes["create"]) > 0 or len(changes["remove"]) > 0):
                hasChanged = True"""


            # ITERATIVE APPROACH
            for newProp in newElem["props"].keys():
                # create
                if newProp not in oldElem["props"]:
                    changes["create"][newProp] = newElem["props"][newProp]
                    hasChanged = True

                # changed
                elif (
                    (newElem["props"][newProp] != oldElem["props"][newProp]) 
                    ):
                    changes["create"][newProp] = newElem["props"][newProp]
                    hasChanged = True
                    # del oldElem["props"][newProp]

            for oldProp in oldElem["props"].keys():
                # remove
                if oldProp not in newElem["props"]:
                    changes["remove"].append(oldProp)
                    hasChanged = True
    
        return hasChanged, changes

    def compareKey(self, oldElem, newElem):
        return (oldElem["key"] != newElem["key"])

    def reconcile(self, parentDOM, DOM, oldElem = None, newElem = None):
        ##
        if oldElem == None and newElem == None: #needed to end reconciliation
            console.log("RENDER CASE : oldElem none, newElem none")
            return
        
        if oldElem == None:
            # create
            console.log("RENDER CASE : oldElem none, newElem exists")
            parentDOM.appendChild(self.createElement(newElem))
            return

        if newElem == None:
            # remove
            console.log("RENDER CASE : oldElem exists, newElem none")
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
                """
                if DOM != None or oldElem != "":
                    parentDOM.removeChild(DOM)
                """
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
            console.log("RENDER CASE : Tags are different")
            parentDOM.removeChild(DOM)
            #create and append child
            parentDOM.appendChild(self.createElement(newElem))
            return

        else:
            # --------------------------------------------------
            
            # if props are different, make necessary changes to the DOM node
            propsHaveChanged, propChanges = self.compareProps(oldElem, newElem, DOM)
            if propsHaveChanged:
                for key in propChanges["create"]:    #create and change props
                    # console.log(newElem["type"], key)
                    if key[0:2] == "on":
                        DOM.removeEventListener(key[2:], oldElem['props'][key])
                        newElem['props'][key] = create_proxy(newElem['props'][key])
                        DOM.addEventListener(key[2:], newElem['props'][key])
                        pass
                    elif hasattr(newElem['props'][key], "__call__"):
                        if key == "value":##
                            DOM.value=newElem['props'][key]()
                        else:
                            DOM.setAttribute(key, newElem['props'][key]())
                    else :
                        if key == "value":##
                            DOM.value=newElem['props'][key]
                        else:
                            DOM.setAttribute(key, newElem['props'][key])

                for key in propChanges["remove"]:
                    DOM.removeAttribute(key)

            # --------------------------------------------------

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

            if hasattr(newElem['children'], "__call__"): #allow arguments without calling function
                # assumes a function call returns a string
                for i in DOM.children:
                    DOM.removeChild(i)
                DOM.innerText = ""
                func_return_val=newElem['children']()
                if type(func_return_val) is str:
                    DOM.appendChild(document.createTextNode(func_return_val))
                else:
                    DOM.appendChild(self.createElement(func_return_val))
                return
                

            # --------------------------------------------------

            len_old = len(oldElem['children'])
            len_new = len(newElem['children'])

            if len_old == len_new:
                console.log('RENDER CASE : Same number of children')
                console.log(DOM.children,newElem['children'],oldElem['children'])
                for i in range(len_old):
                    oldEl = oldElem['children'][i]
                    newEl = newElem['children'][i]
                    # oldEl func, newEl func => None, pieElement, str
                    if self.isFunc(oldEl):
                        oldEl = oldEl()
                    if self.isFunc(newEl):
                        newEl = newEl()
                    # console.log(to_js(oldEl),to_js(newEl))
                    if oldEl == None: 
                        domEl = None
                    else:
                        domEl = DOM.children[i]

                    self.reconcile(DOM, domEl, oldEl, newEl)
                        
            else:     
                # old element has more number of children
                if len_old > len_new:
                    console.log('RENDER CASE : Old has more children')
                    # console.log(DOM.children,to_js(newElem['children']),to_js(oldElem['children']))

                    for i in range(len_new):
                        oldEl = oldElem['children'][i]
                        newEl = newElem['children'][i]
                        """
                        #oldEl func, newEl func => None, pieElement, str
                        if self.isFunc(oldEl):
                            oldEl = oldEl()
                        if self.isFunc(newEl):
                            newEl = newEl()
                        """
                        if oldEl == None: 
                            domEl = None
                        else:
                            domEl = DOM.children[i]
                        self.reconcile(DOM,domEl,oldEl,newEl)
                           
                    # remove the excess elements
                    for i in range(len_new,len_old):
                        DOM.removeChild(DOM.children[len_new])

                # new has more number of children
                else:
                    console.log('RENDER CASE : New has more children')
                    console.log(DOM.children,newElem['children'],oldElem['children'])
                    for i in range(len_old):
                        oldEl = oldElem['children'][i]
                        newEl = newElem['children'][i]
                        """
                        # oldEl func, newEl func => None, pieElement, str
                        if self.isFunc(oldEl):
                            oldEl = oldEl()
                        if self.isFunc(newEl):
                            newEl = newEl()
                        """
                        if oldEl == None: 
                            domEl = None
                        else:
                            domEl = DOM.children[i]
                        self.reconcile(DOM,domEl,oldEl,newEl)

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
        if type(tag) is str:
            return {'key':key,'type':tag,'props':props,'children':children}
        else:
            return tag(props)

    def createElement(self, element):
        """
        Function to create an actual DOM element from the virtual DOM element
        """

        el = document.createElement(element['type'])
        # console.log("creating", element["type"])

        if element['children'] or element["children"] == "":
            # child is a function
            if hasattr(element['children'], "__call__"):
                # assumes a function call returns a string
                func_return_val=element['children']()
                if type(func_return_val) is str:
                    el.appendChild(document.createTextNode(func_return_val))
                else:
                    el.appendChild(document.createElement(func_return_val))

            # child is a string
            elif type(element['children']) is str:
                el.appendChild(document.createTextNode(element['children']))

            # children are a list
            elif type(element['children']) is list:
                for i in element['children']:
                    if i == None:
                        continue
                    elif type(i) is str: 
                        el.appendChild(document.createTextNode(i))
                    elif self.isFunc(i):
                        func_return_val=i()
                        if type(func_return_val) is str:
                            el.appendChild(document.createTextNode(func_return_val))
                        else:
                            if func_return_val != None:
                                el.appendChild(self.createElement(func_return_val))
                    else:
                        el.appendChild(self.createElement(i))

        # if props exist
        if element['props']:
            for key in element['props'].keys():
                # event 
                if key[0:2] == "on":
                    element["props"][key] = create_proxy(element['props'][key])
                    el.addEventListener(key[2:], element['props'][key])
                # prop is a function
                elif hasattr(element['props'][key], "__call__"):
                    el.setAttribute(key, element['props'][key]())
                else:
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

