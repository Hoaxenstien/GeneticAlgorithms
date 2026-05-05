import robby
#import numpy as np
from utils import *
import random
POSSIBLE_ACTIONS = ["MoveNorth", "MoveSouth", "MoveEast", "MoveWest", "StayPut", "PickUpCan", "MoveRandom"]
rw = robby.World(10, 10)
rw.graphicsOff()

def sortByFitness(genomes):
    tuples = [(fitness(g), g) for g in genomes]
    tuples.sort()
    sortedFitnessValues = [f for (f, g) in tuples]
    sortedGenomes = [g for (f, g) in tuples]
    return sortedGenomes, sortedFitnessValues


def randomGenome(length):
    """
    :param length:
    :return: string, random integers between 0 and 6 inclusive
    """
    return ''.join(str(random.randint(0, 6)) for _ in range(length))


def makePopulation(size, length):
    """
    :param size - of population:
    :param length - of genome
    :return: list of length size containing genomes of length length
    """
    return [randomGenome(length) for _ in range(size)]


def fitness(genome, steps=200, init=0.50, num_sessions=25):
    """
    :param genome: to test
    :param steps: number of steps in the cleaning session
    :param init: amount of cans
    :param num_sessions: number of sessions to average over
    :return: average total reward over num_sessions
    """
    if type(genome) is not str or len(genome) != 243:
        raise Exception("strategy is not a string of length 243")
    for char in genome:
        if char not in "0123456":
            raise Exception("strategy contains a bad character: '%s'" % char)
    totaReward = 0
    
    for session in range(num_sessions):
        rw.goto(0, 0)
        if type(init) in [int, float] and 0 <= init <= 1:
            rw.distributeCans(init)
        elif type(init) is str:
            rw.load(init)
        
        sessionReward = 0
        
        for step in range(steps):
            perceptCode = rw.getPerceptCode()
            actionIndex = int(genome[perceptCode])
            action = POSSIBLE_ACTIONS[actionIndex]
            reward = rw.performAction(action)
            session_reward += reward
        
        total_reward+= sessionReward
    
    return total_reward/num_sessions


def evaluateFitness(population):
    """
    :param population:
    :return: a pair of values: the average fitness of the population as a whole 
             and the fitness of the best individual in the population.
    """
    fitnesses = [fitness(g) for g in population]
    avgFitness = sum(fitnesses)/len(fitnesses)
    bestFitness = max(fitnesses)
    return avgFitness, bestFitness


def crossover(genome1, genome2):
    """
    :param genome1:
    :param genome2:
    :return: two new genomes produced by crossing over the given genomes at a random crossover point.
    """
    if len(genome1) != len(genome2):
        raise ValueError("Genomes must be the same length")
    
    crossoverPoint = random.randint(1, len(genome1) - 1)
    
    child1 = genome1[:crossoverPoint] + genome2[crossoverPoint:]
    child2 = genome2[:crossoverPoint] + genome1[crossoverPoint:]
    
    return child1, child2


def mutate(genome, mutationRate):
    """
    :param genome:
    :param mutationRate:
    :return: a new mutated version of the given genome.
    """
    mutated = list(genome)
    for i in range(len(mutated)):
        if random.random() < mutationRate:
            mutated[i] = str(random.randint(0, 6))
    return ''.join(mutated)


def selectPair(population):
    """
    :param population:
    :return: two genomes from the given population using rank selection.
    """
    sortedGenomes, sortedFitness = sortByFitness(population)
    
    ranks = list(range(1, len(population) + 1))
    
    parent1 = weightedChoice(sortedGenomes, ranks)
    parent2 = weightedChoice(sortedGenomes, ranks)
    
    return parent1, parent2


def runGA(populationSize, crossoverRate, mutationRate, logFile=""):
    """
    :param populationSize: :param crossoverRate: :param mutationRate: :param logFile: 
    :return: None
    """
    genomeLen = 243
    
    population = makePopulation(populationSize, genomeLen)
    
    outputFile = open("GAoutput.txt", "w")
    
    rw.graphicsOff("Running GA...")
    
    for generation in range(300):
        fitnesses = [fitness(g) for g in population]
        avgFitness = sum(fitnesses) / len(fitnesses)
        bestFitness = max(fitnesses)
        bestIndex = fitnesses.index(bestFitness)
        bestFtrategy = population[best_index]
        
        print(f"generation {generation}: average fitness {avgFitness}, best fitness {bestFitness}")
        
        if generation % 10 == 0:
            outputFile.write(f"{generation} {avgFitness} {bestFitness} {best_strategy}")
            outputFile.flush()
            
        
        fitnessPairs = list(zip(fitnesses, population))
        fitnessPairs.sort(reverse=True)
        
        newPop = [fitnessPairs[0][1], fitnessPairs[1][1]]
        
        while len(newPop) < populationSize:
            parent1, parent2 = selectPair(population)
            
            if random.random() < crossoverRate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            child1 = mutate(child1, mutationRate)
            child2 = mutate(child2, mutationRate)
            
            newPop.append(child1)
            if len(newPop) < populationSize:
                newPop.append(child2)
        
        population = newPop
    
    outputFile.close()
    
    finalFitness = [fitness(g) for g in population]
    bestIndex= finalFitness.index(max(finalFitness))
    bestStrategy = population[bestIndex]
    
    with open("bestStrategy.txt", "w") as f:
        f.write(bestStrategy)
    
    print(f"\nBest strategy saved to bestStrategy.txt")
    print(f"Best strategy fitness: {max(finalFitness):.2f}")
    
    return None


def test_FitnessFunction():
    f = fitness(rw.strategyM)
    print("Fitness for StrategyM : {0}".format(f))

#test_FitnessFunction()

#runGA(100, 1.0, 0.05)