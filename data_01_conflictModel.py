# class to hold all information about the current state of the game,
# and serve it up to the UI elements and calculators.

import pickle as pkl
import itertools

class GMCRcalc:
    """A parent class to contain all of the necessary calculation methods"""

    bitFlip = {'0':'1','1':'0',
               'N':'Y','Y':'N'}

    toYN = {'0':'N','1':'Y','-':'-'}
    fromYN = {'N':'0','n':'0','Y':'1','y':'1','-':'-'}

    def reducePatterns(self,patterns):
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
            newPatterns = self.reducePatterns(newPatterns)
        return newPatterns

    def expandPatterns(self,patterns):
        """Expands patterns so that they contain no dashes"""
        newPatterns = []
        for pat in patterns:
            if '-' in pat:
                adding = [pat.replace('-','1',1),pat.replace('-','0',1)]
                newPatterns += self.expandPatterns(adding)
            else:
                newPatterns += [pat]
        return newPatterns

    def bin2dec(self,binState):
        """Converts a binary string into a decimal number."""
        bit= 0
        output=0
        for m in binState:
            if m=='1':
                output += 2**bit
            bit+=1
        return output

    def dec2bin(self,decState):
        """converts a decimal number into a binary string of appropriate length."""
        output = bin(decState).lstrip("0b").zfill(self.numOpts())[::-1]
        return output

    def _toIndex(self,stateList):
        """Translates a binary pattern from dash notation to index notation"""
        out = []
        for x in range(len(stateList)):
            if stateList[x] != '-':
                out.append((x,stateList[x]))
        return out

    def _fromIndex(self,idxList):
        """Translates a binary pattern form index notation to dash notation"""
        out = ['-']*self.numOpts()
        for x in idxList:
            out[x[0]]=x[1]
        return ''.join(out)

    def _subtractPattern(self,feas,sub):
        """Remove infeasible state pattern 'sub' from feasible list 'feas' """
        sub = [x for x in enumerate(sub) if x[1] != '-']
        #check if targ overlaps with state:
        for x in sub:
            idx,val = x
            if feas[idx] == self.bitFlip[val]:
                return [feas]
        #subtract overlap if it exists
        remainingStates = []
        curr = feas
        for x in sub:
            idx,val = x
            if curr[idx] == '-':
                remainingStates.append(curr[:idx]+self.bitFlip[val]+curr[idx+1:])
                curr = curr[:idx]+val+curr[idx+1:]
        return remainingStates

    def rmvSt(self,feas,infeas):
        """Subtract states 'infeas' from states 'currFeas'. """
        orig = sum([2**x.count('-') for x in feas])
        newfeas = []
        for pattern in feas:
            newfeas += self._subtractPattern(pattern,infeas)
        feas = newfeas
        numRmvd = orig - sum([2**x.count('-') for x in feas])
        return feas,numRmvd

    def mutuallyExclusive(self,mutEx):
  """Given a list of mutually exclusive options, returns the equivalent set of infeasible states"""
        states = self._toIndex(mutEx)
        toRemove = itertools.combinations(states,2)
        remove = [self._fromIndex(x) for x in toRemove]
        return remove

    def orderedNumbers(self,decimalList):
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


