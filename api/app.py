from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field,computed_field,field_validator
from typing import Annotated,Optional,Literal
import pandas as pd
import pickle
from modelling.predict import predict_output,model,MODEL_VERSION
from schema.user_input import Userinput
from schema import user_input
app=FastAPI()




#human readable , anyone hits this url , understandable by human
@app.get("/")
def home():
    return{"message":"Fastapi is running!"}

#deployment m aws, they will use this endpoint to know that the url is working properly

@app.get('/health')
def health_check():
    return{
        'status':'OK',
        'model_loaded' : model is not None ,
        'version' : MODEL_VERSION,
    }



@app.post('/predict')
def predict_premium(data:Userinput):


    input_df={
        'bmi':data.bmi,
        'age_group':data.age_group,
        'lifestyle_risk':data.lfiestyle_risk,
        'city_tier':data.city_tier,
        'income_lpa':data.income_lpa,
        'occupation':data.occupation
    }

    prediction=predict_output(input_df)
    return JSONResponse(status_code=200,content={'Predicted_category':prediction})