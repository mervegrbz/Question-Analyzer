# -*- coding: utf-8 -*-

import re
from question import *

# init conf scores
nedirFC = 0
verilirFC = 0
denirFC = 0
hangisidirFC = 0
hangiBtwFC = 0
neKadardirFC = 0
genericFC = 0
kacFC = 0
nezamanFC = 0
yuzdekacFC = 0
kactirFC = 0

nedirMC = 0
verilirMC = 0
denirMC = 0
hangisidirMC = 0
hangiBtwMC = 0
neKadardirMC = 0
genericMC = 0
kacMC = 0
nezamanMC = 0
yuzdekacMC = 0
kactirMC = 0

def kactirExpert(qObj, qParts):
    qFocus = []

    SENTENCE = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    SUBJlist = QPart.getAllPartsWithField(qParts, 'depenTag', 'SUBJECT')

    if SUBJlist == []:
        SUBJ = False
    else:
        SUBJ = SUBJlist[len(SUBJlist)-1]

        SUBJclass = qObj.findChildrenDepenTag(SUBJ, 'CLASSIFIER')

        qFocus = SUBJclass

        qFocus.append(SUBJ)

    # see if there is an object as well
    OBJlist = qObj.findChildrenDepenTag(SENTENCE, 'OBJECT')

    if OBJlist != []:
        OBJ = OBJlist[0]

        OBJclass = qObj.findChildrenDepenTag(OBJ, 'CLASSIFIER')
        
        qFocus.extend(OBJclass)
        qFocus.append(OBJ)

    return qFocus, [], kactirFC, kactirMC, "kactir"

def yuzdeKacExpert(qObj, qParts):

    SUBJlist = QPart.getAllPartsWithField(qParts, 'depenTag', 'SUBJECT')

    if SUBJlist == []:
        SUBJ = False
    else:
        SUBJ = SUBJlist[len(SUBJlist)-1]

    subjChildren = qObj.findChildren(SUBJ)

    subjChildren.append(SUBJ)

    YUZDE = QPart.getQPartWithField(qParts, 'text', 'yüzde')

    subjChildren.append(YUZDE)

    return subjChildren, [], yuzdekacFC, yuzdekacMC, "yuzde kac"

def neZamanExpert(question, qParts):

    qFocus = []

    qList = question.questionText.split(' ')

    neIndex = qList.index('ne')

    fWords = qList[neIndex:len(qList)]

    for word in fWords:
        qFocus.append(QPart.getQPartWithField(qParts, 'text', word))

    """
    NE = QPart.getQPartWithField(qParts, 'text', 'ne')
    ZAMAN = QPart.getQPartWithField(qParts, 'text', 'zaman')

    SENTENCE = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')
    
    qFocus = [NE, ZAMAN, SENTENCE]
    """
    return qFocus, [], nezamanFC, nezamanMC, "ne zaman"

def kacExpert(question, qParts):

    qFocus = []
    KAC = None
    for part in question.questionParts:
        if QPart.getPartField(part, 'text').lower() == 'kaç'.decode('utf-8'):
            KAC = part
            break

    if KAC == None:
        return [], [], kacFC, kacMC, "kac"

    
    parents = question.findParent(KAC)
    parentPart = None
    if parents != []:
        parentPart = parents[0]

    SENTENCE = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    # 1) if parent is a DERIV of a SENTENCE, take KAC and SENTENCE
    isOne = False
    if parentPart != None and QPart.getPartField(parentPart,'depenTag') == 'DERIV':
        if QPart.getPartField(question.findParent(parentPart)[0], 'depenTag') == 'SENTENCE':
            isOne = True

    if isOne:
        qFocus = [SENTENCE, KAC]
    # 2) if the parent is a SUBJET, take KAC and SUBJECT and LOCATIVE.ADJUNCT of SENTENCE
    elif parentPart != None and QPart.getPartField(parentPart, 'depenTag') == 'SUBJECT':
        senChildren = question.findChildrenDepenTag(SENTENCE, 'LOCATIVE.ADJUNCT')
        if senChildren != []:
            qFocus = [senChildren[len(senChildren)-1]]
        qFocus.extend([parentPart, KAC])
    # 3) else, look for a subject on the branch
    else:
        branch = question.traceForwardFrom(KAC)

        hasSubject = False
        untilSubject = [KAC]
        for part in branch:
            
            if QPart.getPartField(part, 'depenTag') == 'SUBJECT':
                hasSubject = True

                tamChildren = question.findChildrenDepenTag(part, 'CLASSIFIER')
                tamChildren.extend(question.findChildrenDepenTag(part, 'POSSESSOR'))

                untilSubject.extend([prt for prt in tamChildren if (prt not in branch and QPart.getPartField(prt, 'depenTag') != 'DERIV')])
                untilSubject.append(part)

                break
            else:
                untilSubject.append(part)

        if hasSubject:
            return untilSubject, [], kacFC, kacMC, "kac"
            #print(QPart.getPartField(part, 'depenTag'))

    if qFocus == []:
        # if we get here, then we have nothing to do with SUBJECT
        # grab the whole part from kac to sentence
        forwTrace = question.traceForwardFrom(KAC)
        for part in reversed(forwTrace):
            tag = QPart.getPartField(part, 'depenTag')
            if  tag != 'DERIV' and tag != 'COORDINATION':
                qFocus.append(part)
        qFocus.append(KAC)
        
                


    qFocus.reverse()
    return qFocus, [], kacFC, kacMC, "kac"

def nedirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

    qFocus = []
    qMods = []

    SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
    """
    we know that everyone in 'nedir' has subjects
    but nevertheless
    """
    if not SUBJ:
        return [], [], nedirFC, nedirMC, "nedir"
    else:
        
        """ FOCUS EXTRACTION """

        qFocus = [SUBJ]

        """ we find the possessors and classifiers among the children of the subject"""
        subjChildren = question.findChildren(SUBJ)

        possAndClassifierChildren = question.findChildrenDepenTag(SUBJ, 'POSSESSOR')
        possAndClassifierChildren.extend(question.findChildrenDepenTag(SUBJ, 'CLASSIFIER'))

        """ register the focus parts"""
        for cpChild in possAndClassifierChildren:
            qFocus.append(cpChild)
            qFocus.extend(question.tracebackFromFoldTamlama(cpChild))

        """ MOD EXTRACTION """

        """ don't need the modifiers of the subject, it's also a part of the focus"""
        modChildren = []

        """extend the modChildren with the modifier children of the focus parts """
        for focusPart in qFocus:
            modChildren.extend(question.findChildrenDepenTag(focusPart, 'MODIFIER'))

        """ register the final mod parts"""
        modChildren.reverse()
        for modChild in modChildren:
            qMods.append(modChild)
            qMods.extend(question.tracebackFrom(modChild))
            
        """special hack for parts like 'Türkiyeden'"""
        subjects = QPart.getAllPartsWithField(qParts, 'depenTag', 'SUBJECT')
        if len(subjects) > 1:
            for subj in subjects:
                subjText = QPart.getPartField(subj, 'text')

                compl = re.compile(ur"Türkiye", re.UNICODE)

                if compl.search(subjText) != None:
                    qMods.append(subj)

        qFocus.reverse()
        qMods.reverse()
        return qFocus, qMods, nedirFC, nedirMC, "nedir"


def verilirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

    qFocus = []
    qMods = []

    SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    
    """ FOCUS EXTRACTION """

    """ 
    Assumptions: 

    -- every 'verilir' question has DATIVE.ADJUNCT

    -- if a DATIVE.ADJUNCT has more than one MODIFIER, the last one is its classifier
    """

    childrenTmp = question.findChildrenDepenTag(SEN, 'DATIVE.ADJUNCT')

    if childrenTmp == []:
        return [], [], verilirFC, verilirMC, "verilir"
    else:
        DativeADJ = childrenTmp[0]

    qFocus.extend([SUBJ, DativeADJ])

    focusChildren = question.findChildrenDepenTag(DativeADJ, 'POSSESSOR')
    focusChildren.extend(question.findChildrenDepenTag(DativeADJ, 'CLASSIFIER'))

    dativeModChildren = question.findChildrenDepenTag(DativeADJ, 'MODIFIER')
    dativeModChildren.extend(question.findChildrenDepenTag(DativeADJ, 'POSSESSOR'))
    dativeModChildren.extend(question.findChildrenDepenTag(DativeADJ, 'CLASSIFIER'))
                             
    numFocusChildren = len(focusChildren)

    numOfModChildren = len(dativeModChildren)



    if numOfModChildren > 1:
        """ we take (and remove) the last modifier"""
        #focusChild = focusChildren.pop(numFocusChildren-1)
        
        focusChild = dativeModChildren[numOfModChildren-1]

        childTag = QPart.getPartField(focusChild, 'depenTag')

        if childTag != 'MODIFIER':
            focusChild = dativeModChildren.pop(numOfModChildren-1)
            qFocus.append(focusChild)
            qFocus.extend(question.tracebackFrom(focusChild))
        
    elif numOfModChildren == 1:
        childTag = QPart.getPartField(dativeModChildren[0], 'depenTag')
        if childTag == 'POSSESSOR' or childTag == 'CLASSIFIER':
            fChild = dativeModChildren.pop(0)
            qFocus.append(fChild)
            qFocus.extend(question.tracebackFromFoldTamlama(fChild, includePOSS=True, includeCLASS=True))
            
            modCandidates = question.tracebackFrom(fChild)
            for candy in modCandidates:
                if candy not in qFocus:
                    qMods.append(candy)
                    qMods.extend(question.tracebackFrom(candy))
    """ MOD EXTRACTION """

    if dativeModChildren != []:
        dativeModChildren.reverse()
        for modChild in dativeModChildren:
            qMods.append(modChild)
            qMods.extend(question.tracebackFrom(modChild))

    qFocus.reverse()
    qMods.reverse()
    return qFocus, qMods, verilirFC, verilirMC, "verilir"


def denirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    """ FOCUS EXTRACTION """

    """ FALSE Assumption: every 'denir' has a dative.adjunct """

    DativeADJchildren = question.findChildrenDepenTag(SEN, 'DATIVE.ADJUNCT')

    if DativeADJchildren == []:
        return [], [], denirFC, denirMC, "denir"

    """ Assumption: if it has more than one dative.adjunct, the last one (the closests to the SENTENCE) is most likely the correct one"""

    DativeADJ = DativeADJchildren[len(DativeADJchildren)-1]

    qFocus = [SEN, DativeADJ]
    qFocus.extend(question.tracebackFromFoldTamlama(DativeADJ, True, True, False, False, True))

    """ MOD EXTRACTION """

    """ dump all children of focus parts """

    for fPart in qFocus:
        children = question.findChildren(fPart)
        
        for child in children:

            childPartsDummy = question.tracebackFrom(child)
            childParts = question.tracebackFrom(child)

            for cPart in childPartsDummy:
                if (cPart in qFocus) or (cPart in qMods):
                    childParts.remove(cPart)

            qMods.extend(childParts)

    qFocus.reverse()
    qMods.reverse()
    return qFocus, qMods, denirFC, denirMC, "denir"


def hangisidirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):
    
    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    subjChildren = question.findChildrenDepenTag(SEN, 'SUBJECT')

    if len(subjChildren)<=0:
        """ this will get the subject which is nearest to the sentence """
        SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
        if not SUBJ:
            return [], [], hangisidirFC, hangisidirMC, "hangisidir"
    else:
        SUBJ = subjChildren[len(subjChildren)-1]


    """ FOCUS EXTRACTION """

    qFocus.append(SUBJ)
    qFocus.extend(question.tracebackFromFoldTamlama(SUBJ))
    
    """ MOD EXTRACTION """    

    modChildren = []
    
    """extend the modChildren with the modifier children of the focus parts """
    for focusPart in qFocus:
        modChildren.extend(question.findChildrenDepenTag(focusPart, 'MODIFIER'))

    """ register the final mod parts"""
    modChildren.reverse()
    for modChild in modChildren:
        qMods.append(modChild)
        qMods.extend(question.tracebackFrom(modChild))

        
    """special hack for parts like 'Türkiyeden'"""
    subjects = QPart.getAllPartsWithField(qParts, 'depenTag', 'SUBJECT')
    if len(subjects) > 1:
        for subj in subjects:
            subjText = QPart.getPartField(subj, 'text')

            compl = re.compile(ur"Türkiye", re.UNICODE)

            if compl.search(subjText) != None:
                qMods.append(subj)

    qFocus.reverse()
    qMods.reverse()
    return qFocus, qMods, hangisidirFC, hangisidirMC, "hangisidir"



def hangiBtwExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

    qFocus = []
    qMods = []

    hangiParts = QPart.getAllPartsWithField(qParts, 'text', 'hangi')

    """ eliminate the hangi parts which are DERIV """
    hangiFiltered=[ part for part in hangiParts if (QPart.getPartField(part, 'depenTag') != 'DERIV')]

    if len(hangiFiltered) != 1:
        raise RuntimeError("Confused with this question: " + question.questionText)

    HANGI = hangiFiltered[0]

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')


    """ FOCUS EXTRACTION """

    qFocus = [HANGI]

    """ BEWARE: this part is highly mutative! """

    """ we first concentrate on hangiParent """
    hangiParent = question.findParent(HANGI)[0]

    """ UPWARDS TOWARDS SENTENCE """
    if QPart.getPartField(hangiParent, 'depenTag') == 'DERIV':
        while True:
            hangiParent = question.findParent(hangiParent)[0]
            if QPart.getPartField(hangiParent, 'depenTag') != 'DERIV':
                break

    if len(question.findChildren(hangiParent)) > 1:
        allChildren = question.tracebackFromFoldTamlama(hangiParent, True, True, True, False)
        """ eliminate child parts that are in focus"""
        for child in allChildren:
            if child in qFocus:
                allChildren.remove(child)
                continue

        qFocus.extend(allChildren)

    qFocus.append(hangiParent)

    if QPart.getPartField(hangiParent, 'depenTag') == 'CLASSIFIER':
        qFocus.extend(question.traceForwardFromFoldTamlama(hangiParent, True, True, False, True))
    else:
        qFocus.extend(question.traceForwardFromFoldTamlama(hangiParent, False, False, True, False))

    

   
    """ MOD EXTRACTION """

    """ Tricky...

    there are USUALLY 2 kinds of mods here:
    1) modifier of HANGI --- en çok hangi ...
    2) subjects, adjuncts and other modifiers attached to SENTENCE

    TODO 3) How about modifiers of focus parts other than HANGI -> ... hangi nadide ilin ....

    we dump all (2), then traverse upwards from HANGI for (1), then (3)
    """
    senChildrenDummy = question.findChildren(SEN)
    senChildren = question.findChildren(SEN)

    for child in senChildrenDummy:
        if QPart.getPartField(child, 'depenTag') == 'DERIV':
            senChildren.remove(child)
            senChildren.extend(question.findChildren(child))
            
    for child in senChildren:
        if child not in qFocus:
            modCandidates = question.tracebackFrom(child)
            
            """ excluding the parts before HANGI, in branch ...."""
            isHangiThere = False

            for mod in modCandidates:
                if QPart.getPartField(mod, 'text') == 'hangi':
                    isHangiThere = True
            """ .... that has HANGI in it. So: 

            if HANGI is not there, include the branch"""
            if (not isHangiThere):
                modBranch = question.tracebackFrom(child)
                modBranch.reverse()
                modBranch.append(child)

                qMods.extend(modBranch)

    hangiMods = question.tracebackFromFoldTamlama(HANGI, False, False, True)
    hangiMods.reverse()
    qMods.extend(hangiMods)

    """ Also, if SENTENCE is not included in Focus, include it at the end of qMods"""
    if QPart.getPartField(qFocus[len(qFocus)-1], 'depenTag') != 'SENTENCE':
        qMods.append(SEN)
    
    return qFocus, qMods, hangiBtwFC, hangiBtwMC, "hangi"


def neKadardirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):
    
    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    NE = False
    for derivChild in question.findChildrenDepenTag(SEN, 'DERIV'):
        for neChild in question.findChildrenDepenTag(derivChild, 'OBJECT'):
            NE = neChild
            break

    if not NE:
        raise RuntimeError('neKadardirExpert : there is no NE part')

    qFocus = [SEN, NE]

    # If sentence has an OBJECT child, we take the rightmost one
    # and take OBJECT and its classifier if it has one

    objChildren = question.findChildrenDepenTag(SEN, 'OBJECT')
    objLen = len(objChildren)

    if objLen != 0:
        OBJ = objChildren[objLen-1]
        qFocus.append(OBJ)
        qFocus.extend(question.tracebackFromFoldTamlama(OBJ, False, True, False, False, False))

    else:
        # else if sentence has a SUBJECT child, we take the rightmost one
        # and take it and its classifier if it has one

        subjChildren = question.findChildrenDepenTag(SEN, 'SUBJECT')
        subjLen = len(subjChildren)

        if subjLen != 0:
            SUBJ = subjChildren[subjLen-1]
            qFocus.append(SUBJ)
            qFocus.extend(question.tracebackFromFoldTamlama(SUBJ, False, True, False, False, False))

        else:
            return [], [], neKadardirFC, neKadardirMC, "kadar"

    qFocus.reverse()
    qMods.reverse()
    return qFocus, qMods, neKadardirFC, neKadardirMC, "kadar"

def genericExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):
    
    # just grab the sentence and look for the subject, traceback with
    # possessor and classifier chain



    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    qFocus = [SEN]

    subjChildren = question.findChildrenDepenTag(SEN, 'SUBJECT')

    for subjChild in subjChildren:
        qFocus.append(subjChild)
        qFocus.extend(question.tracebackFromFoldTamlama(subjChild, True, True, False, False, False))

    return qFocus, [], genericFC, genericMC, "generic"
