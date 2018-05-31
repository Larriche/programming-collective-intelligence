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


#print read_file('blogdata.txt')
blognames, words, data = read_file('blogdata.txt')
cluster = hcluster(data)
draw_dendrogram(cluster, blognames, jpeg='blogdata.jpg')
