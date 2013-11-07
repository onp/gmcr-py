# class to hold all information about the current state of the conflict,
# and serve it up to the UI elements and calculators.

import json
import itertools
import data_03_gmcrUtilities as gmcrUtil


class Option:
    def __init__(self,name,reversibility='both'):
        self.name = str(name)
        self.reversibility = reversibility
    
    def __str__(self):
        return self.name
        
    def export_rep(self):
        return {'name':str(self.name),
                'reversibility':str(self.reversibility)}
        
class DecisionMaker:
    def __init__(self,name,masterOptionList):
        self.name = str(name)
        self.options = OptionList(masterOptionList)

    def __str__(self):
        return self.name
        
    def export_rep(self):
        return {'name':str(self.name),
                'options':self.options.export_rep()}

    def addOption(self,option):
        if option not in self.options:
            self.options.append(option)
        
    def removeOption(self,option):
        if option in self.options:
            self.options.remove(option)
            
class Condition:
    """A list of options either taken or not taken against which a state can be tested."""
    def __init__(self,condition,masterOptionList):
        self.options = OptionList(masterOptionList)
        self.masterOptionList = masterOptionList
        self.taken = []
        for opt,taken in condition:
            self.options.append(opt)
            self.taken.append(taken)
        self.name = self.ynd()

    def __str__(self):
        return self.name + " object"
        
    def cond(self):
        """The condition represented tuples of options and whether or not they are taken."""
        return zip(self.options,self.taken)
        
    def ynd(self):
        """Returns the condition in 'Yes No Dash' notation."""
        self.masterOptionList.set_indexes()
        ynd = ['-']*len(self.masterOptionList)
        for opt,taken in self.cond():
            ynd[opt.master_index] = taken
        return ''.join(ynd)
        
        
    def export_rep(self):
        self.masterOptionList.set_indexes()
        return [(opt.master_index,taken) for opt,taken in self.cond()]



class ObjectList:
    def __init__(self,masterList=None):
        self.itemList = []
        self.masterList = masterList
        
    def __len__(self):
        return len(self.itemList)
        
    def __getitem__(self,key):
        return self.itemList[key]
        
    def __setitem__(self,key,value):
        self.itemList[key] = value
        
    def __delitem__(self,key):
        del self.itemList[key]
        
    def __iter__(self):
        return iter(self.itemList)
        
    def __reversed__(self):
        return reversed(self.itemList)
        
    def __contains__(self,item):
        return item in self.itemList
        
    def insert(self,i,x):
        self.itemList.insert(i,x)
        
    def pop(self,i=None):
        return self.itemList.pop(i)
        
    def set_indexes(self):
        for idx,item in enumerate(self.itemList):
            item.master_index = idx

            
class DecisionMakerList(ObjectList):
    def __init__(self,masterOptionList):
        ObjectList.__init__(self)
        self.masterOptionList = masterOptionList

    def export_rep(self):
        return [x.export_rep() for x in self.itemList]

    def append(self,item):
        if isinstance(item,DecisionMaker) and item not in self.itemList:
            self.itemList.append(item)
        elif isinstance(item,str):
            self.itemList.append(DecisionMaker(item,self.masterOptionList))

    def from_json(self,dmData):
        newDM = DecisionMaker(dmData['name'],self.masterOptionList)
        for optIdx in dmData['options']:
            newDM.options.append(self.masterOptionList[int(optIdx)])
        self.append(newDM)

class OptionList(ObjectList):
    def __init__(self,masterList=None):
        ObjectList.__init__(self,masterList)
        
    def export_rep(self):
        if self.masterList is not None:
            self.masterList.set_indexes()
            return [x.master_index for x in self.itemList]
        else:
            return [x.export_rep() for x in self.itemList]

    def append(self,item):
        if isinstance(item,Option) and item not in self.itemList:
            self.itemList.append(item)
            if (self.masterList is not None) and (item not in self.masterList):
                self.masterList.append(item)
        elif isinstance(item,str):
            newOption = Option(item)
            self.itemList.append(newOption)
            if self.masterList is not None:
                self.masterList.append(newOption)
                
    def from_json(self,optData):
        newOption = Option(optData['name'],optData['reversibility'])
        self.append(newOption)
            
class ConditionList(ObjectList):
    def __init__(self,masterOptionList):
        ObjectList.__init__(self)
        self.masterOptionList = masterOptionList
        
    def export_rep(self):
        return [x.export_rep() for x in self.itemList]

    def append(self,item):
        if isinstance(item,Condition):
            self.itemList.append(item)
        elif isinstance(item,list):
            self.itemList.append(Condition(item,self.masterOptionList))
        else:
            raise TypeError('%s is not a valid Condition Object'%(item))
            
    def format(self,fmt="YN-"):
        """Returns the conditions in the specified format.
        
        Valid formats are:
        'YN-': uses 'Y','N', and '-' to represent infeasible states compactly.
        'YN': lists all infeasible states using 'Y' and 'N'.
        'dec': lists all infeasible states in decimal form.
        """
        if fmt == 'YN-':
            return [x.ynd() for x in self]
        if fmt == 'YN':
            return sorted(set(gmcrUtil.expandPatterns(self.format('YN-'))))
        if fmt == 'dec':
            return sorted(set([self.bin2dec(state) for state in self.expandPatterns(self.infeas)]))
        else:
            print('invalid format')

