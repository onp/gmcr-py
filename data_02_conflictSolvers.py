# class to hold all information about the current state of the game,
# and serve it up to the UI elements and calculators.

import numpy as np
import itertools
import json

class RMGenerator:
    """Reachability matrix class.
    
    When initialized with a game for data, it produces a reachability matrix
    for it.  
    
    Key methods for extracting data from the matrix are:
    reachable(dm,state)
    uis(dm,state)
    
    Other methods are provided that allow the reachability data to be exported.
    
    """
    def __init__(self,game):

        self.game = game

        # Generate move value lists for each player
        mvNm=0
        movelists = []
        for dmMv in [len(x) for x in game.optList]:
            movelists.append([2**mvNm for mvNm in range(mvNm,dmMv+mvNm)])
            mvNm += dmMv

        #initialize matrices
        self.reachabilityMatrices = [np.ones((game.numFeas+1,game.numFeas+1),dtype='i4')*-1 for x in range(game.numDMs())]

        for dm in range(game.numDMs()):

            #assign simpler name to the current focal DM's reachability matrix
            focalReachMat = self.reachabilityMatrices[dm]

            # generate a flat list of move values controlled by other DMs
            oDMmoves = list(movelists)
            focalDMmoves = oDMmoves.pop(dm)
            oDMmoves = [val for subl in oDMmoves for val in subl]   #flattening

            # translate the list of moves values for other DMs into a list of base states
            fixedStates = [0]
            for x in oDMmoves:
                fixedStates = [y+z for y in fixedStates for z in [0, x]]

            # translate the list of focal DM move values into a list of focal DM states
            focalStates = [0]
            for x in focalDMmoves:
                focalStates = [y+z for y in focalStates for z in [0, x]]

            # find the full set of mutually reachable states (controlled by the focal DM) for each fixed state (controlled by the other DMs)
            for x in fixedStates:
                reachable = [x]
                reachable = [y+z for y in reachable for z in focalStates]
                reachable = [y for y in reachable if (y in game.feasDec)]

                for state0 in reachable:
                    for state1 in reachable:
                        if state0 != state1:
                            focalReachMat[self.game.ordered[state0],self.game.ordered[state1]] =  game.payoffs[dm][state1]

        # Remove irreversible states ######################################################
            UseIrreversibles = True
            if UseIrreversibles:
                for move in game.irrev:
                    for state0 in game.feasDec:
                        # does state have potential for irreversible move?
                        state0bin = game.dec2bin(state0)     #DM's current state in binary form
                        c = state0bin[move[0]]                          # value of the irreversible move option in DMs current state

                        if c == move[1]:
                            for state1 in game.feasDec:
                                #does target move have irreversible move?
                                state1bin = game.dec2bin(state1)   # DM's target state in binary form
                                co = state1bin[move[0]]

                                if co != move[1]:
                         #remove irreversible moves from reachibility matrix
                                    focalReachMat[self.game.ordered[state0],self.game.ordered[state1]]= 0

    def reachable(self,dm,state):
        """Returns a list of all states reachable by dm from state.
        
        dm is the integer index of the decision maker.
        state is the integer representation of the state in decimal format.
        """
        stateO = self.game.ordered[state]
        reachVec = self.reachabilityMatrices[dm][stateO,:].flatten().tolist()
        reachVec = [x for x,y in enumerate(reachVec) if y != -1]
        reachVec = [self.game.expanded[x] for x in reachVec]
        return(reachVec)

    def UIs(self,dm,state,minPref=None):
        """Returns a list of a unilateral improvements available to dm from state
        
        dm is the integer index of the decision maker.
        state is the integer representation of the state in decimal format.
        minPref (optional) is a minimum preference for UIs to be returned. This
            is used to find moves that are preferred relative to some other
            initial state rather than the current one.  Used in SMR calculation.
        """
        stateO = self.game.ordered[state]
        UIvec = self.reachabilityMatrices[dm][stateO,:].flatten().tolist()

        if minPref is not None:
            UIvec = [i for i,x in enumerate(UIvec) if x>minPref]
        else:
            UIvec = [i for i,x in enumerate(UIvec) if x>self.game.payoffs[dm][state]]

        UIvec = [self.game.expanded[x] for x in UIvec]
        return(UIvec)

    def gameName(self):
        """extracts a guess at the game's name from the file name.
        
        Used in generating file names for data dumps (json or npz).
        """
        gameName = self.game.file[::-1]
        try:
            slashInd = gameName.index('/')
            gameName = gameName[:slashInd]
        except ValueError:
            pass

        return(gameName[::-1].strip('.gmcr'))

    def saveMatrices(self):
        """Export reachability matrix to numpy format."""
        np.savez("RMs_for_"+self.gameName(),*self.reachabilityMatrices)

    def saveJSON(self):
        """Export conflict data to JSON format for presentation.
        
        Includes:
        Nodes: state data,
        DMs: Decision Maker Names,
        options: option names,
        startNode: the first feasible state in the game
        """"
        nodes = {}
        dms = self.game.dmList
        options = self.game.getFlatOpts()
        startNode = self.game.getFeas('dec')[0]

        for stateDec,stateYN in zip(self.game.getFeas('dec'),
                                    self.game.getFeas('YN')):

            nodes[str(stateDec)] = ({'id':str(stateDec),'state':str(stateYN),
                          'ordered':str(self.game.ordered[stateDec]),
                          'reachable':[]})

            for dmInd,dm in enumerate(self.game.dmList):
                for rchSt in self.reachable(dmInd,stateDec):
                    nodes[str(stateDec)]['reachable'].append(
                        {'target':str(rchSt),
                         'dm': 'dm%s'%dmInd},
                         'payoff':self.game.payoffs[dmInd][rchSt]-self.game.payoffs[dmInd][stateDec])

        with open("networkfor_%s.json"%(self.gameName()),'w') as jsonfile:
            json.dump({"nodes":nodes,"DMs":dms,"options":options,
                       "startNode":startNode},jsonfile)


