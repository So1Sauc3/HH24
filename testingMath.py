def fancyMixed(input_string):
    try:
        parts = input_string.split(" ")
        print(parts)
        if len(parts) == 1: return input_string
        frac = []
        for p in parts:
            if p.find('/')!=-1:
                frac = p.split('/')
                return float(parts[0]) + float(frac[0])/float(frac[1])
        return float(parts[0]) + float(parts[1])
    except: return input_string

print(fancyMixed('1 2/4'))