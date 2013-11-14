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
    return newPatterns

def yn2dec(binState):
    """Converts a binary string into a decimal number."""
    bit= 0
    output=0
    for m in binState:
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
    
def mapPrefVec2PayoffVec(prefVec):
    """Map the preference vectors provided into payoff values for each state."""
    for dmi,dm in enumerate(self.decisionMakers):
        for state in dm.preferenceVector:
            if state not in self.feasibles.decimal:
                try:
                    for subSt in state:
                        if subSt not in self.feasDec:
                            raise Exception('State %s (occuring in preference vector for dm %s) is not a feasible state'%(subSt,dmi))
                except TypeError:
                    raise Exception('State %s (occuring in preference vector for dm %s) is not a feasible state'%(state,dmi))

    self.payoffs =[[0]*(2**self.numOpts()) for x in range(self.numDMs())]   

    for dm in range(self.numDMs()):
        for x,y in enumerate(self.prefVec[dm]):
            try:
                for z in y:
                    self.payoffs[dm][z] = self.numFeas - x
            except TypeError:
                self.payoffs[dm][y] = self.numFeas - x

        for state in self.feasDec:
            if self.payoffs[dm][state] == 0:
                raise Exception("feasible state '%s' for DM '%s' was not included in the preference vector" %(state,dm))

def rankStates(dm):
    """Ranks the states for a DM, generating payoff values.
    
    Ranking is based on Preference Prioritization, and output payoff values
    are sequential. Calculated payoffs are stored in self.payoffs[dmIdx]
    """
    self.payoffs[dmIdx] = [0]*(2**self.numOpts())
    pVal=len(self.prefPri[dmIdx])-1
    for Pstatement in self.prefPri[dmIdx]:
        for state in self.feasDec:
            if self.matchesCrit(state,Pstatement):
                self.payoffs[dmIdx][state] += 2**pVal
        pVal-=1

    uniquePayoffs = sorted(set(self.payoffs[dmIdx]))

    pVec = []
    pVecOrd = []

    for i,x in enumerate(uniquePayoffs):
        stateSet = [idx for idx,pay in enumerate(self.payoffs[dmIdx]) if pay==x]
        stateOrd = [self.ordered[idx] for idx,pay in enumerate(self.payoffs[dmIdx]) if (pay==x) and (idx in self.feasDec)]
        pVec.append(stateSet)
        pVecOrd.append(stateOrd)

    pVec.reverse()
    pVecOrd.reverse()
    for i,x in enumerate(pVecOrd):
        if len(x)==1:
            pVecOrd[i]=x[0]
    for i,x in enumerate(pVec):
        if len(x)==1:
            pVec[i]=x[0]
    self.prefVec[dmIdx] = pVec
    self.prefVecOrd[dmIdx] = pVecOrd