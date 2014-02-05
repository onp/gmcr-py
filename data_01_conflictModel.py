# Copyright:   (c) Oskar Petersons 2013

"""Core data model and class definitions for GMCR-py."""

import json
import data_03_gmcrUtilities as gmcrUtil


class Option:
    def __init__(self,name,permittedDirection='both'):
        self.name = str(name)
        self.permittedDirection = permittedDirection
    
    def __str__(self):
        return self.name
        
    def export_rep(self):
        return {'name':str(self.name),
                'permittedDirection':str(self.permittedDirection)}
        
class DecisionMaker:
    def __init__(self,conflict,name):
        self.name = str(name)
        self.conflict = conflict
        self.options = OptionList(conflict.options)
        self.preferences = ConditionList(conflict)

    def __str__(self):
        return self.name
        
    def export_rep(self):
        rep  = {}
        rep['name'] = str(self.name)
        rep['options'] = self.options.export_rep()
        rep['preferences'] = self.preferences.export_rep()
        if self.conflict.useManualPreferenceVectors:
            rep['preferenceVector'] = self.preferenceVector
        return rep

    def addOption(self,option):
        if option not in self.options:
            self.options.append(option)
        
    def removeOption(self,option):
        if option in self.options:
            self.options.remove(option)
            
    def weightPreferences(self):
        for idx,pref in enumerate(self.preferences):
            pref.weight = 2**(len(self.preferences)-idx-1)
            
    def calculatePreferences(self):
        if self.conflict.useManualPreferenceVectors:
            self.payoffs = gmcrUtil.mapPrefVec2Payoffs(self.preferenceVector,self.conflict.feasibles)
        else:
            self.weightPreferences()
            result = gmcrUtil.prefPriorities2payoffs(self.preferences,self.conflict.feasibles)
            self.payoffs = result[0]
            self.preferenceVector = result[1]


class Condition:
    """A list of options either taken or not taken against which a state can be tested."""
    def __init__(self,conflict,condition):
        self.conflict = conflict
        self.options = OptionList(conflict.options)
        self.taken = []
        for opt,taken in condition:
            self.options.append(opt)
            self.taken.append(taken)
        self.name = self.ynd()

    def __str__(self):
        return self.name + " object"
        
    def cond(self):
        """The condition represented as tuples of options and whether or not they are taken."""
        return zip(self.options,self.taken)
        
    def ynd(self):
        """Returns the condition in 'Yes No Dash' notation."""
        self.conflict.options.set_indexes()
        ynd = ['-']*len(self.conflict.options)
        for opt,taken in self.cond():
            ynd[opt.master_index] = taken
        return ''.join(ynd)
        
    def test(self,state):
        """Test against a decimal state. Returns True if state satisfies the Condition."""
        self.conflict.options.set_indexes()
        state = gmcrUtil.dec2yn(state,len(self.conflict.options))
        for opt,taken in self.cond():
            if state[opt.master_index] != taken:
                return False
        return True
        
    def export_rep(self):
        self.conflict.options.set_indexes()
        return [(opt.master_index,taken) for opt,taken in self.cond()]

class CompoundCondition:
    """A condition defined as a union of simple conditions."""
    def __init__(self,conflict,conditions):
        self.conflict = conflict
        self.conditions = [Condition(self.conflict,dat) for dat in conditions]
        self.name = str(self.ynd())[1:-1]
        
    def __str__(self):
        return self.name + " object"
        
    def addCondition(self,condition):
        """Adds the condition given to the compound condition."""
        self.conditions.append(condition)
        self.name = str(self.ynd())[1:-1]
    
    def removeCondition(self,idx):
        """Removes the condition at idx from the compound condition."""
        del self.conditions[idx]
        self.name = str(self.ynd())[1:-1]
    
    def ynd(self):
        """Returns the compound condition as a list with items in 'Yes No Dash' notation."""
        return [cond.ynd() for cond in self.conditions]
        
        
    def test(self,state):
        """Test against a decimal state. Returns True if state satisfies one or
        more of the component conditions."""
        for cond in self.conditions:
            if cond.test(state):
                return True
        return False            
    
    def export_rep(self,state):
        return {"compound":True,"members":[cond.export_rep() for cond in self.conditions]}
    

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
            item.dec_val = 2**(idx)

            
