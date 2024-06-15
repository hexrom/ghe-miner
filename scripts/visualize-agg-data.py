import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import glob

# Function to load and aggregate data from multiple CSV files
def load_and_aggregate_data(pattern):
    files = glob.glob(pattern)
    df_list = [pd.read_csv(file) for file in files]
    aggregated_data = pd.concat(df_list, ignore_index=True)
    return aggregated_data


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
    # Load and aggregate data
    aggregated_data = load_and_aggregate_data("data_*.csv")

    # Visualize data
    visualize_data(aggregated_data)

    # Apply machine learning and visualize results
    cluster_repositories(aggregated_data)
