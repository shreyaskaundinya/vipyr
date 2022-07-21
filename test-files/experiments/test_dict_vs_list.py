from datetime import datetime

def test():
    d = {}
    l = []

    for i in range(0,10000):
        d[i] = i

    for i in range(0, 10000):
        l.append({'key': i, 'children': i})

    start = datetime.now()
    
    for i in range(0, 10000):
        x = d.keys()
    
    end = datetime.now()
    print('dict keys took : ', end-start)


    start = datetime.now()
    
    for i in range(0, 10000):
        x = [i['key'] for i in l]
    
    end = datetime.now()
    print('list compre took : ', end-start)

test()
