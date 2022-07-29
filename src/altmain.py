from json import dumps
from pprint import pp
from state import State
# from event_consts import CREATE,REMOVE,REPLACE,UPDATE
from datetime import datetime
# from sys import _getframe as getframe
from hashlib import blake2b
from uuid import uuid4 as uuid
from component import Component
from typing import Union

'''
TODO:
- Have to add component/component name to DOM as property/attribute
- Have to add link to DOM node as part of the component object/comoponent store
- Mounting, updating and unmounting of components need to be linked to object creation, re-creation/update and removal
- Differentiate between different instances of same component
'''

"""
if 
App
    div
        p
        div
        Comp
            p
        Comp
            p

App
    return h(div, [
        h(p),
        h(div),
        h(Comp, {}, p),
        h(Comp, {}, p),
    ])

Initial Render
    - Call rpe on App
    - check currentRenderngComp = None
    - create random instance id
    - create new Component for App
    - save it in compStore
    - return it
    - reconcile(App, oldVDOM=None, newVDOM=None, dom=root)

Reconcile
- check if App is component or element => component
- check props
- set currentRenderingComp = App
- createFragment of App
    - newVDOMFrag = App(props)
        - create div => return dict
            - create p => return dict
            - create div => return dict
            - create Comp => return new Component(Comp) => instanceId = randomId => save in compStore
            - create Comp => return new Component(Comp) => instanceId = randomId => save in compStore

- reconcile(App, None, None, dom)
    - comp or element => element
    - check tag => store changes
    - check props => store changes

    - if component:
        - oldVDOMFrag = newVDOMFrag
        - createFragment
            - newVDOMFrag = App(props)
                - create div => return dict
                    - create p => return dict
                    - create div => return dict
                    - *NEW Instance* create Comp => return new Component(Comp) => instanceId = randomId => save in compStore
                    - *NEW Instance* create Comp => return new Component(Comp) => instanceId = randomId => save in compStore

    - children
        - reconcile(App, p, p, dom)
        - reconcile(App, div, div, dom)
        - reconcile(App, Comp, Comp, dom)
            - comp or element => comp
            - currentOldVDOMComp = Comp | old
            - currentRenderingComp = Comp | new => instanceId
            - createFragment in new Comp
                => tag(props)
                    => useState => currentRenderingComp.store[stateIdentifier] = currentOldVDOMComp.store[stateIdentifier]
                    => useState => currentRenderingComp.store[stateIdentifier] = currentOldVDOMComp.store[stateIdentifier]
                    => useState => currentRenderingComp.store[stateIdentifier] = currentOldVDOMComp.store[stateIdentifier]
                - create p
            - check tag => store changes
            - check props => store changes
            - children
                - reconcile(Comp, p, p, dom)
                    - comp or element => element
                    - check tag => store changes
                    - check props => store changes
            - compState[currentOldVDOMComp] = Comp | new
"""

class Pie():
    def __init__(self):
        # stores the element to be rendered into the root element
        self.renderElement = None 

        # stores root DOM element
        self.root = None    

        self.top=-1
        self.reconcilationStack = []

        # global store of States
        self.store = {}

        # global dictionary of effects
        # PROTOTYPE: {"Component1":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":()},.....},"stage":"Mounted"},........}
        self.effects={}

        self.VDOM_currentComponent = None

        self.mutations = {
            'CREATE':[],
            'UPDATE':[], # types are same, update occurs
            'REPLACE':[], # types are different
            'REMOVE':[]
        }

        # TODO : Remove clear of console
        # clear the pyscript logs
        # console.clear()

    def dispatchReconcile(self, component:Component, renderState):
        if renderState == "INITIAL":
            start = datetime.now()
            self.reconcile(None, component, None)
            end = datetime.now()
        else:
            start = datetime.now()
            newComponent = self.createPieElement(component.key, component.func, component.props, None)
            self.reconcile(component, newComponent, component.DOMRef)
            end = datetime.now()

        print('RECONCILATION TOOK : ', (str(end-start)))

        self.commitMutations()


    def isString(self, element):
        return type(element) is str

    def createPieElement(self, key, tag, props, children):
        '''
        Function to create vdom element
        '''
        if type(tag) is str:
            hash_el = {
                'key':key,
                'type':tag,
                'props': [props[k].__name__ if self.isFunc(props[k]) else props[k] for k in props] if props else None,
            }
            return {
                'hashed_key' : blake2b(dumps(hash_el).encode()).hexdigest(), 
                'hashed_children' : blake2b(children.encode()).hexdigest() if type(children) is str else None, 
                **hash_el,
                'props': props,
                'children': children
            }
        else:   # If tag is a Component
            if children != None:
                raise Exception('Components cannot have children')
            
            return {'key':key,'tag':tag,'props':props,'children':children}
            
    def pop(self):
        if (self.top) > 0:
            self.top-=1
            return self.reconcilationStack.pop()
        else:
            return None
    
    def push(self, comp):
        self.reconcilationStack.insert(self.top, comp)
        self.top+=1
        
    def peek(self):
        return self.reconcilationStack[self.top] if self.top >= 0 else None

    def appendMutation(self):
        pass
    
    def reconcile(self, oldVEle, newVEle, parentDom, domEle):
        """
        Cases:
               OldVDOM, NewVDOM
            1) None, None
            2) None, Element
            3) None, Component
            4) None, str
            5) Element, None
            6) str, None
            7) Component, None
            8) str, str
            9) str, element
            10) str, Component
            11) element, element
            12) element, str
            13) element, Component
            14) Component, Component
            15) Component, element
            16) Component, str
        """
        pass
        
    def reconcileChildren(self, oldChildren, newChildren):
        pass

    def commitMutations():
        pass
    
    def render(self, renderElement, props, rootDom):
        # renderElement is a function
        self.renderElement = renderElement
        # root is the root div container
        self.root = rootDom
        self.VDOM_currentComponent=self.createPieElement(None, renderElement, props, None)
        self.dispatchReconcile(self.VDOM_currentComponent, "INITIAL")
