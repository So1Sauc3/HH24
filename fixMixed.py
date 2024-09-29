def fixMixed(input_string):
    try:
        st = input_string
        if input_string.find('-') != -1: st=st.split('-')[1].strip()
        print(st)
        parts = st.split(" ")
        if len(parts) == 1:
            if parts[0].find('/') == -1: return input_string
            else: return float(parts[0].split('/')[0]) / float(parts[0].split('/')[1])
        frac = []
        for p in parts:
            if p.find('/')!=-1:
                frac = p.split('/')
                return float(parts[0]) + float(frac[0])/float(frac[1])
        return float(parts[0]) + float(parts[1])
    except: return 1

print(fixMixed("0.5 - 3 0.5"))