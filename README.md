# Insurance Premium Prediction API

This is just dummy project , for my own learning.
This project is made for my learning of FastApi as well as Docker(Docker image and Docker compose )
Creating API for implementation with Ml models and using streamlit as frontend for this project
A machine learning-powered REST API and web application for predicting insurance premiums based on user demographics and lifestyle factors.

## 📋 Features

- **FastAPI Backend**: High-performance REST API for premium predictions
- **Streamlit Frontend**: Interactive web interface for easy access to predictions
- **ML Model**: Trained classification model for accurate premium categorization
- **Input Validation**: Pydantic models for robust data validation
- **Health Checks**: Built-in health check endpoint for deployment monitoring
- **City Tier Categorization**: Automatic city classification for better prediction accuracy

## 🏗️ Architecture

```
├── api/
│   ├── app.py              # FastAPI application with endpoints
│   └── frontend.py         # Streamlit web interface
├── modelling/
│   ├── model.ipynb         # Model training notebook
│   └── predict.py          # Prediction logic
├── schema/
│   └── user_input.py       # Pydantic models for input validation
├── config/
│   └── city_tier.py        # City tier configuration
├── insurance.csv           # Training dataset
└── requirement1.txt        # Project dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd fapi
```

2. **Install dependencies**

```bash
pip install -r requirement1.txt
```

## 📖 Usage

### Running the API Server

```bash
cd api
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

### Running the Streamlit Frontend

```bash
cd api
streamlit run frontend.py
```

The web interface will be available at `http://localhost:8501`

## 🔌 API Endpoints

### 1. Home Endpoint

```
GET /
```

Returns a welcome message confirming the API is running.

### 2. Health Check

```
GET /health
```

Returns the health status of the API and model.

**Response:**

```json
{
  "status": "OK",
  "model_loaded": true,
  "version": "1.0"
}
```

### 3. Premium Prediction

```
POST /predict
```

Predicts the insurance premium category based on user input.

**Request Body:**

```json
{
  "age": 35,
  "weight": 70.5,
  "height": 1.75,
  "income_lpa": 12.5,
  "smoker": false,
  "city": "Delhi",
  "occupation": "private_job"
}
```

**Response:**

```json
{
  "Predicted_category": "medium"
}
```

## 📝 Input Parameters

| Parameter  | Type  | Description            | Constraints                                                                           |
| ---------- | ----- | ---------------------- | ------------------------------------------------------------------------------------- |
| age        | int   | Age of the user        | 0 < age < 120                                                                         |
| weight     | float | Weight in kg           | > 0                                                                                   |
| height     | float | Height in meters       | > 0                                                                                   |
| income_lpa | float | Annual income in lakhs | > 0                                                                                   |
| smoker     | bool  | Smoking status         | true/false                                                                            |
| city       | str   | City name              | Auto-normalized to title case                                                         |
| occupation | str   | Job type               | retired, freelancer, student, government_job, business_owner, unemployed, private_job |

## 🛠️ Development

### Model Training

Open and run the notebook to train/retrain the model:

```bash
jupyter notebook modelling/model.ipynb
```

### Project Structure Details

- **app.py**: Main FastAPI application with three endpoints
- **frontend.py**: Streamlit UI for user interactions
- **predict.py**: Model loading and prediction logic
- **user_input.py**: Pydantic BaseModel for request validation
- **city_tier.py**: City categorization configuration

## 📦 Dependencies

Key packages:

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `streamlit`: Web UI framework
- `pydantic`: Data validation
- `pandas`: Data processing
- `scikit-learn`: Machine learning

See `requirement1.txt` for complete dependencies.

## 🔄 Workflow

1. User provides input via Streamlit frontend or API request
2. Input is validated against Pydantic schema
3. City is normalized and categorized
4. BMI and age group are computed
5. Prediction model generates premium category
6. Result is returned to user

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Created for insurance premium prediction using machine learning.

---

**Last Updated:** 2026-07-22