class LogicalSolver(RMGenerator):
    """Solves the games for equilibria, based on the logical definitions of stability concepts.
    
    """
    def __init__(self,game):
        RMGenerator.__init__(self,game)

    def chattyHelper(self,dm,state):
        """Used in generating narration for the verbose versions of the stability calculations"""
        a= 'state %s (decimal %s, payoff %s)' %(self.game.ordered[state],state,
                                                self.game.payoffs[dm][state])
        return a


        #Nash function
    def nash(self,dm,state):
        if not self.UIs(dm,state):
            narr = self.chattyHelper(dm,state)+' is Nash stable for dm '+ self.game.dmList[dm]+' since they have no UIs from this state.'
            return 1,narr
        else:
            narr = self.chattyHelper(dm,state)+' is NOT Nash stable for dm '+ self.game.dmList[dm]+' since they have UIs available to: '+','.join([self.chattyHelper(dm,state1) for state1 in self.UIs(dm,state)])
            return 0,narr


        #SEQ function
    def seq(self,dm,state):
        ui=self.UIs(dm,state)
        narr = ''

        if not ui:
            seqStab = 1      #stable since the dm has no UIs available
            narr += self.chattyHelper(dm,state)+' is SEQ stable since focal dm '+self.game.dmList[dm]+' has no UIs available.\n'
        else:
            for state1 in ui:             #for each potential move...
                oDMuis = [x for oDM in range(self.game.numDMs()) for x in self.UIs(oDM,state1) if oDM != dm]        #find all possible UIs available to other players
                if not oDMuis:
                    seqStab=0
                    narr += self.chattyHelper(dm,state)+' is unstable by SEQ for focal dm '+self.game.dmList[dm]+', since their opponents have no UIs from '+self.chattyHelper(dm,state1) + '\n'
                    return seqStab,narr
                else:
                    stable=0
                    for state2 in oDMuis:
                        if self.game.payoffs[dm][state2] <= self.game.payoffs[dm][state]:
                            stable = 1
                            narr += 'A move to '+self.chattyHelper(dm,state1)+' is SEQ sanctioned for focal dm '+self.game.dmList[dm]+' by a move to '+self.chattyHelper(dm,state2)+' by other dms.  check other focal dm UIs for sanctioning... \n'
                            break

                    if not stable:
                        seqStab=0
                        narr += self.chattyHelper(dm,state)+') is unstable by SEQ for focal dm '+self.game.dmList[dm]+', since their opponents have no less preferred sanctioning UIs from '+self.chattyHelper(dm,state1) + '\n'
                        return seqStab,narr

            seqStab = 1
            narr += self.chattyHelper(dm,state) + ' is stable by SEQ for focal dm '+self.game.dmList[dm]+', since all available UIs '+str(ui)+' are sanctioned by other players. \n'
        return seqStab,narr


        #SIM function
    def sim(self,dm,state):
        ui=self.UIs(dm,state)
        narr=''

        if not ui:
            simStab = 1      #stable since the dm has no UIs available
            narr += self.chattyHelper(dm,state)+' is SIM stable since focal dm '+self.game.dmList[dm]+' has no UIs available.\n'
        else:
            oDMuis = [x for oDM in range(self.game.numDMs()) for x in self.UIs(oDM,state) if oDM != dm]        #find all possible UIs available to other players from state
            if not oDMuis:
                simStab=0
                narr += self.chattyHelper(dm,state)+' is unstable by SIM for focal dm '+self.game.dmList[dm]+', since their opponents have no UIs from '+self.chattyHelper(dm,state) + '.\n'
                return simStab,narr
            else:
                for state1 in ui:
                    stable=0
                    for state2 in oDMuis:
                        if (state1+state2-state) in self.game.feasDec:
                            if self.game.payoffs[dm][state1+state2-state] <= self.game.payoffs[dm][state]:
                                stable = 1
                                narr += 'A move to '+self.chattyHelper(dm,state1)+' is SIM sanctioned for focal dm '+self.game.dmList[dm]+' by a move to '+self.chattyHelper(dm,state2)+' by other dms, which would give a final state of ' + self.chattyHelper(dm,(state1+state2-state)) + '.  check other focal dm UIs for sanctioning...\n'
                                break
                        else: narr += 'Simultaneous moves to ' + str(state1) + ' and ' + str(state2) + ' are not possible since the resultant state ' + str(state1+state2-state) + ' is infeasible.\n'

                    if not stable:
                        simStab=0
                        narr += self.chattyHelper(dm,state)+') is unstable by SIM for focal dm '+self.game.dmList[dm]+', since their opponents have no less preferred sanctioning UIs from '+self.chattyHelper(dm,state1) + '.\n'
                        return simStab,narr

            simStab = 1
            narr += self.chattyHelper(dm,state) + ' is stable by SIM for focal dm '+self.game.dmList[dm]+', since all available UIs '+str(ui)+' are sanctioned by other players.\n'
        return simStab,narr


        #GMR function
    def gmr(self,dm,state):
        ui=self.UIs(dm,state)
        narr=''

        if not ui:
            gmrStab = 1      #stable since the dm has no UIs available
            narr += self.chattyHelper(dm,state)+' is GMR stable since focal dm '+self.game.dmList[dm]+' has no UIs available.\n'
        else:
            for state1 in ui:             #for each potential move...
                oDMums = [x for oDM in range(self.game.numDMs()) for x in self.reachable(oDM,state1) if oDM != dm]        #find all possible moves (not just UIs) available to other players
                if not oDMums:
                    gmrStab=0
                    narr += self.chattyHelper(dm,state)+' is unstable by GMR for focal dm '+self.game.dmList[dm]+', since their opponents have no moves from '+self.chattyHelper(dm,state1) +'.\n'
                    return gmrStab,narr
                else:
                    stable=0
                    for state2 in oDMums:
                        if self.game.payoffs[dm][state2] <= self.game.payoffs[dm][state]:
                            stable = 1
                            narr += 'A move to '+self.chattyHelper(dm,state1)+' is GMR sanctioned for focal dm '+self.game.dmList[dm]+' by a move to '+self.chattyHelper(dm,state2)+' by other dms.  check other focal dm UIs for sanctioning...\n'
                            break

                    if not stable:
                        gmrStab=0
                        narr += self.chattyHelper(dm,state)+') is unstable by GMR for focal dm '+self.game.dmList[dm]+', since their opponents have no less preferred sanctioning UIs from '+self.chattyHelper(dm,state1) + '.\n'
                        return gmrStab,narr

            gmrStab = 1
            narr += self.chattyHelper(dm,state) + ' is stable by GMR for focal dm '+self.game.dmList[dm]+', since all available UIs '+str(ui)+'are sanctioned by other players.\n'
        return gmrStab,narr


        #SMR function
    def smr(self,dm,state):
        ui=self.UIs(dm,state)
        narr= ''

        if not ui:
            smrStab = 1      #stable since the dm has no UIs available
            narr += self.chattyHelper(dm,state)+' is SMR stable since focal dm '+self.game.dmList[dm]+' has no UIs available.\n'
        else:
            for state1 in ui:             #for each potential move...
                oDMums = [x for oDM in range(self.game.numDMs()) for x in self.reachable(oDM,state1) if oDM != dm]        #find all possible moves (not just UIs) available to other players

                if not oDMums:
                    smrStab=0
                    narr += self.chattyHelper(dm,state)+' is unstable by SMR for focal dm '+self.game.dmList[dm]+', since their opponents have no moves from '+self.chattyHelper(dm,state1) + '.\n'
                    return smrStab,narr
                else:
                    stable=0
                    for state2 in oDMums:
                        if self.game.payoffs[dm][state2] <= self.game.payoffs[dm][state]:     # if a sanctioning state exists...
                            narr += 'A move to '+self.chattyHelper(dm,state1)+' is SMR sanctioned for focal dm '+self.game.dmList[dm]+' by a move to '+self.chattyHelper(dm,state2)+' by other dms.  Check for focal dm countermoves...\n'
                            stable = 1
                            ui2 = self.UIs(dm,state2,self.game.payoffs[dm][state])         # Find list of moves available to the focal DM from 'state2' with a preference higher than 'state'

                            if ui2:     #still unstable since countermove is possible.  Check other sanctionings...
                                narr += '    The sanctioned state '+self.chattyHelper(dm,state2)+' can be countermoved to ' + str([self.chattyHelper(dm,state3) for state3 in self.UIs(dm,state2,self.game.payoffs[dm][state])])+'. Check other sanctionings...\n'
                                stable =0

                            else:        #'state' is stable since there is a sanctioning 'state2' that does not have a countermove
                                narr += '    '+self.chattyHelper(dm,state1)+' remains sanctioned under SMR for focal dm '+self.game.dmList[dm]+', since they cannot countermove their opponent\'s sanction to '+self.chattyHelper(dm,state2) + '.\n'
                                break

                    if not stable:
                        smrStab=0
                        narr += self.chattyHelper(dm,state)+') is unstable by SMR for focal dm '+self.game.dmList[dm]+', since their opponents have no less preferred sanctioning UIs from '+self.chattyHelper(dm,state1)+' that cannot be effectively countermoved by the focal dm.\n'
                        return smrStab,narr

            smrStab = 1
            narr += self.chattyHelper(dm,state) + ' is stable by SMR for focal dm '+self.game.dmList[dm]+', since all available UIs '+str(ui)+' are sanctioned by other players and cannot be countermoved.\n'
        return smrStab,narr

    def findEquilibria(self):
            #Nash calculation
        nashStabilities = np.zeros((self.game.numDMs(),2**self.game.numOpts()))
        for dm in range(self.game.numDMs()):
            for state in self.game.feasDec:
                nashStabilities[dm,state]= self.nash(dm,state)[0]

        np.invert(nashStabilities.astype('bool'),nashStabilities)
        self.nashEquilibria = np.invert(sum(nashStabilities,0).astype('bool'))


            #SEQ calculation
        seqStabilities = np.zeros((self.game.numDMs(),2**self.game.numOpts()))
        for dm in range(self.game.numDMs()):
            for state in self.game.feasDec:
                seqStabilities[dm,state]= self.seq(dm,state)[0]

        np.invert(seqStabilities.astype('bool'),seqStabilities)
        self.seqEquilibria = np.invert(sum(seqStabilities,0).astype('bool'))


            #SIM calculation
        simStabilities = np.zeros((self.game.numDMs(),2**self.game.numOpts()))
        for dm in range(self.game.numDMs()):
            for state in self.game.feasDec:
                simStabilities[dm,state] = self.sim(dm,state)[0]

        np.invert(simStabilities.astype('bool'),simStabilities)
        self.simEquilibria = np.invert(sum(simStabilities,0).astype('bool'))

            #SEQ + SIM calculation
        seqSimStabilities = np.bitwise_and(simStabilities.astype('bool'), seqStabilities.astype('bool'))
        self.seqSimEquilibria = np.invert(sum(seqSimStabilities,0).astype('bool'))

            #GMR calculation
        gmrStabilities = np.zeros((self.game.numDMs(),2**self.game.numOpts()))
        for dm in range(self.game.numDMs()):
            for state in self.game.feasDec:
                gmrStabilities[dm,state]=self.gmr(dm,state)[0]

        np.invert(gmrStabilities.astype('bool'),gmrStabilities)
        self.gmrEquilibria = np.invert(sum(gmrStabilities,0).astype('bool'))


            #SMR calculations
        smrStabilities = np.zeros((self.game.numDMs(),2**self.game.numOpts()))
        for dm in range(self.game.numDMs()):
            for state in self.game.feasDec:
                smrStabilities[dm,state]=self.smr(dm,state)[0]

        np.invert(smrStabilities.astype('bool'),smrStabilities)
        self.smrEquilibria = np.invert(sum(smrStabilities,0).astype('bool'))

        self.allEquilibria = np.vstack((self.nashEquilibria,
                                        self.gmrEquilibria,
                                        self.seqEquilibria,
                                        self.simEquilibria,
                                        self.seqSimEquilibria,
                                        self.smrEquilibria))


