import random
from math import sqrt
from PIL import Image, ImageDraw

class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

def read_file(filename):
    """
    Read the contents of the data fie
    """
    lines = [line for line in file(filename)]

    # First line is the column titles
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []

    for line in lines[1:]:
        row = line.strip().split('\t')

        # First column in each row is the rowname
        rownames.append(row[0])

        # The data for this row is the remainder of the row
        data.append([float(x) for x in row[1:]])

    return rownames, colnames, data

def pearson(v1, v2):
    """
    Calculate the Pearson's correlation score for two blogs given their data
    """
    # Simple sums
    sum1 = sum(v1)
    sum2 = sum(v2)

    # Sums of the squares
    sum1_sq = sum([pow(v, 2) for v in v1])
    sum2_sq = sum([pow(v, 2) for v in v2])

    # Sum of the products
    product_sum = sum([a * b for (a, b) in zip(v1, v2)])

    # Calculate r (Pearson score)
    num = product_sum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1_sq - pow(sum1, 2) / len(v1)) * (sum2_sq - pow(sum2, 2) / len(v1)))

    if den == 0: return 0

    return 1.0 - num/den

def tanimoto(v1, v2):
    """
    Calculate the Tanimoto coefficient for two rows of data

    The formula for tanimoto coefficient = Nc / (Na + Nb - Nc)

    where in our case,
          Na = Number of items in row A (a set of non-zero values in v1)
          Nb = Number of items in row B (a set of non-zero values in v2)
          Nc = Number of items in C (a set of values where non-zero values occurred for both v1 and v2 in
              a given column)
    """
    lenA = 0
    lenB = 0
    lenC = 0

    for i in range(len(v1)):
        if v1[i] != 0:
            lenA += 1

        if v2[i] != 0:
            lenB += 1

        if (v1[i] != 0) and (v2[i] != 0):
            lenC += 1

    coefficient = float(lenC) / (lenA + lenB - lenC)

    # higher coefficients represent more similarity but we need smaller values for distance
    # so we return 1 - coefficient instead
    return 1.0 - coefficient

def hcluster(rows, distance = pearson):
    distances = {}
    current_clust_id = -1

    # Clusters are initially just the rows
    clusters = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(clusters) > 1:
        lowestpair = (0, 1)
        closest = distance(clusters[0].vec, clusters[1].vec)

        # loop through every pair looking for the smallest distance
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                # distances is the cache of the distance calculations
                if (clusters[i].id, clusters[j].id) not in distances:
                    distances[clusters[i].id, clusters[j].id] = distance(clusters[i].vec, clusters[j].vec)

                d = distances[(clusters[i].id, clusters[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i,j)

        # calculate the average of the two clusters
        mergevec = [
            (clusters[lowestpair[0]].vec[i] + clusters[lowestpair[1]].vec[i]) / 2.0
            for i in range(len(clusters[0].vec))]

        # create the new cluster
        new_cluster = bicluster(mergevec, left = clusters[lowestpair[0]], right = clusters[lowestpair[1]],
            distance = closest, id = current_clust_id)

        # cluster ids that weren't in the original set are negative
        current_clust_id -= 1
        del clusters[lowestpair[1]]
        del clusters[lowestpair[0]]
        clusters.append(new_cluster)

    return clusters[0]

def kcluster(rows, distance=pearson, k=4):
    # Determine the minimum and maximum values for each point
    # This is the min and max row value for each column
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]

    # Create k randomly placed centroids that are within range of each row
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]

    lastmatches = None

    for t in range(100):
        # 100 is an arbitrarily chosen number of iterations we want to do
        # if we are not able to attain the desired number of clusters soon
        # enough
        print 'Iteration %d' % t
        bestmatches = [[] for i in range(k)]

        # Find which centroid is the closest for each row
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            best_distance = distance(clusters[bestmatch], row)

            for i in range(k):
                d = distance(clusters[i], row)

                if d < best_distance:
                    bestmatch = i
                    best_distance = d

            bestmatches[bestmatch].append(j)

        # If the results are the same as the last time, this is complete
        if bestmatches == lastmatches:
            break

        lastmatches = bestmatches

        # Move the centroids to the average of their members
        for i in range(k):
            avgs = [0.0] * len(rows[0])

            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]

                    for j in range (len(avgs)):
                        avgs[j] /= len(bestmatches[i])

                clusters[i] = avgs

    return bestmatches


def print_cluster(cluster, labels=None, n=0):
    # indent to make hierarchy layout
    for i in range(n):
        print ' ',

    if cluster.id < 0:
        # negative id means this is branch
        print '-'
    else:
        # positive id means this is an endpoint
        if labels == None:
            print cluster.id
        else:
            print labels[cluster.id]

    # now print the left and right branches
    if cluster.left != None: print_cluster(cluster.left, labels=labels, n=n+1)
    if cluster.right != None: print_cluster(cluster.right, labels=labels, n=n+1)

def get_height(cluster):
    # If this is an endpoint the height is just 1
    if cluster.left == None and cluster.right == None: return 1

    # Otherwise the height is the sum of the heights of each branch
    return get_height(cluster.left) + get_height(cluster.right)

def get_depth(cluster):
    # The distance of an endpoint is 0.0
    if cluster.left == None and cluster.right == None: return 0

    # The distance of a branch branch is the greater of its two sides
    # plus its own distance
    return max(get_depth(cluster.left), get_depth(cluster.right)) + cluster.distance

def draw_dendrogram(cluster, labels, jpeg='clusters.jpg'):
    # height and width
    h = get_height(cluster) * 20
    w = 1200
    depth = get_depth(cluster)

    # width is fixed, so scale distances accordingly
    scaling = float(w - 150) / depth

    # Create a new image with a white background
    img = Image.new('RGB', (w,h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h / 2, 10, h / 2), fill=(255,0,0))

    # Draw the first node
    draw_node(draw, cluster, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')

def draw_node(draw, cluster, x, y, scaling, labels):
    if cluster.id < 0:
        h1 = get_height(cluster.left) * 20
        h2 = get_height(cluster.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        # Line length
        line_length = cluster.distance * scaling

        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # Horizontal line to left item
        draw.line((x, top + h1 / 2 , x + line_length, top + h1 / 2), fill=(255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - h2 / 2, x + line_length, bottom - h2 / 2), fill=(255, 0, 0))

        # Call the function to draw the left and right nodes
        draw_node(draw, cluster.left, x + line_length, top + h1 / 2, scaling, labels)
        draw_node(draw, cluster.right, x + line_length, bottom - h2 / 2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x+5, y-7), labels[cluster.id], (0, 0, 0))