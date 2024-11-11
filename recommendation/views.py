import os
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Count
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from .models import Rating
from django.shortcuts import render


def top_products_view(request):
    # Path to the CSV file
    csv_file_path = os.path.join(settings.BASE_DIR, 'recommendation/data/ratings_Beauty.csv')

    # Load the CSV data into the Rating model if not already loaded
    if not Rating.objects.exists():
        amazon_ratings = pd.read_csv(csv_file_path)
        amazon_ratings = amazon_ratings.dropna()
        for index, row in amazon_ratings.iterrows():
            Rating.objects.create(
                user_id=row['UserId'],
                product_id=row['ProductId'],
                rating=row['Rating']
            )

    # Get the top 30 products based on ratings
    popular_products = (
        Rating.objects.values('product_id')
        .annotate(rating_count=Count('rating'))
        .order_by('-rating_count')[:30]
    )
    product_ids = [product['product_id'] for product in popular_products]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return JSON response for AJAX/API calls
        return JsonResponse({'products': product_ids}, safe=False)
    else:
        # Render HTML template for normal requests
        return render(request, 'recommendation/product.html', {'products': product_ids})


def collaborative_filtering_view(request):
    # Load the ratings data
    csv_file_path = os.path.join(settings.BASE_DIR, 'recommendation/data/ratings_Beauty.csv')
    amazon_ratings = pd.read_csv(csv_file_path)
    amazon_ratings = amazon_ratings.dropna()
    
    # Create a utility matrix
    ratings_utility_matrix = amazon_ratings.pivot_table(values='Rating', index='UserId', columns='ProductId', fill_value=0)
    X = ratings_utility_matrix.T  # Transpose the matrix for SVD

    # Perform SVD
    SVD = TruncatedSVD(n_components=10)
    decomposed_matrix = SVD.fit_transform(X)

    # Calculate the correlation matrix
    correlation_matrix = np.corrcoef(decomposed_matrix)

    def get_recommendations(product_id):
        if product_id in X.index:
            product_ID = X.index.tolist().index(product_id)
            correlation_product_ID = correlation_matrix[product_ID]
            # Recommend products with high correlation, excluding the input product itself
            Recommend = X.index[correlation_product_ID > 0.90].tolist()
            if product_id in Recommend:
                Recommend.remove(product_id)
            return Recommend[:30]  # Return top 30 recommendations
        else:
            return []

    if request.method == 'POST':
        product_id = request.POST.get('product_id', None)
        recommended_products = get_recommendations(product_id) if product_id else []

        # Return JSON response for AJAX requests
        return JsonResponse({
            'recommended_products': recommended_products,
            'product_id': product_id
        }, safe=False)

    # Handle GET requests and initial page load
    else:
        # Default to empty recommendations on initial page load
        recommended_products = []

        return render(request, 'recommendation/cf.html', {
            'recommended_products': recommended_products,
            'example_product': None
        })

def recommendation_based_on_product_view(request):
    # Load product descriptions
    csv_file_path = os.path.join(settings.BASE_DIR, 'recommendation/data/product_descriptions.csv')
    product_descriptions = pd.read_csv(csv_file_path)
    product_descriptions = product_descriptions.dropna()

    # Vectorize the product descriptions
    vectorizer = TfidfVectorizer(stop_words='english')
    X1 = vectorizer.fit_transform(product_descriptions["product_description"])

    # Perform K-Means clustering
    true_k = 10
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
    model.fit(X1)

    # Function to print cluster details
    def print_cluster(i):
        cluster_terms = []
        for ind in order_centroids[i, :30]:
            cluster_terms.append(terms[ind])
        return cluster_terms

    def show_recommendations(product):
        Y = vectorizer.transform([product])
        prediction = model.predict(Y)
        return print_cluster(prediction[0])

    # Get top terms per cluster
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    if request.method == 'POST':
        product_name = request.POST.get('product_name', None)
        recommended_products = show_recommendations(product_name) if product_name else []

        # Return JSON response for AJAX requests
        return JsonResponse({
            'recommended_products': recommended_products,
            'product_name': product_name
        }, safe=False)

    # Handle GET requests and initial page load
    else:
        # Default to empty recommendations on initial page load
        recommended_products = []

        return render(request, 'recommendation/pb.html', {
            'recommended_products': recommended_products,
            'example_product': None
        })