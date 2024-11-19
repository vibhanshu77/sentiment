from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
import csv
from io import StringIO 
import cohere
import pandas as pd

API_KEY = "9j4ENdOLLz6eGv7YWtbOAWyLUUdjWWXzgBBVQbzU"
co = cohere.Client(API_KEY)
file_path = "Examples.csv"

df = pd.read_csv(file_path)

def classify_sentiment(text):
    sentiment_response = co.classify(
        model="large",
        inputs=[text],
        examples=df.to_dict(orient='records')
    )
    label = sentiment_response.classifications[0].prediction.capitalize()
    confidence = sentiment_response.classifications[0].confidence
    sentiment_score = round((confidence * 100), 2)

    return label, sentiment_score

def generate_summary(text):
    prompt = f"You are an expert product reviewer. Summarize the following customer reviews in a concise and complete manner. Provide an overall opinion on the product, focusing on the general sentiment. Include a clear evaluation of whether the product is recommended or not, based on the feedback. Ensure that the summary covers both positive and negative aspects and ends with a clear, definitive conclusion about the product’s recommendation. Please keep the summary short, but make sure it is complete and comprehensive.\n{text}"
    response = co.generate(
        model="command-nightly",
        prompt=prompt,
        max_tokens=120,  
        temperature=0.7, 
        k=0, 
        p=0.75,
        stop_sequences=["\n"]
    )
    summary = response.generations[0].text.strip()
    last_full_stop_position = summary.rfind('.')
    summary = summary[0:last_full_stop_position+1]
    return summary


def index(request):
    return render(request, 'index.html')

@api_view(['POST'])
def review_result(request):
    if request.method == 'POST':
        txt = request.data.get('textInput','')
        if txt:
            sentiment, sentiment_score = classify_sentiment(txt)

            product_summary = generate_summary(txt)

            result = {
                "text": txt,
                "sentiment" : sentiment,
                "sentiment_score" : sentiment_score,
                "summary" : product_summary
            }
            return Response(result)
        
        file = request.FILES.get('fileInput', None)
        if file:
            try:
                file_content = file.read().decode('utf-8')
                csv_reader = csv.reader(StringIO(file_content))
                results = []
                sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
                overall_sentiment_score = 0
                # header = next(csv_reader, None)

                for row in csv_reader:
                    if row:
                        text = row[0]
                        sentiment, sentiment_score = classify_sentiment(text)
                        sentiment_counts[sentiment] += 1
                        overall_sentiment_score += sentiment_score
                        results.append((text, sentiment, sentiment_score))

                total_reviews = len(results)
                if total_reviews == 0:
                    return Response({"error": "No valid reviews found in the file."}, status=400)
                
                positive_percentage = round(((sentiment_counts["Positive"] / total_reviews) * 100), 2)
                neutral_percentage = round(((sentiment_counts["Neutral"] / total_reviews) * 100), 2)
                negative_percentage = round(((sentiment_counts["Negative"] / total_reviews) * 100), 2)  
                average_sentiment_score = round((overall_sentiment_score / total_reviews), 2)
                
                all_reviews_text = " ".join([review[0] for review in results])
                
                if sentiment_counts["Positive"] > sentiment_counts["Negative"] and sentiment_counts["Positive"] > sentiment_counts["Neutral"]:
                    overall_sentiment = "Positive"
                elif sentiment_counts["Negative"] > sentiment_counts["Positive"] and sentiment_counts["Negative"] > sentiment_counts["Neutral"]:
                    overall_sentiment = "Negative"
                else:
                    overall_sentiment = "Neutral"

                product_summary = generate_summary(all_reviews_text)
                
                result = {
                            "Positive_Reviews" : positive_percentage,
                            "Neutral_Reviews" : neutral_percentage,
                            "Negative_Reviews" : negative_percentage,
                            "Average_Sentiment_Score" : average_sentiment_score,
                            "Overall_Sentiment" : overall_sentiment,
                            "Product_Summary" : product_summary
                        }
                
                return Response(result)

            except Exception as e:
                return Response({"error": f"Error processing file: {str(e)}"}, status=500)
        
        return Response({"error": "No input text or file provided."}, status=400)