class FeasibleList:
    def __init__(self,dash=None):
        if not dash:
            self.decimal = []
            self.dash = []
            return
        self.dash = gmcrUtil.reducePatterns(dash)                               #as 'Y,N,-' compact patterns
        self.yn = gmcrUtil.expandPatterns(self.dash)                            #as 'Y,N' patterns
        self.decimal   = sorted([gmcrUtil.yn2dec(state) for state in self.yn])  #as decimal values
        self.toOrdered,self.toDecimal = gmcrUtil.orderedNumbers(self.decimal)   #conversion dictionaries
        self.ordered = sorted(self.toOrdered.keys())                            #as ordered numbers
        self.ordDec = ['%3d  [%s]'%(self.toOrdered[x],x) for x in reversed(self.decimal)]     #special display notation
    
    def __len__(self):
        return len(self.decimal)


class ConflictModel:
    def __init__(self,file=None):
        """Initializes a new, empty conflict.  If 'file' is given, loads values from 'file'"""

        self.options = OptionList()       #list of Option objects
        self.decisionMakers = DecisionMakerList(self.options)        #list of DecisonMaker objects
        self.infeasibles  = ConditionList(self.options)       #list of Condition objects
        self.feasibles = FeasibleList()

        self.irrev = []         #stored as (idx,'val') tuples

        self.prefVec = []    
        self.prefVecOrd = []

        self.prefPri = []     #stored as lists of dash patterns

        self.payoffs = []     #stored as lists of decimal payoffs

        self.file = file
        if self.file is not None:
            self.load_from_file(self.file)

    def export_rep(self):
        """Generates a representation of the conflict suitable for JSON encoding."""
        return {'decisionMakers':self.decisionMakers.export_rep(),
                'options':self.options.export_rep(),
                'infeasibles':self.infeasibles.export_rep(),
                'program':'gmcr-py'}
        
    def save_to_file(self,file):
        """Saves the current conflict to the file location given."""
        print(self.export_rep())
        try:
            fileObj = open(file,mode='w')
        except IOError:
            print('file not readable')
            return
        try:
            json.dump(self.export_rep(),fileObj)
        finally:
            fileObj.close()

    def json_import(self,d):
        """Imports values into the conflict from JSON data d"""
        for optData in d['options']:
            self.options.from_json(optData)
        for dmData in d['decisionMakers']:
            self.decisionMakers.from_json(dmData)
        # load infeasible states
        try:
            self.setPref(   d['prefVec'])
            self.setIrrev(  d['irrev'])
            self.setPayoffs(d['payoffs'])
            self.setPrefPri(d['prefPri'])
        except KeyError:
            pass

    def load_from_file(self,file):
        """Load a conflict from the file given."""
        try:
            fileObj = open(file,mode='r')
        except IOError:
            print('file not readable')
            raise Exception('the loaded file was invalid')
            return
        try:
            self.json_import(json.load(fileObj))
        except EOFError:
            print('file is empty')
            return
        finally:
            fileObj.close()


    def addInfeasibleState(self,infeas):
        """Add infeasible states to the conflict.
        
        Input is as a list of tuples of the form (Option object, Option state)
        where Option Object is an Option Object that is already in the conflict,
        and Option state is the value of either 'Y' or 'N'
        """
        
        self.infeasibles.append(infeas)

    def setPref(self,prefs):
        """Sets Preferences in the conflict."""
        self.prefVec = prefs
        self.payoffs = [[0]*(self.numOpts()**2) for x in range(self.numDMs())]

    def setPayoffs(self,payoffs):
        """Sets Payoffs in the conflict.
        
        Conflicts with setPref, and is not used by the GUI program"""
        self.payoffs = payoffs
        

    def moveInfeas(self,idx,targ):
        """move an infeasible state from position idx in the list to position targ."""
        print(self.infeasibles[idx])
        print(self.infeasibles)
        j = self.infeasibles.pop(idx)
        print(j)
        self.infeasibles.insert(targ,j)
        self.recalculateFeasibleStates()

    def removeInfeas(self,idx):
        """remove the infeasible state at position idx"""
        del self.infeasibles[idx]
        self.recalculateFeasibleStates()


    def recalculateFeasibleStates(self):
        """Updates all feasible state calculations."""
        print("recalculating feasible states")
        feasDash = ['-'*len(self.options)]
        for infeas in self.infeasibles:
            res = gmcrUtil.rmvSt(feasDash,infeas.ynd())
            feasDash = res[0]
            infeas.statesRemoved = res[1]
        self.feasibles = FeasibleList(res[0])

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
        """If data is provided, populate the conflict's preference priority settings with it.
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

