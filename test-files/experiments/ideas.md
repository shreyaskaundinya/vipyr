# Ideas

```python

def Component(props):
    [value, setValue] = rpy.useState(initialValue)
    [value, setValue] = rpy.useState(initialValue)

    def effectFunc():
        return {}

    rpy.useEffect(
        effectFunc,
        [deps]
    )

    return rpy.createPieElement(
        "div",
        ...,
        [
            rpy.createPieElement(
                "p",
                ...,
                "hello world"
            )
        ]
    )
```

```json
{
    tag:App,
    ...,
    children:
    {
        {
            tag:div
            props:.....,
            children:{
                {
                    tag:'p',
                    props:....
                }:1,
                {   tag:'List',
                    props:....,
                }:0,
                {
                    tag:'p',
                    props:....
                }:3,
                {
                    tag:'p',
                    props:....
                }:4,
                {
                    tag:'p',
                    props:....
                }:2,
                ....
            }
        }:0,
        ....
    }
}

```

---

## Things to remember :

-   currentComponent
-   renderQueue
-   be able to differentiate instances of the same component.
-   old and new VDOM
-   partial rerender
-   how to implement batch updates?

## Component struct

Note :

    - parentDom : for Fragment element types or Array/map/filter returns cuz those dont have "dom" property

```

{
    type: function | str,
    # component: Component | None,
    key: immutable type | None,
    props: dict | None,
    children: list | (str | int | bool) | None,
    frag: dict,
    hooks: hooks class,
    dom,
    parentDom,
    isDirty: boolean,
}

<div>
    <Comp val="hello"/>
    <Comp val="world"/>
</div>

<div>
    <Comp val="world"/>
</div>

c = Comp | hello
newVNode.comp = Comp | hello
```

## Hooks struct

-   currentIndex => used to append the hooks into the list
-   list of all hooks in a component
-   effects are queue of functions to be run => use effect func, cleanup
    -   call old cleanups
    -   call new effects, cleanups

### Supported HookTypes:

1. useState
2. useEffect

```
{
    component: Comp,
    list: [
        {},
        {}
    ],
    effects: [

    ]
}

```

### state hook struct

```
calls component.setState to perform partial rerender?
    - use self from component to push to renderQueue?
{
    type: HookType,
    state: [
        initialValue,
        value,
        setValue: function
    ]
}

NOTE : if we implement shouldComponentUpdate lifecycle method
    => we need to have a nextState
    => call the shouldComponentUpdate func and then update if it returns true
```

### effect hook struct

```
depsChanged(oldDeps, newDeps)

{
    type: HookType,
    deps: [],
    cleanup: function,
    effect: function
}
```
