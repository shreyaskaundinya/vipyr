from json import dumps
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
        
        # global store of Components
        '''
        Add key the user gives as value to instanceId key in instance dictionary
        PROTOTYPE:
        {
            "123..": {"object":Component123...,effects":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":(),"states":{"State1":state_var1,"State2":stae_var1}},...},
            "987..": {"object":Component987...,effects":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":(),"states":{"State1":state_var1,"State2":stae_var1}},...},
            ...
        }
        '''
        self.compStore = {}

        self.top=-1
        self.reconcilationStack = []

        # global store of States
        self.store = {}

        # global dictionary of effects
        # PROTOTYPE: {"Component1":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":()},.....},"stage":"Mounted"},........}
        self.effects={}

        self.VDOM_currentComponent = None

        # TODO : Remove clear of console
        # clear the pyscript logs
        # console.clear()

    def dispatchReconcile(self, component:Component):
        if self.isInitialRender:
            start = datetime.now()
            self.reconcile(None, component, self.root)
            end = datetime.now()
        else:
            start = datetime.now()
            newComponent = self.createPieElement(component.key, component.func, component.props, None)
            self.reconcile(component, newComponent, component.DOMRef)
            end = datetime.now()

        print('RECONCILATION TOOK : ', (str(end-start)))

    def construct(self, func, key, props):   # PROTOTYPE tag-function callback, key-string, props-dictionary
        instanceId = uuid() # type(instanceId) is <class 'uuid.UUID'>
        return Component(func,key,props,instanceId)

    def storeInstance(self,instance):
        self.compStore[instance.instanceId]['object']=instance

    def deleteInstance(self, instanceId):
        del self.compStore[instanceId]

    '''
        Way to avoid having seperate attributes in compStore:
        temp=component.VDOMFrag
        component.VODMFrag=component.createFragment()
    '''
    def isComponentInstance(element):
        if type(element) is Component:
            return True
        return False

    def createPieElement(self, key, tag, props, children):
        '''
        Function to create vdom element
        '''
        if type(tag) is str:
            # TODO : Fix the function part [maybe use func ref number instead of name]
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
            '''
            # Creation of instanceId
            # HACK Have to change stack frame index if below code is wrapped inside a function
            frameObj=getframe(1)
            byteInstr=frameObj.f_lasti    # Byte code instruction number
            parentName=frameObj.f_code.co_name  # Name of the component which is calling RPE(parent component)
            tagStr=tag.__name__
            '''
            
            if children != None:
                raise Exception('Components cannot have children')
            
            obj=self.construct(tag,key,props)
            self.storeInstance(obj)
            return obj

        # Key can be used to differentiate between instances
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

    def reconcile(self, oldVdomElement: Union[Component, dict, str, None], newVdomElement: Union[Component, dict, str, None], domElement):
        """
        if component
            - if old vdom and new vdom are none
                - construct and reconcile
            - else
                - push to stack
                
            
        """

        if self.isComponentInstance(oldVdomElement):
            pass

    
    def render(self, renderElement, props, rootDom):
        # renderElement is a function
        self.renderElement = renderElement
        # root is the root div container
        self.root = rootDom
        self.VDOM_currentComponent=self.createPieElement(None, renderElement, props, None)

        self.dispatchReconcile(self.VDOM_currentComponent)
    
