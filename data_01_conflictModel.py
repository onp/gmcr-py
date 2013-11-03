# class to hold all information about the current state of the conflict,
# and serve it up to the UI elements and calculators.

import json
import itertools
import data_03_gmcrUtilities as gmcrUtil


class Option:
    def __init__(self,name):
        self.name = str(name)
    
    def __str__(self):
        return self.name
        
    def export_rep(self):
        return {'name':str(self.name)}
        
class DecisionMaker:
    def __init__(self,name,masterOptionList):
        self.name = str(name)
        self.options = OptionList(masterOptionList)

    def __str__(self):
        return self.name
        
    def export_rep(self):
        return {'name':str(self.name),'options':self.options.export_rep()}

    def addOption(self,option):
        if option not in self.options:
            self.options.append(option)
        
    def removeOption(self,option):
        if option in self.options:
            self.options.remove(option)
            
class Condition:
    """A list of options either taken or not taken against which a state can be tested."""
    def __init__(self,name=''):
        self.name = str(name)
        self.options = []
        self.taken = []

    def __str__(self):
        return self.name +': '+ str(list(self.asReferences))

    def addCondition(self,option,taken):
        self.options.append(option)
        self.taken.append(taken)

    def asReferences(self):
        return zip(self.options,self.taken)



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
        if isinstance(item,DecisionMaker):
            self.itemList.append(item)
        elif isinstance(item,str):
            self.itemList.append(DecisionMaker(item,self.masterOptionList))
            
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
        if isinstance(item,Option):
            self.itemList.append(item)
            if (self.masterList is not None) and (item not in self.masterList):
                self.masterList.append(item)
        elif isinstance(item,str):
            newOption = Option(item)
            self.itemList.append(newOption)
            if self.masterList is not None:
                self.masterList.append(newOption)
            
class ConditionList(ObjectList):
    def __init__(self):
        ObjectList.__init__(self)
        
    def export_rep(self):
        return [x.export_rep() for x in self.itemList]

    def append(self,item):
        if isinstance(item,Condition):
            self.itemList.append(item)
        else:
            raise TypeError('%s is not a valid Condition Object'%(item))






class ConflictModel:
    def __init__(self,file=None):
        """Initializes a new, empty conflict.  If 'file' is given, loads values from 'file'"""

        self.options = OptionList()       #list of Option objects
        self.decisionMakers = DecisionMakerList(self.options)        #list of DecisonMaker objects

        self.infeas  = ConditionList()       #list of Condition objects
        
        self.feasDec = []       #stored as decimal values
        self.feasDash= []       #stored as dash patterns
        self.ordered = {}       #decimal -> ordered dictionary
        self.expanded = {}      #ordered -> decimal dictionary
        self.numFeas = 0        #number of feasible states, integer

        self.irrev = []         #stored as (idx,'val') tuples

        self.prefVec = []    
        self.prefVecOrd = []

        self.prefPri = []     #stored as lists of dash patterns

        self.payoffs = []     #stored as lists of decimal payoffs

        self.file = file
        if self.file:
            self.loadVals()

    def export_rep(self):
        return {'decisionMakers':self.decisionMakers.export_rep(),
                'options':self.options.export_rep()}

    def json_export(self):
        return json.dumps(self.export_rep())

#    def dExport(self):
#        """ Returns the conflict description as a dictionary """
#        exptDict = {'decisionMakers' :self.dmList,
#                    'options' :self.optList,
#                    'infeas'  :self.infeas,
#                    'prefVec' :self.prefVec,
#                    'irrev'   :self.irrev,
#                    'prefPri' :self.prefPri,
#                    'payoffs' :self.payoffs}
#        return exptDict

    def dImport(self,d):
        """Imports values into the conflict from dictionary 'd'"""
        self.setDMs (   d['decisionMakers'])
        self.setOpts(   d['options'])
        try:
            self.setInfeas( d['infeas'])
            self.setPref(   d['prefVec'])
            self.setIrrev(  d['irrev'])
            self.setPayoffs(d['payoffs'])
            self.setPrefPri(d['prefPri'])
        except KeyError:
            pass

    def load_from_file(self,file):
        """Load a conflict from the file given."""
        try:
            fileData = open(file,mode='r')
        except IOError:
            print('file not readable')
            raise Exception('the loaded file was invalid')
            return
        try:
            self.json_import(json.loads(fileData))
        except EOFError:
            print('file is empty')
            return
        savFile.close()

    def save_to_file(self,file):
        """Saves the current conflict to the file location given."""
        print(self.json_export())
        try:
            savFile = open(self.file,mode='w')
        except IOError:
            print('file not readable')
            return
        
        savFile.close()

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
        """ Returns a list of all of the options in the conflict as a flat list."""
        return [x.name for x in self.options]

    def setDMs(self,data):
        """Creates decision makers from save data."""
        self.decisionMakers = []
        for dmData in dms:
            dm = DecisionMaker(dmData.name)
            for index in dmData.options:
                dm.addOption(self.options[index])
            self.decisionMakers.append(dm)
            
    #    self.prefVec = [[] for x in range(self.numDMs())]
    #    self.prefVecOrd = [[] for x in range(self.numDMs())]
    #    self.prefPri = [[] for x in range(self.numDMs())]
    #    self.payoffs = [[] for x in range(self.numDMs())]

    def numDMs(self):
        """Return the number of DMs in the conflict."""
        return len(self.decisionMakers)

    def setOpts(self,data):
        """Creates options in the conflict from save data."""
        self.options = []
        for optData in data:
            opt = Option(optData)
            self.options.append(opt)

    def numOpts(self):
        """Return the number of options in the conflict."""
        return len(self.options)

    def setInfeas(self,data):
        """Interface function. Sets infeasible states in the conflict."""
        self.infeas= []
        
        self.infeasMetaData = {}
        self.feasDash = ['-'*self.numOpts()]
        for pattern in infeas:
            self.addInfeas(pattern,external=False)
        self.feasDec   = sorted([self.bin2dec(state) for state in self.expandPatterns(self.feasDash)])
        self.ordered,self.expanded = self.orderedNumbers(self.feasDec)
        self.numFeas = len(self.feasDec)

    def addInfeas(self,infeas,external=True):
        """Add infeasible states to the conflict.  Input in dash format.
        
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
        """Interface function. Sets irreversible states in the conflict."""
        self.irrev = irrev

    def setPref(self,prefs):
        """Interface function. Sets Preferences in the conflict."""
        self.prefVec = prefs
        self.payoffs = [[0]*(self.numOpts()**2) for x in range(self.numDMs())]

    def setPayoffs(self,payoffs):
        """Interface function. Sets Payoffs in the conflict.
        
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
        """Interface function.  Returns the feasible states in the conflict in the specified format.
        
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
            for state in gmcrUtil.reducePatterns(self.feasDash):
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
    testconflict = ConflictModel()

    testconflict.setFile('AmRv2.gmcr')

    infoDict = {'dms'     :DMnames,
                'opts'    :Options,
                'infeas'  :infeasible,
                'irrev'   :irreversible,
                'prefVec' :prefVec,
                'prefPri' :PrefPriorities,
                'payoffs' :payoffs}

    testconflict.dImport(infoDict)

    testconflict.saveVals()



if __name__ == '__main__':
    main()
