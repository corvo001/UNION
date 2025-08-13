from sklearn.cluster import KMeans

class PatternClassifier:
    def __init__(self, n_clusters=5):
        self.model = KMeans(n_clusters=n_clusters, random_state=42)

    def fit(self, feature_vectors):
        self.model.fit(feature_vectors)

    def predict(self, vector):
        return self.model.predict([vector])[0]
