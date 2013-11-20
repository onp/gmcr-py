import itertools

bitFlip = {'N':'Y','Y':'N'}

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
            adding = [pat.replace('-','Y',1),pat.replace('-','N',1)]
            newPatterns += expandPatterns(adding)
        else:
            newPatterns += [pat]
    return sorted(newPatterns)

def yn2dec(ynState):
    """Converts a binary YN string into a decimal number."""
    bit= 0
    output=0
    for m in ynState:
        if m=='Y':
            output += 2**bit
        bit+=1
    return output

def dec2yn(decState,numOpts):
    """converts a decimal number into a binary string of appropriate length."""
    output = bin(decState).lstrip("0b").zfill(numOpts)[::-1].replace('1','Y').replace('0','N')
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
    numRmvd = orig - sum([2**x.count('-') for x in newfeas])
    print(feas)
    print(newfeas)
    return newfeas,numRmvd

def mutuallyExclusive(mutEx):
    """Given a list of mutually exclusive options, returns the equivalent set of infeasible states"""
    return list(itertools.combinations(mutEx,2))

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
    
def validatePreferenceVector(prefVec,feasibles):
    """Check that the preference vector given is valid."""
    
    alreadySeen = []
    for state in prefVec:
        if state in feasibles.ordered:
            if state in alreadySeen:
                return "State %s cannot appear more than once."%(state)
            alreadySeen.append(state)
        else:
            try:
                for subSt in state:
                    if subSt in feasibles.ordered:
                        if subSt in alreadySeen:
                            return "State %s cannot appear more than once."%(subSt)
                        alreadySeen.append(subSt)
                    else:
                        return "State %s is not a feasible state."%(subSt)
            except TypeError:
                return "State %s is not a feasible state"%(state)
                
    for state in feasibles.ordered:
        if state not in alreadySeen:
            return "State %s is missing."%(state)
            
    return None
    
def mapPrefVec2Payoffs(preferenceVector,feasibles):
    """Map the preference vectors provided into payoff values for each state."""             
    payoffs =[0]*len(feasibles)     #Make a clean payoffs vector   

    #use position in preference vector to give a payoff value.
    for idx,state in enumerate(preferenceVector):
        try:
            for subState in state:
                payoffs[subState-1] = len(feasibles) - idx
        except TypeError:
            payoffs[state-1] = len(feasibles) - idx

    if 0 in payoffs:
        state = feasibles.ordered[payoffs.index(0)]
        raise Exception("Feasible state '%s' for DM was not included in the preference vector" %(state))
        
    return payoffs

def prefPriorities2payoffs(preferences,feasibles):
    """Ranks the states for a DM, generating payoff values.
    
    Ranking is based on Preference Prioritization, and output payoff values
    are sequential.
    """
    #generate initial payoffs
    payoffsRaw = [0]*len(feasibles)
    for preference in preferences:
        for state in feasibles.decimal:
            if preference.test(state):
                payoffsRaw[feasibles.toOrdered[state]-1] += preference.weight

    #reduce magnitude of payoffs - do not do this if weights had special meaning.
    uniquePayoffs = sorted(set(payoffsRaw))
    preferenceVector = []
    payoffs = list(payoffsRaw)  #creates a copy

    for idx,value in enumerate(uniquePayoffs):
        for jdx,pay in enumerate(payoffsRaw):
            if pay==value:
                payoffs[jdx] = idx+1
        stateSet = [idx+1 for idx,pay in enumerate(payoffsRaw) if pay==value]
        if len(stateSet) > 1:
            preferenceVector.append(stateSet)
        else:
            preferenceVector.append(stateSet[0])

    preferenceVector.reverse()      #necessary to put most preferred states at beginning instead of end
    
    return payoffs, preferenceVector