class DecisionMakerList(ObjectList):
    def __init__(self,conflict):
        ObjectList.__init__(self)
        self.conflict = conflict

    def export_rep(self):
        return [x.export_rep() for x in self.itemList]

    def append(self,item):
        if isinstance(item,DecisionMaker) and item not in self.itemList:
            self.itemList.append(item)
        elif isinstance(item,str):
            self.itemList.append(DecisionMaker(self.conflict,item))

    def from_json(self,dmData):
        newDM = DecisionMaker(self.conflict,dmData['name'])
        for optIdx in dmData['options']:
            newDM.options.append(self.conflict.options[int(optIdx)])
        for preference in dmData['preferences']:
            newDM.preferences.from_json(preference)
        if self.conflict.useManualPreferenceVectors:
            newDM.preferenceVector = dmData['preferenceVector']
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
        newOption = Option(optData['name'],optData['permittedDirection'])
        self.append(newOption)
            
class ConditionList(ObjectList):
    def __init__(self,conflict):
        ObjectList.__init__(self)
        self.conflict = conflict
        
    def export_rep(self):
        return [x.export_rep() for x in self.itemList]
        
    def from_json(self,condData):
        """Replaces the option number with the actual option object."""
        if isinstance(condData,list):
            for opt in condData:
                opt[0] = self.conflict.options[opt[0]]
        elif isinstance(condData,dict):
            for mem in condData['members']:
                for opt in mem:
                    opt[0] = self.conflict.options[opt[0]]
        self.append(condData)

    def append(self,item):
        if isinstance(item,Condition):
            newCondition = item
        elif isinstance(item,list):
            newCondition = Condition(self.conflict,item)
        elif isinstance(item,dict):
            newCondition = CompoundCondition(item['members'])
        else:
            print(item)
            raise TypeError('Not a valid Condition Object')
        if newCondition.ynd() not in [cond.ynd() for cond in self]:
            self.itemList.append(newCondition)
        else:
            print("attempted to add duplicate; ignored")
            
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
            return [self.yn2dec(state) for state in self.format('YN')]
        else:
            print('invalid format')


class FeasibleList:
    def __init__(self,dash=None):
        if not dash:
            self.decimal = []
            self.dash = []
            return
        self.dash = gmcrUtil.reducePatterns(dash)                               #as 'Y,N,-' compact patterns
        temp = sorted([(gmcrUtil.yn2dec(yn),yn) for yn in gmcrUtil.expandPatterns(self.dash)])
        self.yn = [yn for dec,yn in temp]                                       #as 'Y,N' patterns
        self.decimal   = [dec for dec,yn in temp]                               #as decimal values
        self.toOrdered,self.toDecimal = gmcrUtil.orderedNumbers(self.decimal)   #conversion dictionaries
        self.ordered = sorted(self.toDecimal.keys())                            #as ordered numbers
        self.ordDec = ['%3d  [%s]'%(ord,dec) for ord,dec in zip(self.ordered,self.decimal)]     #special display notation
    
    def __len__(self):
        return len(self.decimal)


class ConflictModel:
    def __init__(self):
        """Initializes a new, empty conflict.  If 'file' is given, loads values from 'file'"""

        self.options = OptionList()       #list of Option objects
        self.decisionMakers = DecisionMakerList(self)        #list of DecisonMaker objects
        self.infeasibles  = ConditionList(self)       #list of Condition objects
        self.feasibles = FeasibleList()

        self.useManualPreferenceVectors = False
        self.preferenceErrors = None


    def export_rep(self):
        """Generates a representation of the conflict suitable for JSON encoding."""
        self.reorderOptionsByDM()
        return {'decisionMakers':self.decisionMakers.export_rep(),
                'options':self.options.export_rep(),
                'infeasibles':self.infeasibles.export_rep(),
                'useManualPreferenceVectors':self.useManualPreferenceVectors,
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
        self.useManualPreferenceVectors = d['useManualPreferenceVectors']
        for optData in d['options']:
            self.options.from_json(optData)
        for dmData in d['decisionMakers']:
            self.decisionMakers.from_json(dmData)
        for infData in d['infeasibles']:
            self.infeasibles.from_json(infData)
        self.reorderOptionsByDM()
        self.recalculateFeasibleStates()


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
        self.feasibles = FeasibleList(feasDash)

    def reorderOptionsByDM(self):
        moved = []
        for dm in self.decisionMakers:
            for option in dm.options:
                if option not in moved:
                    moved.append(option)
                    self.options.insert(len(moved),self.options.pop(self.options.index(option)))
        self.options.set_indexes()
                
    def breakingChange(self):
        self.useManualPreferenceVectors = False
        self.reorderOptionsByDM()
        self.recalculateFeasibleStates()
        for dm in self.decisionMakers:
            dm.preferenceVector = None
            dm.calculatePreferences()
