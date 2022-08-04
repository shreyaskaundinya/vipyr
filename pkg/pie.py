from json import dumps
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

# from event_consts import CREATE,REMOVE,REPLACE,UPDATE
from datetime import datetime
from hashlib import blake2b
from sys import _getframe
from functools import cache

class Pie():
    def __init__(self):
        self.currVDOM = None 
        self.prevVDOM = None
        
        # stores the element to be rendered into the root element
        self.renderElement = None 

        # stores root DOM element
        self.root = None    
        
        # global store of states
        self.store = {}

        # global dictionary of effects
        # Prototype: {"Component1":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":()},.....},"stage":"Mounted"},........}
        self.effects={}

        self.VDOM_currentComponent = []
        self.depth = 0

        # TODO : Remove clear of console
        # clear the pyscript logs
        console.clear()

    def dispatchReconcile(self):
        start = datetime.now()

        # create new VDOM
        self.prevVDOM=self.currVDOM
        self.currVDOM=self.createPieElement(None, self.renderElement, {}, None)
        
        end = datetime.now()
        console.log('CREATION OF VDOM TOOK: ', to_js(str(end-start)))

        # rerender whole tree
        #self.root.removeChild(self.root.firstElementChild)
        #self.root.appendChild(self.createElement(self.currVDOM))

        start = datetime.now()
        self.reconcile(self.root, self.root.firstChild, self.prevVDOM, self.currVDOM)
        end = datetime.now()
        console.log('RECONCILATION TOOK : ', to_js(str(end-start)))
        
        '''
        TODO
        Get to know which component is updated, go through corresponding effects and see which ones need to be called.
        Also need to know which components get unmounted, and call cleanup accordingly
        '''

    def useState(self, key, initialState = None):
        '''
            Pseudo-Hook2
            Function to create state instance for a particular key
            or return an existing state for that key
        '''
        # if state already return it, else create the new state
        try:
            return self.store[key]
        except:
            self.store[key] = State(initialState, self.dispatchReconcile)
            return self.store[key]
            
    def useEffect(self, component, effect, dependency = None):
        '''
        Cases:
        1) Dependency is none: have to call effect during initial render(component mount-are both the same?) and every update, and cleanup during unmount
        2) Dependency is []: have to call effect during initial render and one update(dependency doesn't change), and cleanup during unmount
        3) Dependency is [....]: have to call effect during initial render and on updates where dependecies change, and cleanup during unmount
        Note: Cleanup is called before calling the effect once again, i.e, on every update
        - Mounting of a component occurs only once
        - Updation happens during state change
        - When does unmounting of a component occur?
        - How are the dependency values updated?
        - Every time we are re-creating VDOM useEffect will be called
        '''
        if effect == None:
            raise Exception("Error : Effect cannot be None")
        if component == None:
            raise Exception("Error : Component cannot be None")

        effect_name=effect.__name__
        # Component is getting mounted
        if self.effects.get(component) == None or self.effects[component].get(effect_name) == None:
            self.effects[component][effect_name]={'old_dep':dependency, 'new_dep': dependency, 'effect': effect, 'cleanup': None}
            self.effects[component]['stage']='mount'
        # Component is getting updated
        else:
            self.effects[component][effect_name]['old_dep']=self.effects[component][effect_name]['new_dep']
            self.effects[component][effect_name]['new_dep']=dependency
            self.effects[component]['stage']='update'
        return

    def isFunc(self, item):
        return hasattr(item, '__call__')

    def compareTag(self, oldElem, newElem):
        '''
            Function that compares the type of an old VDOM element and new VDOM element
        '''
        return (oldElem['type'] != newElem['type'])

    def compareProps(self, oldElem, newElem, DOM):
        '''
            Function to compare props and return those to be changed
            
            Cases :
                - Creating new prop
                - Changing value of existing prop
                - Removing a prop
        '''

        hasChanged = False
        changes = {
            'create': {},
            'remove': []
        }

        if oldElem['props'] == None and newElem['props']:
            changes['create'] = newElem['props']
            hasChanged = True
        
        elif newElem['props'] == None and oldElem['props']:
            changes['remove'] = oldElem['props'].keys()
            hasChanged= True

        elif newElem['props'] == None and oldElem['props'] == None:
            return False, changes
        else :
            # TODO : Try making the props diff faster
            # props in new not in old => create
            # props in old not in new => remove
            # props in old and new but changed => change

            # ITERATIVE APPROACH
            for newProp in newElem['props'].keys():
                # create
                if newProp not in oldElem['props']:
                    changes['create'][newProp] = newElem['props'][newProp]
                    hasChanged = True

                # changed
                elif (
                    (newElem['props'][newProp] != oldElem['props'][newProp]) 
                    ):
                    changes['create'][newProp] = newElem['props'][newProp]
                    hasChanged = True
                    # del oldElem['props'][newProp]

            for oldProp in oldElem['props'].keys():
                # remove
                if oldProp not in newElem['props']:
                    changes['remove'].append(oldProp)
                    hasChanged = True
    
        return hasChanged, changes
    def compareKeys(self,oldElem,newElem):
        """"
        
        
        """

    def reconcile(self, parentDOM, DOM, oldElem = None, newElem = None):
        if oldElem == None and newElem == None: 
            # needed to end reconciliation
            # console.log('RENDER CASE : oldElem none, newElem none')
            return
        
        if oldElem == None:
            # create
            # console.log('RENDER CASE : oldElem none, newElem exists')
            parentDOM.appendChild(self.createElement(newElem))
            return

        if newElem == None:
            # remove
            # console.log('RENDER CASE : oldElem exists, newElem none')
            parentDOM.removeChild(DOM)
            return

        '''
        Cases : 
            1. new is str, old is str
            2. new is str, old is element
            3. new is element, old is str
            4. new is element, old is element
        '''
        # text node handling
        if type(newElem) is str:
            if oldElem != newElem:
                '''
                if DOM != None or oldElem != '':
                    parentDOM.removeChild(DOM)
                '''
                parentDOM.removeChild(DOM)
                parentDOM.appendChild(document.createTextNode(newElem))
            return
        
        elif type(oldElem) is str:
            parentDOM.removeChild(DOM)
            parentDOM.appendChild(document.createElement(newElem))
            return
        
        # --------------------------------------------------
        if oldElem['hashed_key'] != newElem['hashed_key']:
            # if two tags are different, rerender the whole subtree
            if self.compareTag(oldElem, newElem):
                # replace the current child in place
                # console.log('RENDER CASE : Tags are different')
                parentDOM.replaceChild(self.createElement(newElem), DOM)
                return

            else:
                # if props are different, make necessary changes to the DOM node
                propsHaveChanged, propChanges = self.compareProps(oldElem, newElem, DOM)
                if propsHaveChanged:
                    for key in propChanges['create']:    # create and change props
                        # handle event listeners
                        if key[0:2] == 'on':
                            # remove previous listener
                            DOM.removeEventListener(key[2:], oldElem['props'][key])
                            # create proxy of event handler
                            newElem['props'][key] = create_proxy(newElem['props'][key])
                            # add new event listener
                            DOM.addEventListener(key[2:], newElem['props'][key])

                        # if the value of a prop is a func, call it
                        elif hasattr(newElem['props'][key], '__call__'):
                            if key == 'value':##
                                DOM.value=newElem['props'][key]()
                            else:
                                DOM.setAttribute(key, newElem['props'][key]())
                        else :
                            # TODO : Find more cases that need to be isolated
                            if key == 'value':
                                DOM.value=newElem['props'][key]
                            else:
                                DOM.setAttribute(key, newElem['props'][key])

                    for key in propChanges['remove']:
                        DOM.removeAttribute(key)
        
        '''
        --- CHILDREN ------------------------------------------------------------

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
        '''

        if newElem['children'] == None:
            # remove all
            for child in DOM.children:
                DOM.removeChild(child)
            return
        
        if oldElem['children'] == None:
            # append all
            for child in newElem['children']:
                if type(child) is str:
                    DOM.appendChild(document.createTextNode(child))
                DOM.appendChild(self.createElement(child))
            return
        
        if type(oldElem['children']) is str or type(newElem['children']) is str:
            if (oldElem['hashed_children'] != newElem['hashed_children']):
                self.reconcile(DOM, DOM.firstChild, oldElem['children'], newElem['children'])
            return

        if hasattr(newElem['children'], '__call__'): 
            # allow arguments without calling function
            # assumes a function call returns a string
            for i in DOM.children:
                DOM.removeChild(i)
            DOM.innerText = ''
            func_return_val = newElem['children']()
            if type(func_return_val) is str:
                DOM.appendChild(document.createTextNode(func_return_val))
            else:
                DOM.appendChild(self.createElement(func_return_val))
            return
            

        # --------------------------------------------------
        # TODO : Try hashing leaf nodes [children => str, None] with the children to avoid recalling reconcile

        len_old = len(oldElem['children'])
        len_new = len(newElem['children'])

        len_min = len_old if len_old <= len_new else len_new

        for i in range(len_min):
            oldEl = oldElem['children'][i]
            newEl = newElem['children'][i]
            '''
            # oldEl func, newEl func => None, pieElement, str
            if self.isFunc(oldEl):
                oldEl = oldEl()
            if self.isFunc(newEl):
                newEl = newEl()
            '''
            if oldEl == None: 
                domEl = None
                self.reconcile(DOM, domEl, oldEl, newEl)
                continue
            else:
                domEl = DOM.children[i]

            if newEl == None:
                self.reconcile(DOM, domEl, oldEl, newEl)
            elif type(oldEl['children']) is str or type(newEl['children']) is str:
                if (oldEl['hashed_children'] != newEl['hashed_children']) or (oldEl['hashed_key'] != newEl['hashed_key']):
                    self.reconcile(DOM, domEl, oldEl, newEl)
            else: 
                self.reconcile(DOM, domEl, oldEl, newEl)

        # Old VDOM Element has more number of children
        if len_old > len_new:
            # console.log('RENDER CASE : Old has more children')
            # remove the excess elements
            for i in range(len_new, len_old):
                DOM.removeChild(DOM.children[len_new])

        # New VDOM Element has more number of children
        else:
            # console.log('RENDER CASE : New has more children')
            # add new elements
            for i in range(len_old,len_new):
                if type(newElem['children'][i]) is str:
                    DOM.appendChild(document.createTextNode(newElem['children'][i]))
                else:
                    DOM.appendChild(self.createElement(newElem['children'][i]))

    def constructComponent(self, key, tag, props):
        
        # self.VDOM_currentComponent = blake2b(ID.encode()).hexdigest()

        pass
    
    # @cache
    def createPieElement(self, key, tag, props, children):
        '''
        Function to create vdom element
        '''
        if type(tag) is str:
            # TODO : Fix the function part [maybe use func ref number instead of name]
            newProps = props if props else {"class": ""}

            newProps["class"] = ""
            
            # curr = self.VDOM_currentComponent[-1]
            
            # if curr[1] == 0:
            #     console.log(tag, to_js(curr))

            # curr[1] += 1

            hash_el = {
                'key':key,
                'type':tag,
                'props': [newProps[k].__name__ if self.isFunc(newProps[k]) else newProps[k] for k in newProps] if newProps else None,
                'component': self.VDOM_currentComponent
            }
            
            return {
                'hashed_key' : blake2b(dumps(hash_el).encode()).hexdigest(),
                'hashed_children' : blake2b(children.encode()).hexdigest() if type(children) is str else None, 
                **hash_el, 
                'props': newProps, 
                'children': children
            }
        else:
            frame1 = _getframe(1)
            line_no1 = frame1.f_lasti
            name1 = frame1.f_code
            newProps = props if props else {"class": ""}
            ID = blake2b((str(name1)+str(line_no1)+str(key)).encode()).hexdigest()
            newProps["class"] =  ID
            self.VDOM_currentComponent.append([tag.__name__, 0])
            x = tag(newProps)
            self.VDOM_currentComponent.pop()
            return x

    def createElement(self, element):
        '''
        Function to create an actual DOM element from the virtual DOM element
        '''
        el = document.createElement(element['type'])

        if element['children'] or element['children'] == '':
            # child is a function
            if hasattr(element['children'], '__call__'):
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
                if key[0:2] == 'on':
                    element['props'][key] = create_proxy(element['props'][key])
                    el.addEventListener(key[2:], element['props'][key])
                # prop is a function
                elif hasattr(element['props'][key], '__call__'):
                    el.setAttribute(key, element['props'][key]())
                else:
                    el.setAttribute(key, element['props'][key])

        return el


    def render(self, element, root):
        '''
        Function to handle the render
        '''
        self.renderElement = element
        self.root = root

        #self.currVDOM = self.renderElement()
        #root.appendChild(self.createElement(self.currVDOM))
        
        self.dispatchReconcile()
        # self.root.appendChild(self.createElement(self.renderElement()))

