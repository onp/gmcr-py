# class to hold all information about the current state of the conflict,
# and serve it up to the UI elements and calculators.

import json
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
        self.preferences = ConditionList(masterOptionList)

    def __str__(self):
        return self.name
        
    def export_rep(self):
        return {'name':str(self.name),
                'options':self.options.export_rep(),
                'preferences':self.preferences.export_rep()}

    def addOption(self,option):
        if option not in self.options:
            self.options.append(option)
        
    def removeOption(self,option):
        if option in self.options:
            self.options.remove(option)
            
    def weightPreferences(self):
        for idx,pref in enumerate(self.preferences):
            pref.weight = 2**(len(self.preferences)-idx-1)
            
    def calculatePayoffs(self):
        pass
        # NOT USED RIGHT NOW
        #check if using preference prioritization, or manual input
        #generate payoffs and preference vector
        #OR map preference vector into payoffs
            
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
        
    def test(self,state):
        """Test against a decimal state. Returns True if state meets the Condition."""
        self.masterOptionList.set_indexes()
        state = gmcrUtil.dec2yn(state,len(self.masterOptionList))
        for opt,taken in self.cond():
            if state[opt.master_index] != taken:
                return False
        return True
        
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
        
    def index(self,i):
        return self.itemList.index(i)
        
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
        for preference in dmData['preferences']:
            newDM.preferences.from_json(preference)
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
        
    def from_json(self,condData):
        newCondition = [(self.masterOptionList[opt],taken) for opt,taken in condData]
        self.append(newCondition)

    def append(self,item):
        if isinstance(item,Condition):
            self.itemList.append(item)
        elif isinstance(item,list):
            self.itemList.append(Condition(item,self.masterOptionList))
        else:
            print(item)
            raise TypeError('Not a valid Condition Object')
            
    def moveCondition(self,idx,targ):
        """Move a condition from position idx in the list to position targ."""
        j = self.pop(idx)
        self.insert(targ,j)

    def removeCondition(self,idx):
        """Remove the Condition at position idx"""
        del self[idx]
            
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
        self.ordered = sorted(self.toDecimal.keys())                            #as ordered numbers
        self.ordDec = ['%3d  [%s]'%(self.toOrdered[x],x) for x in reversed(self.decimal)]     #special display notation
    
    def __len__(self):
        return len(self.decimal)


class ConflictModel:
    def __init__(self):
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


    def export_rep(self):
        """Generates a representation of the conflict suitable for JSON encoding."""
        self.reorderOptionsByDM()
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
        for infData in d['infeasibles']:
            self.infeasibles.from_json(infData)
        self.reorderOptionsByDM()
        self.recalculateFeasibleStates()

#            self.setPref(   d['prefVec'])
#          self.setPayoffs(d['payoffs'])
#         self.setPrefPri(d['prefPri'])


    def load_from_file(self,file):
        """Load a conflict from the file given."""
        self.__init__()
        self.file = file
        try:
            fileObj = open(file,mode='r')
        except IOError:
            print('file not readable')
            return
        try:
            self.json_import(json.load(fileObj))
        except EOFError:
            print('file is empty')
            return
        finally:
            fileObj.close()

    def recalculateFeasibleStates(self):
        """Updates all feasible state calculations."""
        print("recalculating feasible states")
        feasDash = ['-'*len(self.options)]
        for infeas in self.infeasibles:
            res = gmcrUtil.rmvSt(feasDash,infeas.ynd())
            feasDash = res[0]
            infeas.statesRemoved = res[1]
        self.feasibles = FeasibleList(res[0])

    def reorderOptionsByDM(self):
        moved = []
        for dm in self.decisionMakers:
            for option in dm.options:
                if option not in moved:
                    moved.append(option)
                    self.options.insert(len(moved),self.options.pop(self.options.index(option)))
        self.options.set_indexes()
                