class ConflictModel(GMCRcalc):
    def __init__(self,file=None):
        """Initializes a new, empty game.  If 'file' is given, loads values from 'file'"""
        self.dmList = []        #stored as Strings

        self.optList = []     #stored as lists of Strings

        self.infeas  = []       #stored as dash patterns
        self.feasDec = []       #stored as decimal values
        self.feasDash= []       #stored as dash patterns
        self.ordered = {}        #decimal -> ordered dictionary
        self.expanded = {}      #ordered -> decimal dictionary
        self.numFeas = 0        #number of feasible states, integer

        self.irrev = []       #stored as (idx,'val') tuples

        self.prefVec = []    
        self.prefVecOrd = []

        self.prefPri = []     #stored as lists of dash patterns

        self.payoffs = []     #stored as lists of decimal payoffs

        if file:
            self.file = file
            self.loadVals()



    def dExport(self):
        """ Returns the game description as a dictionary """
        exptDict = {'dms'     :self.dmList,
                    'opts'    :self.optList,
                    'infeas'  :self.infeas,
                    'prefVec' :self.prefVec,
                    'irrev'   :self.irrev,
                    'prefPri' :self.prefPri,
                    'payoffs' :self.payoffs}
        return exptDict

    def dImport(self,d):
        """Imports values into the game from dictionary 'd'"""
        self.setDMs (   d['dms'])
        self.setOpts(   d['opts'])
        self.setInfeas( d['infeas'])
        self.setPref(   d['prefVec'])
        self.setIrrev(  d['irrev'])
        self.setPayoffs(d['payoffs'])
        try:
            self.setPrefPri(d['prefPri'])
        except KeyError:
            pass

    def loadVals(self):
        """Load a game from the file location in self.file"""
        try:
            savFile = open(self.file,mode='rb')
        except IOError:
            print('file not readable')
            raise Exception('the loaded file was invalid')
            return
        try:
            self.dImport(pkl.load(savFile))
        except EOFError:
            print('file is empty')
            return
        savFile.close()

    def saveVals(self):
        """Saves the current game to the file location in self.file"""
        try:
            savFile = open(self.file,mode='wb')
        except IOError:
            print('file not readable')
            return
        pkl.dump(self.dExport(),savFile)
        savFile.close

    def setFile(self,file):
        """Changes the file save/load location used."""
        self.file = file

    def getStateList(self,infeasIdx=-1):
        """Interface function.  Returns the list of infeasible states in
        dash notation"""
        if infeasIdx != -1:
            stateIter = iter(self._fromIndex(self.infeas[infeasIdx]))
        else:
            stateIter = iter(['-']*self.numOpts())
        states=[]

        for x in range(len(self.optList)):
            states.append([])
            for y in self.optList[x]:
                states[x].append([y,next(stateIter)])
        return states

    def getFlatOpts(self):
        """ Returns a list of all of the options in the game as a flat list."""
        flatOpts = []
        for x in self.optList:
            flatOpts+=x
        return flatOpts

    def setDMs(self,dms):
        """Interface function. Sets DMs in the game."""
        self.dmList  = dms
        self.prefVec = [[] for x in range(self.numDMs())]
        self.prefVecOrd = [[] for x in range(self.numDMs())]
        self.prefPri = [[] for x in range(self.numDMs())]
        self.payoffs = [[] for x in range(self.numDMs())]

    def numDMs(self):
        """Return the number of DMs in the game."""
        return len(self.dmList)

    def setOpts(self,opts):
        """Interface function. Sets Options in the game"""
        self.optList = opts

    def numOpts(self):
        """Return the number of options in the game."""
        return sum([len(x) for x in self.optList])

    def setInfeas(self,infeas):
        """Interface function. Sets infeasible states in the game."""
        self.infeas= []
        self.infeasMetaData = {}
        self.feasDash = ['-'*self.numOpts()]
        for pattern in infeas:
            self.addInfeas(pattern,external=False)
        self.feasDec   = sorted([self.bin2dec(state) for state in self.expandPatterns(self.feasDash)])
        self.ordered,self.expanded = self.orderedNumbers(self.feasDec)
        self.numFeas = len(self.feasDec)

    def addInfeas(self,infeas,external=True):
        """Add infeasible states to the game.  Input in dash format.
        
        The 'external' flag is set to false by some calls to prevent excessive
        recalculation of values when a large number of infeasibles are being
        added simultaneously.
        """
        if (not self.infeas) & bool(external) :  #adding a first infeasible state should go through "setInfeas"
             self.setInfeas([infeas])
             return None
        if infeas in self.infeas:
            return None
        self.infeas.append(infeas)
        res = self.rmvSt(self.feasDash,infeas)
        self.feasDash = res[0]
        self.infeasMetaData[infeas] = res
        if external:
            self.feasDec   = sorted([self.bin2dec(state) for state in self.expandPatterns(self.feasDash)])
            self.ordered,self.expanded = self.orderedNumbers(self.feasDec)
            self.numFeas = len(self.feasDec)

    def setIrrev(self,irrev):
        """Interface function. Sets irreversible states in the game."""
        self.irrev = irrev

    def setPref(self,prefs):
        """Interface function. Sets Preferences in the game."""
        self.prefVec = prefs
        self.payoffs = [[0]*(self.numOpts()**2) for x in range(self.numDMs())]

    def setPayoffs(self,payoffs):
        """Interface function. Sets Payoffs in the game.
        
        Conflicts with setPref, and is not used by the GUI program"""
        self.payoffs = payoffs

    def getInfeas(self,fmt='dash'):
        """Interface function.  Returns the infeasible states in the specified format.
        
        Valid formats are:
        dash: uses '1','0', and '-' to represent infeasible states compactly.
        'YN': lists all infeasible states using 'Y' and 'N'.
        'bin': lists all infeasible states using '1' and '0'.
        'dec': lists all infeasible states in decimal form.
        """
        if fmt == 'dash':
            return self.infeas
        if fmt == 'YN':
            ynInf = []
            for state in self.infeas:
                ynInf.append(''.join([self.toYN[x] for x in state]))
            return ynInf
        if fmt == 'bin':
            return sorted(set(self.expandPatterns(self.infeas)))
        if fmt == 'dec':
            return sorted(set([self.bin2dec(state) for state in self.expandPatterns(self.infeas)]))
        else:
            print('invalid format')

    def getFeas(self,fmt):
        """Interface function.  Returns the feasible states in the game in the specified format.
        
        Valid formats are:
        'dash': uses '1','0', and '-' to represent feasible states compactly.
        'YN-': uses 'Y','N', and '-' to represent feasible states compactly.
        'YN': lists all feasible states using 'Y' and 'N'.
        'bin': lists all feasible states using '1' and '0'.
        'dec': lists all feasible states in decimal form.
        'ord': lists all feasible states in ordered form.
        'ord_dec': lists all feasible states, as the ordered value followed by
            the decimal one in square brackets
  """
        if fmt == 'dash':
            return self.reducePatterns(self.feasDash)
        if fmt == 'YN-':
            ynFeas = []
            for state in self.reducePatterns(self.feasDash):
                ynFeas.append(''.join([self.toYN[x] for x in state]))
            return ynFeas
        if fmt == 'YN':
            ynFeas = []
            for state in self.expandPatterns(self.feasDash):
                ynFeas.append(''.join([self.toYN[x] for x in state]))
            return ynFeas
        if fmt == 'bin':
            return self.expandPatterns(self.feasDash)
        if fmt == 'dec':
            return self.feasDec
        if fmt == 'ord':
            return list(self.ordered.keys())
        if fmt == 'ord_dec':
            return ['%3d  [%s]'%(self.ordered[x],x) for x in reversed(self.feasDec)]
        else:
            print('invalid format')

    def moveInfeas(self,idx,targ):
        """move an infeasible state from position idx in the list to position targ."""
        self.infeas.insert(targ,self.infeas.pop(idx))
        self.updateInfeas(min(idx,targ))

    def removeInfeas(self,idx):
        """remove the infeasible state at position idx"""
        del self.infeasMetaData[self.infeas[idx]]
        del self.infeas[idx]
        self.updateInfeas(idx)
        self.feasDec   = sorted([self.bin2dec(state) for state in self.expandPatterns(self.feasDash)])
        self.ordered,self.expanded = self.orderedNumbers(self.feasDec)
        self.numFeas = len(self.feasDec)

    def updateInfeas(self,idx=None):
        """Updates all infeasible calculations below idx. If idx not given, update all."""
        if not self.infeas:
            self.feasDash = ['-'*self.numOpts()]
        if not idx:
            idx = 0
            self.feasDash = ['-'*self.numOpts()]
        else:
            self.feasDash = self.infeasMetaData[self.infeas[idx-1]][0]
        if idx< len(self.infeas):
            infeas = self.infeas[idx]
            res = self.rmvSt(self.feasDash,infeas)
            self.feasDash = res[0]
            self.infeasMetaData[infeas] = res

            self.updateInfeas(idx+1)

    def mapPayoffs(self):
        """Map the preference vectors provided into payoff values for each state."""
        for dmi,dm in enumerate(self.prefVec):		#DM index, preference vector for that DM
            for state in dm:
                if state not in self.feasDec:
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

    def setPrefPri(self,prefPri):
        """If data is provided, populate the game's preference priority settings with it.
        Otherwise, reinitialize the preference priorities to blank."""
        if prefPri:
            self.prefPri = prefPri
        else:
            self.prefPri = [[] for x in range(self.numDMs())]

    def addPreference(self,dmIdx,state):
        """Append a new preferred state for a DM, in the lowest priority position."""
        if state not in self.prefPri[dmIdx]:
            self.prefPri[dmIdx].append(state)

    def removePreference(self,dmIdx,idx):
        """Remove the specified preferred state from a DM's profile"""
        del self.prefPri[dmIdx][idx]

    def movePreference(self,dmIdx,idx,targ):
        """Move a preference from position idx in the DM's list to position targ."""
        self.prefPri[dmIdx].insert(targ,self.prefPri[dmIdx].pop(idx))

    def rankPreferences(self,dmIdx):
        """returns a refreshed preference vector for the given DM."""
        self.rankStates(dmIdx)
        return str(self.prefVecOrd[dmIdx])[1:-1]

    def matchesCrit(self,stateX,criteriaX):
        """returns True if stateX is in the set specified by criteriaX"""
        stateX = self.dec2bin(stateX)
        criteria = self._toIndex(criteriaX)
        for x in criteria:
            if stateX[x[0]] != x[1]:
                return False
        return True

    def rankStates(self,dmIdx):
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

    def rankAll(self):
        """calls rankState for every DM in the conflict."""
        for dm in range(self.numDMs()):
            self.rankStates(dm)


