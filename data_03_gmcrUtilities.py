bitFlip = {'0':'1','1':'0',
           'N':'Y','Y':'N'}

toYN = {'0':'N','1':'Y','-':'-'}
fromYN = {'N':'0','n':'0','Y':'1','y':'1','-':'-'}

def reducePatterns(patterns):
    """Reduce patterns into compact dash notation. Effectively a partial
    implementation of the Quine-McCluskey Algorithm."""
    newPatterns = []
    matched = []
    for x,p1 in enumerate(patterns):
        if x in matched: continue
        for y,p2 in enumerate(patterns[x+1:],1):
            if x+y in matched: continue
            diffs=0
            for idx,bit in enumerate(zip(p1,p2)):
                if bit[0] != bit [1]:
                    diffs += 1
                    dbit  = idx
                if diffs >1:break
            if diffs ==1:
                newPatterns.append(p1[:dbit]+'-'+p1[dbit+1:])
                matched+=[x,x+y]
                break
        if x not in matched: newPatterns.append(p1)
    if matched:
        newPatterns = reducePatterns(newPatterns)
    return newPatterns

def expandPatterns(patterns):
    """Expands patterns so that they contain no dashes"""
    newPatterns = []
    for pat in patterns:
        if '-' in pat:
            adding = [pat.replace('-','1',1),pat.replace('-','0',1)]
            newPatterns += expandPatterns(adding)
        else:
            newPatterns += [pat]
    return newPatterns

def bin2dec(binState):
    """Converts a binary string into a decimal number."""
    bit= 0
    output=0
    for m in binState:
        if m=='1':
            output += 2**bit
        bit+=1
    return output

def dec2bin(decState,numOpts):
    """converts a decimal number into a binary string of appropriate length."""
    output = bin(decState).lstrip("0b").zfill(numOpts)[::-1]
    return output

def _toIndex(stateList):
    """Translates a binary pattern from dash notation to index notation"""
    out = []
    for x in range(len(stateList)):
        if stateList[x] != '-':
            out.append((x,stateList[x]))
    return out

def _fromIndex(idxList,numOpts):
    """Translates a binary pattern form index notation to dash notation"""
    out = ['-']*numOpts
    for x in idxList:
        out[x[0]]=x[1]
    return ''.join(out)

def _subtractPattern(feas,sub):
    """Remove infeasible state pattern 'sub' from feasible list 'feas' """
    sub = [x for x in enumerate(sub) if x[1] != '-']
    #check if targ overlaps with state:
    for x in sub:
        idx,val = x
        if feas[idx] == bitFlip[val]:
            return [feas]
    #subtract overlap if it exists
    remainingStates = []
    curr = feas
    for x in sub:
        idx,val = x
        if curr[idx] == '-':
            remainingStates.append(curr[:idx]+bitFlip[val]+curr[idx+1:])
            curr = curr[:idx]+val+curr[idx+1:]
    return remainingStates

def rmvSt(feas,infeas):
    """Subtract states 'infeas' from states 'currFeas'. """
    orig = sum([2**x.count('-') for x in feas])
    newfeas = []
    for pattern in feas:
        newfeas += _subtractPattern(pattern,infeas)
    feas = newfeas
    numRmvd = orig - sum([2**x.count('-') for x in feas])
    return feas,numRmvd

def mutuallyExclusive(mutEx):
    """Given a list of mutually exclusive options, returns the equivalent set of infeasible states"""
    states = _toIndex(mutEx)
    toRemove = itertools.combinations(states,2)
    remove = [_fromIndex(x) for x in toRemove]
    return remove

def orderedNumbers(decimalList):
    """creates translation dictionaries for using ordered numbers.
    
    Generates the decimal->ordered and ordered->decimal translation
    dictionaries for a list of decimal values.
    """
    ordered  = {}        #decimal -> ordered dictionary
    expanded = {}        #ordered -> decimal dictionary
    for i,x in enumerate(decimalList,1):
        ordered[x]=i
        expanded[i]=x
    return ordered,expanded