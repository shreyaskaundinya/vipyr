import pandas as pd
from pyodide.http import open_url
from sklearn.cluster import KMeans

# Read dataset from file using pandas
df = pd.read_csv(
    open_url(
        "https://raw.githubusercontent.com/thuwarakeshm/PracticalML-KMeans-Election/master/voters_demo_sample.csv"
    )
)

# perform K-Means clustering to find 2 clusters considering only age and income of voters
kmeans = KMeans(n_clusters=2, random_state=0).fit(df[["Age", "Income"]])

print("Cluster Centroids")
for cluster in kmeans.cluster_centers_:
    print(f"Cluster I : Age {cluster[0]} and Income {cluster[1]}")