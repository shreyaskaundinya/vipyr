from json import dumps
from js import document, console
from pyodide import create_proxy, to_js
from state import State
# from event_consts import CREATE,REMOVE,REPLACE,UPDATE
from datetime import datetime
from sys import _getframe as getframe
from hashlib import blake2b
from component import Component

'''
TODO:
- Have to add component/component name to DOM as property/attribute
- Have to add link to DOM node as part of the component object/comoponent store
- Mounting, updating and unmounting of components need to be linked to object creation, re-creation/update and removal
- Differentiate between different instances of same component
'''

class Pie():
    def __init__(self):
        self.currVDOM = None 
        self.prevVDOM = None
        
        # stores the element to be rendered into the root element
        self.renderElement = None 

        # stores root DOM element
        self.root = None    
        
        # global store of Components
        '''
        Add key the user gives as value to instanceId key in instance dictionary
        PROTOTYPE:
        {"Component": 
            {
                "123..": {"object":Component123...,effects":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":(),"states":{"State1":state_var1,"State2":stae_var1}},...},
                "987..": {"object":Component987...,effects":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":(),"states":{"State1":state_var1,"State2":stae_var1}},...},
                ...
            },
            ...
        }
        '''
        self.compStore = {}

        # global store of States
        self.store = {}

        # global dictionary of effects
        # PROTOTYPE: {"Component1":{"Effect1":{"old_dep":None,"new_dep":None,"effect":(),"cleanup":()},.....},"stage":"Mounted"},........}
        self.effects={}

        self.VDOM_currentComponent = None

        # TODO : Remove clear of console
        # clear the pyscript logs
        console.clear()

    def dispatchReconcile(self):
        start = datetime.now()

        # create new VDOM
        self.prevVDOM=self.currVDOM
        self.currVDOM=self.renderElement()
        
        end = datetime.now()
        console.log('CREATION OF VDOM TOOK: ', to_js(str(end-start)))

        # rerender whole tree
        #self.root.removeChild(self.root.firstElementChild)
        #self.root.appendChild(self.createElement(self.currVDOM))

        start = datetime.now()
        self.reconcile(None, self.root.firstChild, self.prevVDOM, self.currVDOM)
        end = datetime.now()
        console.log('RECONCILATION TOOK : ', to_js(str(end-start)))

    def isComponentInstance(self,element):
        if type(element) is Component:
            return True
        return False

    def construct(self, func, key, props):   # PROTOTYPE tag-function callback, key-string, props-dictionary
        instanceId = # FIXME syntax & import
        return Component(func,key,props,instanceId)

    def componentExists(self,tag):  # OPTIMIZE give an appropriate name
        if self.compStore.get(tag) is None:
            return False
        return True

    def instanceExists(self,tag,instanceId):
        if self.compStore[tag].get(instanceId) is None:
            return False
        return True

    def storeInstance(self,instance):
        self.compStore[instance.instanceId]['object']=instance

    def deleteInstance(self, instanceId):
        del self.compStore[instanceId]

    '''
        Way to avoid having seperate attributes in compStore:
        temp=component.VDOMFrag
        component.VODMFrag=component.createFragment()
    '''

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
                'component': self.VDOM_currentComponent
            }
            return {
                'hashed_key' : blake2b(dumps(hash_el).encode()).hexdigest(), 
                'hashed_children' : blake2b(children.encode()).hexdigest() if type(children) is str else None, 
                **hash_el, 
                'props': props,
                'children': children
            }
        else:   # If tag is a Component
            # Creation of instanceId
            # HACK Have to change stack frame index if below code is wrapped inside a function
            frameObj=getframe(1)
            byteInstr=frameObj.f_lasti    # Byte code instruction number
            parentName=frameObj.f_code.co_name  # Name of the component which is calling RPE(parent component)
            tagStr=tag.__name__
            

            if children != None:
                raise Exception('Components cannot have children')
            
            compExist=self.componentExists(tagStr)
            
            if compExist:
                if self.instanceExists(tagStr,instanceId): # FIXME How will the instanceId be given? -If tag is an object
                    return self.compStore[tagStr][instanceId]['object']

            obj=self.construct(tag,key,props)
            self.compStore[tagStr]=self.compStore[tagStr] if self.compExist else {}
            self.storeInstance(obj)
            return obj

        # Key can be used to differentiate between instances

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


    def reconcile(Component, dom):
        """
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
        print("hello")