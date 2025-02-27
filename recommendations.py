import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

# --- Data Loading & Preprocessing ---

# Load the dataset
df_merge = pd.read_csv('df_merge.csv')
df_rs = df_merge[["customer_unique_id","product_id","product_category_name_english","review_score"]]

# Clean up product category names
df_rs['product_category_name_cleaned'] = df_rs['product_category_name_english'].str.replace('_', ' ')
df_rs = df_rs.sort_values(by=['product_id', 'product_category_name_cleaned'])

df_product_labels = df_rs[['product_id', 'product_category_name_cleaned']].drop_duplicates()
df_product_labels['product_category_numbered'] = df_product_labels.groupby('product_category_name_cleaned').cumcount() + 1
df_product_labels['product_category_labeled'] = df_product_labels['product_category_name_cleaned'] + " " + df_product_labels['product_category_numbered'].astype(str)

df_rs = df_rs.merge(df_product_labels[['product_id', 'product_category_labeled']], on='product_id', how='left')

# --- User-Based Collaborative Filtering ---

SAMPLE_FRACTION = 0.55 # Adjust as needed

# Get unique users
unique_users = df_rs['customer_unique_id'].unique()

# Randomly sample users
sampled_users = pd.Series(unique_users).sample(frac=SAMPLE_FRACTION, random_state=42)

# Filter dataset to only include sampled users
df_sampled = df_rs[df_rs['customer_unique_id'].isin(sampled_users)]

df_sampled = df_sampled.groupby(['customer_unique_id', 'product_id'], as_index=False)['review_score'].mean()

user_item_matrix = df_sampled.pivot(index='customer_unique_id', columns='product_id', values='review_score')
user_item_matrix = user_item_matrix.fillna(0)


# Convert the user-item matrix to a sparse matrix (for efficiency)
user_item_sparse = csr_matrix(user_item_matrix.values)

user_similarity = cosine_similarity(user_item_sparse)
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

def recommend_user_based(target_user, n_recommendations=5):
    if target_user not in user_similarity_df.index:
        return f"Sorry, no recommendations available for user {target_user}. Try exploring popular products!"

    similar_users = user_similarity_df[target_user].drop(target_user).sort_values(ascending=False)
    top_similar_users = similar_users.head(3).index  
    similar_users_items = user_item_matrix.loc[top_similar_users].mean(axis=0)
    user_rated_products = user_item_matrix.loc[target_user][user_item_matrix.loc[target_user] > 0].index
    recommended_product_ids = similar_users_items.drop(user_rated_products).sort_values(ascending=False).head(n_recommendations).index
    product_mapping = df_rs[['product_id', 'product_category_labeled']].drop_duplicates().set_index('product_id')['product_category_labeled']
    
    recommended_categories = product_mapping.loc[recommended_product_ids].tolist()[:n_recommendations]

    return recommended_categories






# --- Item-Based Collaborative Filtering ---

# Prepare the item-user data by grouping reviews
df_sampled_item = df_rs.groupby(['product_id', 'customer_unique_id'], as_index=False)['review_score'].mean()

PRODUCT_SAMPLING_PERCENTAGE = 0.35
total_unique_products = df_rs["product_id"].nunique()
MAX_PRODUCTS = int(total_unique_products * PRODUCT_SAMPLING_PERCENTAGE)

top_products = df_sampled_item['product_id'].value_counts().nlargest(MAX_PRODUCTS).index
df_sampled_item = df_sampled_item[df_sampled_item['product_id'].isin(top_products)]

item_user_matrix = df_sampled_item.pivot(index='product_id', columns='customer_unique_id', values='review_score')
item_user_matrix = item_user_matrix.fillna(0)

# Convert the matrix to a sparse format (for efficiency)
item_user_sparse = csr_matrix(item_user_matrix.values)
item_similarity = cosine_similarity(item_user_sparse)
item_similarity_df = pd.DataFrame(item_similarity, index=item_user_matrix.index, columns=item_user_matrix.index)

def recommend_item_based(target_product, n_recommendations=5):
    if target_product not in item_similarity_df.index:
        return "Product not found. Try exploring other popular products!"

    similar_products = item_similarity_df[target_product].sort_values(ascending=False)
    recommended_product_ids = similar_products.drop(target_product).head(n_recommendations).index
    product_mapping = df_rs[['product_id', 'product_category_labeled']].drop_duplicates().set_index('product_id')['product_category_labeled']
    recommended_categories = product_mapping.loc[recommended_product_ids].tolist()

    return recommended_categories[:n_recommendations]