from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field,computed_field,field_validator
from typing import Annotated,Optional,Literal
import pandas as pd
import pickle

with open('model.pkl','rb') as f:
    model=pickle.load(f)

print(model)
print(model.named_steps["preprocessor"].named_transformers_["cat"].categories_)
MODEL_VERSION='1.0.0'
app=FastAPI()


tier_1_cities=["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities=[
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]
#PYDANTIC MODEL TO EVALUATE INCOMING DATA
class userinput(BaseModel):
    age:Annotated[int,Field(...,gt=0,lt=120,description='age of the user')]
    weight:Annotated[float,Field(...,gt=0,description='weight of the user')]
    height:Annotated[float,Field(...,gt=0,description='Height of the user in meters')]
    income_lpa:Annotated[float,Field(...,gt=0,description='Income of the user ')]
    smoker:Annotated[bool,Field(...,description='is the user smoker or not')]
    city:Annotated[str,Field(...,description='the city the user belongs to')]
    occupation: Annotated[Literal['retired','freelancer','student', 'government_job','business_owner','unemployed','private_job'],Field(...,description='Occupation of the user')]


    @field_validator('city')
    @classmethod
    def normaliz_city(cls, v:str) -> str:
        v=v.strip().title()
        return v

    @computed_field
    @property
    def bmi(self) ->float:
        return self.weight/self.height**2

    @computed_field
    @property
    def lfiestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker and self.bmi >27:
            return "medium"
        else:
            return "low" 

    @computed_field
    @property
    def city_tier(self) ->int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age<25:
            return"young"
        elif self.age<45:
            return "adult"
        elif self.age<60:
            return "middle_aged"
        else:
            return "senior"

#human readable , anyone hits this url , understandable by human
@app.get("/")
def home():
    return{"message":"Fastapi is running!"}

#deployment m aws, they will use this endpoint to know that the url is working properly

@app.get('/health')
def health_check():
    return{
        'status':'OK',
        'model_loaded' : model is not None 
        'version' : MODEL_VERSION,
    }



@app.post('/predict')
def predict_premium(data:userinput):


    input_df=pd.DataFrame([{
        'bmi':data.bmi,
        'age_group':data.age_group,
        'lifestyle_risk':data.lfiestyle_risk,
        'city_tier':data.city_tier,
        'income_lpa':data.income_lpa,
        'occupation':data.occupation
    }])

    prediction=model.predict(input_df)[0]
    return JSONResponse(status_code=200,content={'Predicted_category':prediction})