# ##################

def main():
    # #################################################################################
    # #############                     INPUTS                            #############
    # #################################################################################

        # Define DMs:
        #   write as a list of strings
        #   ex: ["Americans","British","Canadians"]
    DMnames = ["Americans","British"]


        # Define Options:
        #   a list for each DM, listed in the same order as above
        #   ex:   [  ["Escalate","Petition"], ["Dance"]  ]
    Options =   [   ["Boycott","Riot","Militias","Declare"],
                    ["Tax","Military","Supression"]]

        # Define Infeasible States:
        #   list infeasible outcomes as list of tuples (position, state)
        #   ex:   ( 1 - - 1 - 1) would be [(0,1), (3,1), (5,1)]
    infeasible = ['---11--',    #no tax possible if declaration

                  '--01---',    #no independence without militia
                  '---1--0',    #no independence without suppression

                  '-----01',    #no suppression without military
                 ]

        # Define irreversible moves:
        #   List irreversible moves as [OptionNumber, 'position that can't be moved away from']
    UseIrreversibles = True
    irreversible = [    [3, '1']        # Declaration of Independence is irreversible
                   ]

    payoffs = [[],
               []]

        # Define Preference Vector     (or see Option Prioritization below)
        #   vector of payoff values, including all feasible states in ascending decimal order
    prefVec = [ [],
                []]


        # Define Preferences through Option Prioritization
        #   Set this option to 'True' if Prioritization should be used.  This will
        #   cause the preference vector defined above to be ignored, and a new
        #   preference vector will be created based on the priorities defined.
        # Define Priorities below:
        #   Format is somewhat complex, related to the infeasible state format.
    PrefPriorities=[    [   #First DM priority list
                            ['True',  [(6,'0')]           ],     # Prefer No Supression
                            ['True',  [(4,'0')]  ],              # Prefer No Tax
                            ['True',  [(3,'0'), (6,'0')]  ],     # Prefer no Declaration if no Supression
                            ['True',  [(3,'1'), (6,'1')]  ],     # Prefer Declaration if Supression
                            ['True',  [(0,'0'), (4,'0')]  ],     # Prefer no Boycott if no Tax
                            ['True',  [(0,'1'), (4,'1')]  ],     # Prefer Boycott if Tax
                            ['True',  [(5,'0')]  ],              # Prefer no military presence
                            ['If',    [(2,'1')],  [(4,'1'),(5,'1'),(6,'1')]   ],    #Prefer having Militias if British do (Tax, Military,Supression)
                            ['If',    [(1,'1')],  [(4,'1'),(5,'1'),(6,'1')]   ],    #Prefer Rioting if British do (Tax, Military, Supression)
                            ['If',    [(3,'1')],  [(4,'1'),(5,'1'),(6,'1')]   ],    #Prefer Declaration if British do (Tax, Military, Supression)
                            ['If',    [(0,'1')],  [(4,'1'),(5,'1'),(6,'1')]   ],    #Prefer Boycott if British do (Tax, Military, Supression)
                            ['True',  [(1,'0'), (6,'1')]  ]                         #Prefer no Riots if Suppression
                        ],

                        [   #Second DM priority list
                            ['True',  [(3,'0')]               ],        # Prefer No Declaration
                            ['True',  [(0,'0')]               ],        # Prefer No Boycott
                            ['True',  [(1,'0')]               ],        # Prefer No Riot
                            ['True',  [(0,'0'),(4,'1')]       ],        # Prefer to Tax if no boycott
                            ['True',  [(0,'1'),(4,'0')]       ],        # Prefer to Tax if no boycott
                            ['True',  [(5,'1'), (1,'1')]      ],        # Prefer Military if Riots
                            ['True',  [(5,'1'), (0,'1')]      ],        # Prefer Military if Boycotts
                            ['True',  [(5,'0')]               ],        # Prefer No Military
                            ['True',  [(6,'0'), (1,'0')]      ],        # Prefer No Suppression if No Riots
                            ['True',  [(6,'1'), (1,'1')]      ],        # Prefer Suppression if Riots
                            ['True',  [(5,'1'), (3,'1')]      ]         # Prefer Military if Declaration
                        ]
                   ]


    # #################### actual testing
    testGame = ConflictModel()

    testGame.setFile('AmRv2.gmcr')

    infoDict = {'dms'     :DMnames,
                'opts'    :Options,
                'infeas'  :infeasible,
                'irrev'   :irreversible,
                'prefVec' :prefVec,
                'prefPri' :PrefPriorities,
                'payoffs' :payoffs}

    testGame.dImport(infoDict)

    testGame.saveVals()



if __name__ == '__main__':
    main()
