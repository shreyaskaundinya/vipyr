def get_content(filename: str):
    try:
        f = open(filename, "r")
        r = f.read()
        f.close()
        return r
    except:
        raise Exception("Error loading file")

def get_lines(filename: str):
    try:
        f = open(filename, "r")
        l = f.readlines()
        f.close()
        return l
    except:
        raise Exception("Error loading file")

def recursive_bundler(source, entry, exclude):
    r = get_lines(entry)
    r.insert(0, "\n")
    
    for i in range(len(r)):
        s = r[i].split()
        if len(s) < 1:
            continue

        if s[0] == "import":
            if s[1] in exclude:
                continue
            counter = i
            r.remove(r[i])
            for line in recursive_bundler(source, source+s[1]+".py", exclude):
                r.insert(counter, line)
                counter+=1
            
        if s[0] == "from":
            if s[1] in exclude:
                continue
            counter = i
            r.remove(r[i])
            for line in recursive_bundler(source, source+s[1]+".py", exclude):
                r.insert(counter, line)
                counter+=1
    
    r.append("\n")

    return r