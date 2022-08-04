from json import dumps
from js import document, console
from pyodide import create_proxy, to_js
from pprint import pp   # OPTIMIZE Usage?
from state import State
# from event_consts import CREATE,REMOVE,REPLACE,UPDATE
from datetime import datetime
# from sys import _getframe as getframe
from hashlib import blake2b
from typing import Union
from sys import _getframe as getframe

'''
TODO:
- Have to add component/component name to DOM as property/attribute
- Have to add link to DOM node as part of the component object/comopostate
- Mounting, updating and unmounting of components need to be linked to object creation, re-creation/update and removal
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
    - check tastate changes
    - check propstate changes

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
                    => useState => currentRenderingstate[stateIdentifier] = currentOldVDOMstate[stateIdentifier]
                    => useState => currentRenderingstate[stateIdentifier] = currentOldVDOMstate[stateIdentifier]
                    => useState => currentRenderingstate[stateIdentifier] = currentOldVDOMstate[stateIdentifier]
                - create p
            - check tastate changes
            - check propstate changes
            - children
                - reconcile(Comp, p, p, dom)
                    - comp or element => element
                    - check tastate changes
                    - check propstate changes
            - compState[currentOldVDOMComp] = Comp | new
"""

class Pie():
    def __init__(self):
        # stores the element to be rendered into the root element
        self.renderElement = None 

        # stores root DOM element
        self.root = None    
        
        # glstate of Components
        '''
        PROTOTYPE:
        {
            "ID1": {"dict":Component123},
            "ID2": {"dict":Component987},
            ...
        }
        '''
        self.compStore = {}

        # global recycle bin
        self.recycleBin= {}

        # To implment batch updates
        # BUG updateQueue should be in state.py or altmain.py?
        self.updateQueue=[]

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

    def dispatchReconcile(self, component:dict):
        # Initial render
        if self.isInitialRender:
            start = datetime.now()
            self.reconcile(None, component, self.root)
            end = datetime.now()
        # Re-renders
        else:
            start = datetime.now()
            # OPTIMIZE Either send Component as new vdom and None as old vdom every time to reconcile(1 extra reconcile call but able to modularize code properly), or create and send old and new  of the Component
            newVDOMFrag = component()
            oldDOMRef,oldVDOMFrag=None,None if component['vdomFrag'] == None else component['vdomFrag']['domRef'],component['vdomFrag']
            component['vdomFrag']=newVDOMFrag

            self.VDOM_currentComponent=component    # The current component will be the component whose state has changed

            self.reconcile(oldVDOMFrag, newVDOMFrag, oldDOMRef)
            end = datetime.now()
        print('RECONCILATION TOOK : ', (str(end-start)))

    def storeInstance(self,dictComp,key):
        self.compStore[key]['dict']=dictComp

    def deleteInstance(self, key):
        del self.compStore[key]

    def createPieElement(self, key, tag, props, children):
        '''
        Function to create vdom element
        '''
        if type(tag) is str:    # If tag is a DOM element
            # TODO : Fix the function part [maybe use func ref number instead of name]
            hash_el = {
                'key':key,
                'type':tag,
                'props': [props[k].__name__ if self.isFunc(props[k]) else props[k] for k in props] if props else None,
                'componentID':self.VDOM_currentComponent['id']
            }
            return {
                'hashed_key' : blake2b(dumps(hash_el).encode()).hexdigest(), 
                'hashed_children' : blake2b(children.encode()).hexdigest() if type(children) is str else None,  # TODO Allow for dictionaries also 
                **hash_el,
                'props': props,
                'children': children,
                'domRef': None
            }
        else:   # If tag is a Component(callback)
            if children != None:
                raise Exception('Components cannot have children')

            parentFrame=getframe(1)
            filePath=parentFrame.f_code.co_filename
            line_no=parentFrame.f_lineno
            instr_code_no=parentFrame.f_lasti
            ID=tag.__name__+filePath+str(line_no)+str(instr_code_no)

            dictComp={'id':ID,'key':key,'type':tag,'props':props,'children':children,'vdomFrag':None,'isDirty':False,'state':{}}  # TODO Add other attributes

            self.storeInstance(dictComp,key)

            return dictComp

    # FIXME Adjust this in such a way that it can be called after all the changes have been stored
    def createElement(self,vdomNode:dict):  # Assumption: Entire VDOM exists when this is called
        element=vdomNode['vdomFrag'] if vdomNode['type'].isFunc() else vdomNode

        # Creation of DOM element
        el = document.createElement(element['type'])

        # Adding DOM element reference to the vdom element
        element['domRef']=el    # DOM elemets are Javascript objects
        
        # Adding componentID to DOM element
        el.classList.add(vdomNode['componentID'])
        
        if element['children'] or element['children'] == '':
            # Child is a function
            if hasattr(element['children'], '__call__'):
                # assumes a function call returns a string  FIXME What will happen if there are CPE calls or components as child/children?
                func_return_val=element['children']()
                if type(func_return_val) is str:
                    el.appendChild(document.createTextNode(func_return_val))
                else:
                    el.appendChild(document.createElement(func_return_val))

            # Child is a string
            elif type(element['children']) is str:
                el.appendChild(document.createTextNode(element['children']))

            # Children: list
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

        # If props exist
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

    def addCreateChange(self):
        pass
    
    def addUpdateChange(self):
        pass

    def addReplaceChange(self):
        pass
    
    def addRemoveChange(self):
        pass

    def useState(self,state,initialState=None):
        states=self.VDOM_currentComponent['state']    # Assumption: VDOM_currentComponent has been fixed
        try:
            return states[state]
        except:
            states[state] = State(initialState, self.dispatchReconcile)
            return states[state]

    def useEffect():
        pass

    def reconcile(self, oldVdomElement: Union[dict, str, None], newVdomElement: Union[dict, str, None], domElement):
        """
        if component
            - if old vdom and new vdom are none
                - construct and reconcile
            - else
                - push to stack
        """
        if oldVdomElement == None:
            if newVdomElement == None:
                return
            self.addCreateChange()
        pass

    def render(self, renderElement, props, rootDom):
        # renderElement is a function
        self.renderElement = renderElement
        # root is the root div container
        self.root = rootDom
        self.VDOM_currentComponent=self.createPieElement(None, renderElement, props, None)  # Returns a dictionary containing App

        self.dispatchReconcile(self.VDOM_currentComponent)
    
# TODO Using one generator and multiple iterators to maintain lifecycle of components
# TODO Using generators like constructors