# coding: utf-8
#------------------------------------------------------------------------------#
import os
import sys
import json
import datetime
import xlwt

from flask import Flask, jsonify, send_file, request, render_template

from watson_developer_cloud import NaturalLanguageClassifierV1
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, \
        SentimentOptions, CategoriesOptions, EntitiesOptions
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
app = Flask(__name__)
port = int(os.getenv('PORT', 8000))
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
@app.route("/")
def ui_trigger():
    return render_template('tweet_search_3.html')


@app.route("/", methods=['POST'])
def create_file():
    tweet_key = request.form['text']
    #print ("tweet_key : ", tweet_key)
    
    day_1 = request.form['start_day']
    #print ("from_date : ", day_1)
    
    day_2 = request.form['end_day']
    #print ("to_date : ", day_2)

    tweet_dump_file = "output_got.txt"
    if (os.path.isfile(tweet_dump_file)):
        os.remove(tweet_dump_file)

    os.system('python Exporter.py --querysearch {} --since {} --until {} \
               --language lang:en'.format(tweet_key, day_1, day_2))

    tweet_list = []
    with open(tweet_dump_file, "r", encoding='utf8') as fd:
        for line in fd:
            if (len(line) > 1):
                tweet_list.append(line.strip())
    #print (tweet_list)
    #print ("tweet_list length: [%s]" %len(tweet_list)) 

    if (0 == len(tweet_list)):
        return "Sorry !! Scraping Unsuccessful"

    dras_nlc = NaturalLanguageClassifierV1(
        iam_apikey="RPPtGQWQIvNnVR88qRB-VCxaqBZUcg6kx5Od1vwJGDZn",
        url="https://gateway.watsonplatform.net/natural-language-classifier/api")

    dras_nlu = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey='K4stH9lHJfizNGdJOS1NLMAJY4Wt0hH7RCaSP0kdGR19',
        url='https://gateway-lon.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2018-11-16')


    excel_file = "tweet_analysis.xls"
    if (os.path.isfile(excel_file)):
        os.remove(excel_file)

    workbook = xlwt.Workbook()  
  
    # Specifying style 
    style = xlwt.easyxf('font: bold 1') 

    sheet_1 = workbook.add_sheet("Preparedness")
    sheet_1.write(0, 0, 'TWEET TEXT', style) 
    sheet_1.write(0, 1, 'LOCATION', style) 
    sheet_1.write(0, 2, 'COMPANY/ORGANIZATION', style) 
    sheet_1.write(0, 3, 'TOPIC', style) 

    sheet_2 = workbook.add_sheet("Response")
    sheet_2.write(0, 0, 'TWEET TEXT', style) 
    sheet_2.write(0, 1, 'COMPLAIN', style) 
    sheet_2.write(0, 2, 'LOCATION', style)
    sheet_2.write(0, 3, 'TOPIC', style)
    sheet_2.write(0, 4, 'COMPANY/ORGANIZATION', style)
  
    sheet_3 = workbook.add_sheet("Impact") 
    sheet_3.write(0, 0, 'TWEET TEXT', style) 
    sheet_3.write(0, 1, 'COMPLAIN', style) 
    sheet_3.write(0, 2, 'LOCATION', style) 
    sheet_3.write(0, 3, 'TOPIC', style)

    sheet_4 = workbook.add_sheet("Recover")
    sheet_4.write(0, 0, 'TWEET TEXT', style) 
    sheet_4.write(0, 1, 'COMPLAIN', style) 
    sheet_4.write(0, 2, 'LOCATION', style)
    sheet_4.write(0, 3, 'TOPIC', style)
    sheet_4.write(0, 4, 'COMPANY/ORGANIZATION', style)

    sheet_5 = workbook.add_sheet("Other")
    sheet_5.write(0, 0, 'TWEET TEXT', style) 
    sheet_5.write(0, 2, 'TOPIC', style) 


    impact_count = 1
    response_count = 1
    recover_count = 1
    pre_count = 1
    other_count = 1

    tweet_analysis_result = []
    for item in range (0, len(tweet_list)):
        temp_dict = {}
        input_tweet = tweet_list[item]
        temp_dict['tweet'] = input_tweet
        nlc_result = dras_nlc.classify('7738f7x565-nlc-1025', input_tweet).\
                     get_result()
        nlc_result = json.dumps(nlc_result, indent=2)
        category = json.loads(nlc_result)["top_class"]
        #print ("\npredicted tweet category is : ", category)
        temp_dict['category'] = category      
        nlu_response = dras_nlu.analyze(
                           text=input_tweet, 
                           features=Features(
                               sentiment=SentimentOptions(),
                               entities=EntitiesOptions(),
                               categories=CategoriesOptions(limit=3))).\
                       get_result()
        nlu_response = json.dumps(nlu_response, indent=2)
        sentiment = json.loads(nlu_response)["sentiment"]["document"]["label"]
        topic = json.loads(nlu_response)["categories"][0]["label"]
        complain="N"
        if(sentiment=="negative"):
            complain="Y"
        #print ("Tweet Sentiment: ", sentiment)
        #print ("Tweet topic: ", topic)
        entities = json.loads(nlu_response)["entities"]
        prev_location=""
        location_present="n"
        company_present="n"
        for i in range (0, len(entities)):
            if (entities[i]["type"] == "Location"):
                location = prev_location +','+ entities[i]["text"]
                prev_location=location
                location_present="y"
            if(entities[i]["type"] == "Organization" or 
                    entities[i]["type"] == "Company"):
                company= entities[i]["text"]
                company_present="y"
                print ("Company: ", company)
                  
        temp_dict['complain'] = complain                            
        if (location_present == "y"):
                temp_dict['location'] = location
        if (company_present == "y"):
                temp_dict['company'] = company
        temp_dict['topic'] = topic    
        tweet_analysis_result.append(temp_dict)

        #---------------------Fill Excel Starting------------------------------#
        if (category == "Preparedness"):
            sheet_1.write(pre_count, 0, input_tweet)
            if (location_present == "y"):
                sheet_1.write(pre_count, 1, location)
            if (company_present == "y"):
                sheet_1.write(pre_count, 2, company)
            sheet_1.write(pre_count, 3, topic)
            pre_count = pre_count + 1   
            
        if (category == "Response"):
            sheet_2.write(response_count, 0, input_tweet)
            sheet_2.write(response_count, 1, complain)
            if (location_present == "y"):
                sheet_2.write(response_count, 2, location)
            sheet_2.write(response_count, 3, topic)
            if (company_present == "y"):
                sheet_2.write(response_count, 4, company)
            response_count = response_count + 1
                   
        if (category == "Impact"): 
            sheet_3.write(impact_count, 0, input_tweet)
            sheet_3.write(impact_count, 1, complain)
            if (location_present == "y"):
                sheet_3.write(impact_count, 2, location)
            sheet_3.write(impact_count, 3, topic)
            impact_count = impact_count + 1   
    
        if (category == "Recover"):
            sheet_4.write(recover_count, 0, input_tweet)
            sheet_4.write(recover_count, 1, complain)
            if (location_present == "y"):
                sheet_4.write(recover_count, 2, location)
            sheet_4.write(recover_count, 3, topic)
            if (company_present == "y"):
                sheet_4.write(recover_count, 4, company)
            recover_count = recover_count + 1
    
        if (category == "Other"):
            sheet_5.write(other_count, 0, input_tweet)
            sheet_5.write(other_count, 2, topic)
            other_count = other_count + 1
    #-----------------------------Fill Excel Ending----------------------------#

        if (item == 9):
            break
    workbook.save(excel_file) 
    return jsonify(tweet_analysis_result)

    #return jsonify(tweet_list)
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
@app.route("/download")
def get_file():
    path = "tweet_analysis.xls"
    return send_file(path, as_attachment=True)
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
#------------------------------------------------------------------------------#



