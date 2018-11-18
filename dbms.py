from itertools import combinations
from helpers import every
from helpers import some
from helpers import first

class FunctionalDependencySet:

    def __init__(self, iterable = []):
        self.__items__ = set( (lhs,rhs) for lhs, rhs in map(lambda x: x.split('->'), iterable) )

    def __len__(self):
        return len(self.__items__)

    def __iter__(self):
        return iter(self.__items__)
    
    def add(self, lhs, rhs):
        self.__items__.add((lhs,rhs))

    def remove(self, lhs, rhs):
        self.__items__.remove((lhs, rhs))

    def replaceItems(self, newItems):
        self.__items__ = newItems

    def leftSideSet(self):
        return set(lhs for lhs, rhs in self.__items__)
    
    def rightSideSet(self):
        return set(rhs for lhs, rhs in self.__items__)

    def closureSet(self, attributes):
        closure = set(attributes)

        for _ in range(0, len(self.__items__)):
            for lhs, rhs in self.__items__:
                if set(lhs).issubset(closure): 
                    closure.update(rhs)

        return closure

    def toString(self):
        return "FD = {\n\t" + "\n\t".join([ " -> ".join(item) for item in self.__items__]) + "\n}"

class Relation:
    def __init__(self, attributes, fdSet = FunctionalDependencySet() ):
        self.__attributes__ = set(attributes)
        self.fdSet = fdSet

    def attributes(self):
        return self.__attributes__

    def closureSet(self, attributes):
        return self.fdSet.closureSet(attributes)

    def validKey(self, attribute):
        return self.closureSet(attribute) == self.__attributes__

    def candidateKeys(self):
        keys = []
        for i in range(1, len(self.__attributes__)+1):
            # Generate possible combinations and filter out the super sets of existing candidate Keys
            possibilities = [ item for item in combinations(self.__attributes__, i) if not len(keys) or every(keys, lambda key: not set(key).issubset(item))]
            # add to candidate Keys if it is a valid Key in relation
            keys += [item for item in possibilities if self.validKey(item) ]

        return keys

    def toString(self):
        return "R(" + ", ".join(self.__attributes__) + "):\n" + self.fdSet.toString()

def cover(fd1, fd2):
    return every( lambda item: fd1.closureSet(item).issubset(fd2.closureSet(item)), fd1.leftSideSet() )

def equivalence(fd1,fd2):
    return cover(fd1,fd2) and cover(fd2,fd1)

def isPartialDependency(fdItem, candidates, nonPrimes):
    lhs, rhs = fdItem

    if( not set(rhs).intersection(nonPrimes) ):
        return False

    return some( 
        candidates, 
        lambda key: not(set(key) == set(lhs)) and set(lhs).intersection(key) 
    )

def hasPartialDependency(relation):
    candidates = relation.candidateKeys()
    primes = set( attr for key in candidates for attr in key)
    nonPrimes = relation.attributes().difference(primes)

    return some(
        relation.fdSet, 
        lambda fdItem: isPartialDependency(fdItem, candidates, nonPrimes) 
    )

def isFirstNF(relation):
    return True

def isSecondNF(relation): 
    return isFirstNF(relation) and not hasPartialDependency(relation)

def isThirdNF(relation):
    primes = set( attr for key in relation.candidateKeys() for attr in key)

    if(not isSecondNF(relation)):
        return False

    return every(
        relation.fdSet, 
        lambda fdItem: set(fdItem[1]).issubset(fdItem[0]) or relation.validKey(fdItem[0]) or set(fdItem[1]).issubset(primes) 
    )

def isBCNF(relation):
    if(not isThirdNF(relation)):
        return False

    return every(relation.fdSet.leftSideSet(), lambda lhs: relation.validKey(lhs) )

def minimalCover(fdSet):
    #Split the dependencies
    fdSet.replaceItems(
        set((lhs,attr) for lhs, rhs in fdSet for attr in rhs)
    ) 
    
    #Reduce Right side
    for lhs, rhs in list(fdSet):
        fdSet.remove(lhs,rhs)
        if  not set(rhs).issubset(fdSet.closureSet(lhs)):
            fdSet.add(lhs,rhs)

    #Reduce Left side
    compositeLhsFds = [ (lhs,rhs) for lhs,rhs in fdSet if len(lhs) > 1 ]
    for lhs, rhs in compositeLhsFds:
        lhsClosure = fdSet.closureSet(lhs)
        fdSet.remove(lhs,rhs)
        lhs = first(lhs, lambda attr: lhsClosure == fdSet.closureSet(attr))
        fdSet.add(lhs,rhs)

    return fdSet
