import re
import math

class classifier:
    def __init__(self, getfeatures, filename=None):
        # Counts of feature/category combinations
        self.fc = {}

        # Counts of documents in each category
        self.cc = {}
        self.getfeatures = getfeatures

    def incf(self, f, cat):
        # Increase the count of a feature/category pair
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    def incc(self, cat):
        # Increase the count of a category
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    def fcount(self, f, cat):
        # The number of times a feature has appeared in a category
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])

        return 0.0

    def catcount(self, cat):
        # The number of items in a category
        if cat in self.cc:
            return float(self.cc[cat])

        return 0

    def totalcount(self):
        # The total number of items
        return sum(self.cc.values())

    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.getfeatures(item)

        # Increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)

        # Increment the count for this category
        self.incc(cat)

    def fprob(self, f, cat):
        if self.catcount(cat) == 0:
            return 0

        # The total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f, cat)/self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # Calculate current probability
        basicprob = prf(f, cat)

        # Count the number of times this feature has appeared in all
        # categories
        totals = sum([self.fcount(f,c) for c in self.categories()])

        weightedprob = ((weight * ap) + (totals * basicprob)) / (weight + totals)

        return weightedprob

class naivebayes(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.thresholds = {}

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return 1.0

        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}

        # Find the category with the highest probability
        max = 0.0

        for cat in self.categories():
            probs[cat] = self.prob(item, cat)

            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat == best:
                continue

            if probs[cat] * self.getthreshold(best) > probs[best]:
                return default

        return best

    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # Multiply the probabilities of all the features together
        p = 1

        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)

        return p

    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()
        docprob = self.docprob(item, cat)

        return docprob * catprob

def getwords(doc):
    splitter = re.compile('\\W*')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc) if len(s)>2 and len(s) < 20]

    # Return the unique set of words only
    return dict([(w,1) for w in words])

def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')

cl = naivebayes(getwords)
sampletrain(cl)
print cl.classify('quick rabbit', default='unknown')
print cl.classify('quick money', default='unknown')

cl.setthreshold('bad', 3.0)
print cl.classify('quick money', default='unknown')

for i in range(10):
    sampletrain(cl)

print cl.classify('quick money', default='unknown')

cl.classify('quick money', default='unknown')

