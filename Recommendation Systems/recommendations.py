from math import sqrt
from scipy.stats.stats import pearsonr

# A dictionary of movie critics and their ratings of a small
# set of movies
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
'The Night Listener': 4.5, 'Superman Returns': 4.0,
'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0},
'Larry': {'Snakes on a Plane':4.5, 'You, Me and Dupree':1.0,'Superman Returns':4.0}}


def sim_distance(prefs, person1, person2):
    """
    Returns a distance-based similarity score for person1 and person2
    """

    # Get the list of shared items
    shared_items = {}

    for item in prefs[person1]:
        if item in prefs[person2]:
            shared_items[item] = 1

    # If they have no items in common return 0
    if len(shared_items) == 0:
        return 0

    # Add up the squares of all the differences for similar movies
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in prefs[person1] if item in prefs[person2]])

def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    shared_items = {}

    for item in prefs[p1]:
        if item in prefs[p2]: shared_items[item] = 1

    # Number of shared items
    n = len(shared_items)

    # If there are no ratings in common, return 0
    if n == 0: return 0

    n = float(n)

    # Add up all the preferences
    x = [prefs[p1][it] for it in shared_items]
    y = [prefs[p2][it] for it in shared_items]

    sum1 = sum(x)
    sum2 = sum(y)

    print pearsonr(x, y)

    # Sum up the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in shared_items])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in shared_items])

    # Sum up the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in shared_items])

    # Calculate Pearson score
    num = pSum - (sum1 * sum2/n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))

    r = num / den

    return r

def sim_pearson_mine(prefs, p1, p2):
    """
    My version of pearson's coefficient calculation routine using
    the formula I'm familiar with
    """
    shared_items = {}

    for item in prefs[p1]:
        if item in prefs[p2]: shared_items[item] = 1

    # Number of shared items
    n = len(shared_items)

    # If there are no ratings in common, return 0
    if n == 0: return 0

    n = float(n)

    # Read preferences into corresponding lists
    x = [prefs[p1][it] for it in shared_items]
    y = [prefs[p2][it] for it in shared_items]

    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_sq = sum([pow(i, 2) for i in x])
    sum_y_sq = sum([pow(i, 2) for i in y])
    products = [a * b for (a,b) in zip(x,y)]
    sum_products = sum(products)

    mean_x = sum_x / n
    mean_y = sum_y / n

    num = sum_products - (n * mean_x * mean_y)
    den = sqrt(sum_x_sq - (n * pow(mean_x, 2))) * sqrt(sum_y_sq - (n * pow(mean_y, 2)))

    return num / den

def top_matches(prefs, person, n = 5, similarity = sim_pearson):
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]

    # Sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]

def get_recommendations(prefs, person, similarity=sim_pearson):
    """
    Get recommendations for a person by using a weighted average of every
    other user's rankings
    """
    totals = {}
    sim_sums = {}

    for other in prefs:
        if other == person: continue

        sim = similarity(prefs, person, other)

        # ignore scores of 0 or lower
        if sim <= 0: continue

        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # similarity * score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                # sum of similarities
                sim_sums.setdefault(item, 0)
                sim_sums[item] += sim

        # Create the normalized list
        rankings = [(total / sim_sums[item], item) for item, total in totals.items()]

        # Return the sorted list
        rankings.sort()
        rankings.reverse()
        return rankings

def transform_prefs(prefs):
    """
    Switch keys and values in the dictionary storing data for recommendation system
    """

    result = {}

    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            result[item][person] = prefs[person][item]

    return result


#print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')
#print sim_pearson_mine(critics, 'Lisa Rose', 'Gene Seymour')
#print top_matches(critics, 'Larry', n = 2)
print get_recommendations(critics, 'Larry')
movies =  transform_prefs(critics)
print top_matches(movies, 'Superman Returns')