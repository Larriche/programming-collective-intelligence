import time
import random
import math

def getminutes(t):
    """
    Get the number of minutes a given time spans
    """
    x = time.strptime(t, '%H:%M')
    return x[3]*60 + x[4]

def printschedule(r):
    for d in range(len(r)/2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[d]]
        ret = flights[(destination, origin)][r[d+1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2],
            ret[0], ret[1], ret[2])

def schedulecost(sol):
    totalprice = 0
    lastestarrival = 0
    earliestdep = 24 * 60

    for d in range(len(sol)/2):
        # Get the inbound and outbound flights
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d+1])]

        # Total price is the price of all outbound and return flights
        totalprice += outbound[2]
        totalprice += returnf[2]

        # Track the latest arrival and earliest departure
        if lastestarrival < getminutes(outbound[1]): latestarrival = getminutes(outbound[1])

        if earliestdep > getminutes(returnf[0]): earliestdep = getminutes(returnf[0])

    # Every person must wait at the airport until the latest person arrives
    # They also must arrive at the same time and wait for their flight
    totalwait = 0

    for d in range(len(sol)/2):
        origin = people[d][1]
        outbound=flights[(origin,destination)][int(sol[d])]
        returnf=flights[(destination, origin)][int(sol[d+1])]
        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep

    # Does this solution require an extra day of car rental? That'll be $50!
    if latestarrival > earliestdep: totalprice += 50

    return totalprice + totalwait

def randomoptimize(domain, costf):
    """
    Generates random solutions and evaluate their cost
    Returns best solution after 1000 guesses
    """
    best = 999999999
    bestr = None

    for i in range(1000):
        # Create a random solution
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

        # Get the cost
        cost = costf(r)

        # Compare it to the best one so far
        if cost < best:
            best = cost
            bestr = r

    return bestr

def hillclimb(domain, costf):
    """
    Uses a hillclimbing approach to looking for a solution
    """
    # Create a random solution
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

    # Main loop
    while 1:
        # Create list of neighbouring solutions
        neighbours = []

        for j in range(len(domain)):
            # One way in each direction
            if sol[j] > domain[j][0]:
                neighbours.append(sol[0:j] + [sol[j] + 1] + sol[j+1:])
            if sol[j] < domain[j][1]:
                neighbours.append(sol[0:j] + [sol[j] - 1] + sol[j+1:])

        # See what the best solution amongst the neighbours is
        current = costf(sol)
        best = current

        for j in range(len(neighbours)):
            cost = costf(neighbours[j])
            if cost < best:
                best = cost
                sol = neighbours[j]

        # If there is no improvement, then we've reached the top
        if best == current:
            break

        return sol

people = [('Seymour', 'BOS'),
    ('Franny', 'DAL'),
    ('Zooey', 'CAK'),
    ('Walt', 'MIA'),
    ('Buddy', 'ORD'),
    ('Les', 'OMA')]

destination = 'LGA'

flights = {}

for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    flights[(origin, dest)].append((depart, arrive, int(price)))


domain = [(0,8)] * (len(people) * 2)
s = randomoptimize(domain, schedulecost)
print schedulecost(s)

s = hillclimb(domain, schedulecost)
print schedulecost(s)