import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json

# Load the data collected by DataScoop
def load_data(csv_file=None, json_file=None):
    if csv_file:
        data = pd.read_csv(csv_file)
    elif json_file:
        with open(json_file, "r") as file:
            data = pd.DataFrame(json.load(file))
    else:
        raise ValueError("No file provided")
    return data


# Data visualization function
def visualize_data(data):
    # Example: Bar plot of repositories per organization
    org_repo_counts = data["org"].value_counts()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=org_repo_counts.index, y=org_repo_counts.values)
    plt.xlabel("Organization")
    plt.ylabel("Number of Repositories")
    plt.title("Repositories per Organization")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Example: Pie chart of programming languages usage
    language_counts = data["repo_lang"].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(
        language_counts, labels=language_counts.index, autopct="%1.1f%%", startangle=140
    )
    plt.title("Programming Languages Usage")
    plt.tight_layout()
    plt.show()


# Machine learning function: Clustering repositories by language usage
def cluster_repositories(data):
    # Select relevant features for clustering
    features = data["repo_langs"].apply(lambda x: ",".join(x)).str.get_dummies(sep=",")
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=5, random_state=42)
    data["cluster"] = kmeans.fit_predict(scaled_features)

    # Visualize clusters
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=data["repo_name"], y=data["cluster"], hue=data["cluster"], palette="viridis"
    )
    plt.xlabel("Repository")
    plt.ylabel("Cluster")
    plt.title("Repository Clusters by Language Usage")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Load data
    data = load_data(
        csv_file="datascoop_data.csv"
    )  # or json_file='datascoop_data.json'

    # Visualize data
    visualize_data(data)

    # Apply machine learning and visualize results
    cluster_repositories(data)
