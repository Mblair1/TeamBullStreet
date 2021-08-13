#TeamBullStreet RISE 2021
#Happiness metrics. 
#Uses an emotional AI api to detect sentiment
#in employees coments within the app.

#Importing the Emotional AI Api.
import paralleldots
api_key = "XEJJc0vPsbqXjgDxhJHhWpXRwjNzQ8crQneVzpI1Td4"

#Get file object to analyze.
file = open("Rise_Student_Feedback.txt", "r")

#Intent metrics counter. 
#News metrics.
news_count = 0
query_count = 0
spam_count = 0
marketing_count = 0

#List of sentiments in news.
lst_news = ["query", "spam", "marketing"]

#Feedback metrics.
feedback_count = 0
complaint_count = 0
suggestion_count = 0
appreciation_count = 0

#List of sentiments in feedback.
lst_feedback = ["complaint", "suggestion", "appreciation"]

while(True): 
    #Read next line.
    text = file.readline()
    #Check if line is not null.
    if not text:
        break

    #score keeper - will keep the sentiment with the highest probability
    score_keeper = 0

    #Obtaining emotional probabilities. 
    happiness_metrics = paralleldots.intent(text)

    #Parse through the probabilities and detect the sentiment with 
    #the highest probability.
    # if the probability of it being news >  the probability of it being feedback
    #run this

    if happiness_metrics["intent"]["news"] >  happiness_metrics["intent"]["feedback"]["score"]:
        feedback_count += 1
        for i in happiness_metrics["intent"]:
            temp = happiness_metrics["intent"][i]
            if temp > score_keeper: 
                score_keeper = temp

        for key, value in happiness_metrics["intent"].items():
            if lst_news.index(key) == 0 and value == score_keeper: query_count += 1
            if lst_news.index(key) == 1 and value == score_keeper: spam_count += 1
            if lst_news.index(key) == 2 and value == score_keeper: marketing_count += 1
                
    #else run this
    else:
        for i in happiness_metrics["intent"]["feedback"]["tag"]:
            temp = happiness_metrics["intent"]["feedback"]["tag"][i]
            if temp > score_keeper: 
                score_keeper = temp

        for key, value in happiness_metrics["intent"]["feedback"]["tag"].items():
            if lst_feedback.index(key) == 0 and value == score_keeper: complaint_count += 1
            if lst_feedback.index(key) == 1 and value == score_keeper: suggestion_count += 1
            if lst_feedback.index(key) == 2 and value == score_keeper: appreciation_count += 1

print("Number of responses that are feedback:", feedback_count)
print("Number of responses within feedback that are complaints:", complaint_count)
print("Number of responses within feedback that are suggestions:", suggestion_count)
print("Number of responses within feedback that are appreciation:", appreciation_count)


    #then find the highest score in the selected dict. and the highest scores key is the right intent of the text. 