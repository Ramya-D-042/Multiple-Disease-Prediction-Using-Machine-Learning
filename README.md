Multiple Disease Prediction - Final (Single 15-input prediction)
----------------------------------------------------------------
This Flask app predicts Heart Disease, Diabetes, and Parkinson's simultaneously from a single
set of 15 common inputs. It includes login/signup/forgot, admin users view, contact popup,
attractive UI, and models pre-trained on demo synthetic data that accept 15 inputs (so the single-form works).

Files of interest:
 - app.py : Flask backend
 - train_models.py : trains dataset-specific models (if you want to replace)
 - train_unified_models.py : creates demo unified models that accept 15 inputs (already saved in models/)
 - templates/ : HTML templates including admin page
 - static/ : CSS and logo
 - models/ : contains unified demo models and scalers that accept 15 features
 - dataset/ : place your CSVs here if you want to train dataset-specific models

Quick run:
 1. pip install -r requirements.txt
 2. (Optional) place your CSVs into dataset/ and run python train_models.py
 3. python app.py
 4. Open http://127.0.0.1:5000

Demo login: demo / Demo@1234
Contact: healthpredict@gmail.com | +91 98765 43210
