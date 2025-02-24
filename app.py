
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# File paths
DATA_PATH = "job_posting.csv"
MODEL_PATH = "tfidf_model.pkl"

# Load data and model
@st.cache_data
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        data.dropna(subset=["job_description"], inplace=True)
        data["job_description"] = data["job_description"].fillna("").astype(str)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        raise

@st.cache_resource
def load_model(filepath):
    try:
        with open(filepath, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        raise

# Recommend Jobs
def recommend_jobs(user_input, tfidf_matrix, vectorizer, data):
    user_query_tfidf = vectorizer.transform([user_input])
    cosine_sim = cosine_similarity(user_query_tfidf, tfidf_matrix).flatten()
    data["similarity_score"] = cosine_sim
    recommended_jobs = (
        data.sort_values(by="similarity_score", ascending=False)
        .head(5)
        .loc[:, ["cleaned_title", "job_category", "country", "avg_hourly", "link"]]
    )
    return recommended_jobs

# Streamlit interface
def main():
    st.title("Job Recommendation System")
    st.write("Enter job title to get recommendations!")

    # Load data and model
    data = load_data(DATA_PATH)
    vectorizer = load_model(MODEL_PATH)
    st.write(f"Data loaded successfully with {len(data)} rows.")
    st.write("Model loaded successfully.")

    # Input
    user_input = st.text_input("Job Title/Description:", "")

    if user_input:
        tfidf_matrix = vectorizer.transform(data["job_description"])
        recommendations = recommend_jobs(user_input, tfidf_matrix, vectorizer, data)

        if not recommendations.empty:
            st.write("**Top Recommendations:**")
            for _, row in recommendations.iterrows():
                st.markdown(
                    f"""
                    **{row['cleaned_title']}**  
                    Category: {row['job_category']}  
                    Location: {row['country']}  
                    Hourly Rate: ${row['avg_hourly']}  
                    [Job Link]({row['link']})  
                    ---
                    """
                )
        else:
            st.write("No matches found. Please modify your input and try again.")
    else:
        st.write("Please enter a job title to get recommendations.")

if __name__ == "__main__":
    main()