class InverseSolver(RMGenerator):
    def __init__(self,game):
        RMGenerator.__init__(self,game)

        self.desEq = self.game.desEq
        self.vary  = self.game.vary

    def _decPerm(self,full,vary):
        """Returns all possible permutations of a list 'full' when only the span
        defined by 'vary' is allowed to change. (UI vector for 1 DM)."""
        if not vary:
            yield full
        else:
            for x in itertools.permutations(full[vary[0]:vary[1]]):
                yield full[:vary[0]]+list(x)+full[vary[1]:]

    def prefPermGen(self,pref,vary):
        """Returns all possible permutations of the group of preference vectors
        'pref' when the spans defined in 'vary' are allowed to move for each DM."""
        b=[self._decPerm(y,vary[x]) for x,y in enumerate(pref)]
        c=itertools.product(*b)
        for y in c:
            yield y
            
    def nashCond(self):
        output=[""]
        for dm in range(self.game.numDMs()):
            desEq = self.game.ordered[self.desEq[0]]
            mblNash = [self.game.ordered[state] for state in self.mustBeLowerNash[0][dm]]
            message = "For DM %s: %s must be more preferred than %s"%(dm,desEq,mblNash)
            output.append(message)
        return "\n".join(output)
        
    def gmrCond(self):
        output=[""]
        for dm in range(self.game.numDMs()):
            desEq = self.game.ordered[self.desEq[0]]
            mblGMR = [self.game.ordered[state] for state in self.mustBeLowerNash[0][dm]]
            mbl2GMR = []
            for stateList in self.mustBeLowerGMR[0][dm]:
                mbl2GMR.extend(stateList)
            mbl2GMR = list(set(mbl2GMR))
            mbl2GMR = [self.game.ordered[state] for state in mbl2GMR] 
            message = "For DM %s: %s must be more preferred than %s, or at least one of %s must be less preferred than %s"%(dm,desEq,mblGMR,mbl2GMR,desEq)
            output.append(message)
        return "\n".join(output)
        

    def _mblInit(self):
        self.mustBeLowerNash = [[self.reachable(dm,state) for dm in range(self.game.numDMs())] for state in self.desEq]
        #mustBeLowerNash[state0][dm] contains the states that must be less preferred than 'state0' for 'dm'
        # to have a Nash equilibrium at 'state0'.

        self.mustBeLowerGMR = [[[[] for state1 in dm] for dm in state] for state in self.mustBeLowerNash]
        #mustBeLowerGMR[state0][dm][idx] contains the states that 'dm' could be sanctioned to after taking
        # the move in 'idx' from 'state0'. If, for each 'idx' there is at least one state less preferred
        # than 'state0', then 'state0' is GMR.  Sanctions are UMs for opponents, but not necessarily UIs.

        for x,state0 in enumerate(self.mustBeLowerNash):
            for y,dm in enumerate(state0):      #'dm' contains a list of reachable states for dm from 'state0'
                for z,state1 in enumerate(dm):
                    for dm2 in range(self.game.numDMs()):
                        if y != dm2:
                            self.mustBeLowerGMR[x][y][z]+= self.reachable(dm2,state1)

        #seq check uses same 'mustBeLower' as GMR, as sanctions are dependent on the UIs available to
        # opponents, and as such cannot be known until the preference vectors are set.

        self.mustBeLowerSMR = [[[[[] for idx in state1] for state1 in dm] for dm in state0] for state0 in self.mustBeLowerGMR]
        #mustBeLowerSMR[state0][dm][idx][idx2] contains the states that 'dm' could countermove to
        # if sanction 'idx2' was taken by opponents after 'dm' took move 'idx' from 'state0'.
        # if at least one state is more preferred that 'state0' for each 'idx2', then the state is
        # not SMR for 'dm'.

        for x,state0 in enumerate(self.mustBeLowerGMR):
            for y,dm in enumerate(state0):
                for z,idx in enumerate(dm): #idx contains a list of
                    self.mustBeLowerSMR[x][y][z] = [self.reachable(y,state2) for state2 in idx]


    def findEquilibria(self):
        self._mblInit()
        self.pVecs = list(self.prefPermGen(self.game.prefVec,self.vary))
        self.pVecsOrd = list(self.prefPermGen(self.game.prefVecOrd,self.vary))
        self.nash  = np.ones((len(self.pVecs),self.game.numDMs())).astype('bool')
        self.gmr   = np.zeros((len(self.pVecs),self.game.numDMs())).astype('bool')
        self.seq   = np.zeros((len(self.pVecs),self.game.numDMs())).astype('bool')
        self.smr   = np.zeros((len(self.pVecs),self.game.numDMs())).astype('bool')

        for prefsI,prefsX in enumerate(self.pVecs):
            payoffs =[[0]*(2**self.game.numOpts()) for x in range(self.game.numDMs())]

            for dm in range(self.game.numDMs()):
                for i,y in enumerate(prefsX[dm]):
                    try:
                        for z in y:
                            payoffs[dm][z] = self.game.numFeas - i
                    except TypeError:
                        payoffs[dm][y] = self.game.numFeas - i
            #check if Nash
            for dm in range(self.game.numDMs()):
                for state0p,state0d in enumerate(self.desEq):
                    if not self.nash[prefsI,dm]: break
                    pay0=payoffs[dm][state0d]        #payoff of the original state; higher is better
                    for pay1 in (payoffs[dm][state1] for state1 in self.mustBeLowerNash[state0p][dm]):    #get preferences of all states reachable by 'dm'
                        if pay0<pay1:       #prefs0>prefs1 means a UI exists
                            self.nash[prefsI,dm]=False
                            break

            #check if GMR
            self.gmr[prefsI,:]=self.nash[prefsI,:]

            for dm in range(self.game.numDMs()):
                if self.nash[prefsI,dm]:
                    continue
                for state0p,state0d in enumerate(self.desEq):
                    pay0=payoffs[dm][state0d]
                    for state1p,state1d in enumerate(self.mustBeLowerNash[state0p][dm]):
                        pay1 = payoffs[dm][state1d]
                        if pay0<pay1:   #if there is a UI available
                            #nash=False
                            self.gmr[prefsI,dm]=False
                            #print('%s is unstable by Nash, set dm %s gmr unstable'%(state0d,dm))
                            for pay2 in (payoffs[dm][state2] for state2 in self.mustBeLowerGMR[state0p][dm][state1p]):
                                if pay0>pay2:       #if initial state was preferred to sanctioned state
                                    self.gmr[prefsI,dm]=True
                                    break

            #check if SEQ
            mustBeLowerSEQ = [[[[] for state1 in dm] for dm in state] for state in self.mustBeLowerNash]

            for x,state0 in enumerate(self.mustBeLowerNash):
                for y,dm in enumerate(state0):
                    for z,state1 in enumerate(dm):
                        for dm2 in range(self.game.numDMs()):
                            if y != dm2:
                                mustBeLowerSEQ[x][y][z]+=[state2 for state2 in self.reachable(dm2,state1) if payoffs[dm2][state2]>payoffs[dm2][state1]]

            self.seq[prefsI,:]=self.nash[prefsI,:]

            for dm in range(self.game.numDMs()):
                if self.nash[prefsI,dm]:
                    continue
                for state0p,state0d in enumerate(self.desEq):
                    pay0=payoffs[dm][state0d]
                    for state1p,state1d in enumerate(self.mustBeLowerNash[state0p][dm]):
                        pay1 = payoffs[dm][state1d]
                        if pay0<pay1:  #if there is a UI available
                            #nash=False
                            self.seq[prefsI,dm]=False
                            #print('%s is unstable by Nash, set dm %s gmr unstable'%(state0d,dm))
                            for pay2 in (payoffs[dm][state2] for state2 in mustBeLowerSEQ[state0p][dm][state1p]):
                                if pay0>pay2:       #if initial state was preferred to sanctioned state
                                    self.seq[prefsI,dm]=True        #set to true since sanctioned, however this will be broken if another UI exists.
                                    break

            #check if SMR
            self.smr[prefsI,:]=self.nash[prefsI,:]

            for dm in range(self.game.numDMs()):
                if self.nash[prefsI,dm]:
                    continue
                for state0p,state0d in enumerate(self.desEq):
                    pay0=payoffs[dm][state0d]
                    for state1p,state1d in enumerate(self.mustBeLowerNash[state0p][dm]):
                        pay1 = payoffs[dm][state1d]
                        if pay0<pay1:   #if there is a UI available
                            #nash=False
                            self.smr[prefsI,dm]=False
                            for state2p,state2d in enumerate(self.mustBeLowerGMR[state0p][dm][state1p]):
                                pay2 = payoffs[dm][state2d]
                                if pay0>pay2:       #if initial state was preferred to sanctioned state
                                    self.smr[prefsI,dm]=True        #set to true since sanctioned, however this will be broken if another UI exists, or if dm can countermove.
                                    for pay3 in (payoffs[dm][state3] for state3 in self.mustBeLowerSMR[state0p][dm][state1p][state2p]):
                                        if pay0<pay3:       #if countermove is better than original state.
                                            self.smr[prefsI,dm]=False
                                            break
                                    break       #check this

        self.equilibriums = np.vstack((self.nash.all(axis=1),self.seq.all(axis=1),self.gmr.all(axis=1),self.smr.all(axis=1)))

    def filter(self,filt):
        values = []
        for pVeci,pVecOrd in enumerate(self.pVecsOrd):
            eqms = self.equilibriums[:,pVeci]
            if np.greater_equal(eqms,filt).all():
                values.append(tuple(list(pVecOrd)+[bool(x) for x in eqms]))
        counts = self.equilibriums.sum(axis=1)
        return values,counts


class MatrixCalc(RMGenerator):
    def __init__(self,game):
        RMGenerator.__init__(game)






def main():
    from data_01_conflictModel import ConflictModel
    g1 = ConflictModel('Prisoners.gmcr')

    rms = LogicalSolver(g1)


if __name__ == '__main__':
    main()
