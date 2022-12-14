import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#1. LOADING & PRE-PROCESSING CLASS-LEVEL DATASET
# Load class-level dataset
df = pd.read_csv('class.csv', low_memory=False)
df.info()

# Check missing data in dataset
for col in df.columns:
  missing_data=df[col].isna().sum()
  if (missing_data>0):
    print(f"column {col} has {missing_data} missing data")

# Define and initialise a predictive result dataset
rs= pd.DataFrame({'Code_smell':[],'Algo':[],'Balance':[],'Ratio':[] , 'Accuracy':[],'Precision':[], 'F1_score':[],'AUC':[]})

# 2. BUILDING THE MACHINELEARNING MODEL

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, roc_auc_score, f1_score
def _train_and_test(model, _data_train, algo):
  global newResult, accuracy,precision,f1,roc
  model.fit(_data_train[features], _data_train[target])
  predictions = model.predict_proba(data_test[features])
  pred_label = model.predict(data_test[features]) 
  accuracy = accuracy_score(data_test[target], pred_label)
  precision = precision_score(data_test[target], pred_label)
  f1 = f1_score(data_test[target], pred_label)
  roc = roc_auc_score(data_test[target], predictions[:,1])
  print('{} Accuracy score on test: {}'.format(algo, accuracy))
  print('{} Precision score on test: {}'.format(algo, precision))
  print('{} ROC score on test: {}'.format(algo, roc))
  print('{} F1 score on test: {}'.format(algo, f1))
  print('{} Classification Report: '.format(algo))
  print(classification_report(data_test[target], pred_label))
  newResult = {'Code_smell':target,'Algo':_algo,'Balance':_balance,'Ratio':_ratio , 'Accuracy':accuracy,'Precision':precision, 'F1_score':f1,'AUC':roc}
  return newResult

# 3. SEQUENTLY, CODE SMELL PREDICTING BY EACH OTHER MODELS
features = list(df.select_dtypes(include=['int64', 'float64']).columns)
target = 'Brain Class'
df[target] = df[target].astype(int)

# Split the Brain-class dataset into subsets: training-set, validation-set, and testing-set.
y = df[target]
X = df[features]

id_pos = np.where(y.values.reshape(-1) == 1)[0]
id_neg = np.where(y.values.reshape(-1) == 0)[0]

np.random.shuffle(id_pos)
np.random.shuffle(id_neg)

train_pos_size = 500
train_neg_size = 223500
val_pos_size = 170
val_neg_size = 74500

# Creating training-set:
id_train_pos = id_pos[:train_pos_size]
id_train_neg = id_neg[:train_neg_size] 
id_train = np.concatenate((id_train_pos, id_train_neg), axis = 0)

# Creating validation-set:
id_val_pos = id_pos[train_pos_size:(train_pos_size + val_pos_size)]
id_val_neg = id_neg[train_neg_size:(train_neg_size + val_neg_size)]
id_val = np.concatenate((id_val_pos, id_val_neg), axis = 0)

# Creating testing-set:
id_test_pos = id_pos[(train_pos_size + val_pos_size):(train_pos_size + 2*val_pos_size)]
id_test_neg = id_neg[(train_neg_size + val_neg_size):(train_neg_size + 2*val_neg_size)]
id_test = np.concatenate((id_test_pos, id_test_neg), axis = 0)

# initialize datasets
data_train = df.iloc[id_train]
data_val = df.iloc[id_val]
data_test = df.iloc[id_test] 

## Using the Undersampling method, balancing the training-set in different ratios 
# Create the training-set in the ratio 80:20 (~ 4*train_pos_size:train_pos_size) by keeping 4*train_pos_size random negative samples from it.
np.random.shuffle(id_train_neg)
id_train_neg_80_20 = id_train_neg[:4*train_pos_size]
id_train_80_20 = np.concatenate((id_train_neg_80_20, id_train_pos), axis = 0)

# Create the training-set in the ratio 75:25 (~ 3*train_pos_size:train_pos_size) by keeping 3*train_pos_size random negative samples from it.
np.random.shuffle(id_train_neg)
id_train_neg_75_25 = id_train_neg[:3*train_pos_size]
id_train_75_25 = np.concatenate((id_train_neg_75_25, id_train_pos), axis = 0) 

# Create the training-set in the ratio 60:40 (~ 1.5*train_pos_size:train_pos_size) by keeping 1.5*train_pos_size random negative samples from it.
np.random.shuffle(id_train_neg)
id_train_neg_60_40 = id_train_neg[:int(1.5*train_pos_size)]
id_train_60_40 = np.concatenate((id_train_neg_60_40, id_train_pos), axis = 0) 

# initialize training-set
data_train_80_20 = df.iloc[id_train_80_20]
data_train_75_25 = df.iloc[id_train_75_25]
data_train_60_40 = df.iloc[id_train_60_40]

#The validation-set is used for model tuning to determine the best-selected model.
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score
import matplotlib.pyplot as plt

model_1 = RandomForestClassifier(n_estimators=100,
                                max_depth=5,
                                min_samples_split=200,
                                class_weight=None,
                                max_features=10)

model_2 = RandomForestClassifier(n_estimators=500, 
                                max_depth=10, 
                                min_samples_split=400, 
                                random_state=12, 
                                class_weight="balanced",
                                max_features="auto")

model_3 = RandomForestClassifier(n_estimators=800, 
                                max_depth=10, 
                                min_samples_split=200, 
                                random_state=12, 
                                class_weight="balanced",
                                max_features="sqrt")

def _tunning_model(model , X_train, y_train, X_val, y_val):
  model.fit(X_train, y_train)
  model_predictions = model.predict_proba(X_val)
  model_pred = model.predict(X_val[features]) 
  model_roc_score = roc_auc_score(y_val, 
                                  model_predictions[:,1])
  model_f1_score = f1_score(y_val, model_pred)
  return model, model_roc_score, model_f1_score

model_1, model_1_roc_score, model_1_f1_score = _tunning_model(model_1, 
                                          data_train[features], data_train[target],
                                          data_val[features], data_val[target])
print('model 1 F1 score on val dataset: ', model_1_f1_score)
#print('model 1 ROC score on validation-set: ', model_1_roc_score)

model_2, model2_roc_score, model_2_f1_score = _tunning_model(model_2, 
                                          data_train[features], data_train[target],
                                          data_val[features], data_val[target])
print('model 2 F1 score on val dataset: ', model_2_f1_score)
#print('model 2 ROC score on validation-set: ', model_2_roc_score)


model_3, model3_roc_score, model_3_f1_score = _tunning_model(model_3, 
                                          data_train[features], data_train[target],
                                          data_val[features], data_val[target])
print('model 3 F1 score on val dataset: ', model_3_f1_score)
#print('model 3 ROC score on validation-set: ', model_3_roc_score)

#3.1 Creating the best-selected model using Random Forest Classifier algorithm
from sklearn.ensemble import RandomForestClassifier
RFC_model = RandomForestClassifier(n_estimators=100,
                                max_depth=5,
                                min_samples_split=200,
                                class_weight=None,
                                max_features=10)
_algo = 'RFC'

# Training & testing the model on the imbanlance training-set.
_balance ='_None_'
_ratio = '*'
rs = rs.append(_train_and_test(RFC_model, data_train, _algo + _balance + _ratio),ignore_index=True)

#Training & testing the model on training-set with differrent ratio of Undersampling balancing method.
_balance ='_unsam_'
_ratio = '80_20'
rs = rs.append(_train_and_test(RFC_model, data_train_80_20, _algo + _balance + _ratio),ignore_index=True)
_ratio = '75_25'
rs = rs.append(_train_and_test(RFC_model, data_train_75_25, _algo+_balance+_ratio),ignore_index=True)
_ratio = '60_40'
rs = rs.append(_train_and_test(RFC_model, data_train_60_40, _algo+_balance+_ratio),ignore_index=True)

#Training & testing the model on training-set with differrent Oversampling balancing method.
from imblearn.pipeline import make_pipeline
from imblearn.over_sampling import (RandomOverSampler, SMOTE, BorderlineSMOTE, SVMSMOTE, ADASYN)

oversam = {0 : 'RandomOverSampler',
          1 : 'SMOTE',
          2 : 'BorderlineSMOTE',
          3 : 'SVMSMOTE',
          4 : 'ADASYN'}
_balance ='_oversam_'
for i, sampler in enumerate((RandomOverSampler(sampling_strategy = 1, random_state=0), 
                             SMOTE(sampling_strategy = 1, random_state=0),
                             BorderlineSMOTE(sampling_strategy = 1, random_state=0, kind='borderline-1'),
                             SVMSMOTE(sampling_strategy = 1, random_state=0),
                             ADASYN(sampling_strategy = 1, random_state=0))):
  pipe_line = make_pipeline(sampler, RFC_model)
  _ratio = oversam[i]
  rs = rs.append(_train_and_test(pipe_line, data_train, _algo + _balance + _ratio),ignore_index=True)

rs.to_csv('Class_BrainClass_RFC_rs.csv', header=True, sep=';', decimal=',') 

#3.2 Creating the best-selected model using Light Gradient Boosting algorithm
import lightgbm as lgb

LGB_model = lgb.LGBMClassifier(n_estimator = 800, 
                                    objective = 'binary', 
                                    class_weight = 'balanced',
                                    learning_rate = 0.05,
                                    reg_alpha = 0.1,
                                    reg_lambda = 0.1,
                                    subsample = 0.8,
                                    n_job = -1,
                                    random_state = 12
                                   )
_algo = 'LGB'

# Training & testing the model on the imbanlance training-set.
_balance ='_None_'
_ratio = '*'
rs = rs.append(_train_and_test(LGB_model, data_train, _algo + _balance + _ratio),ignore_index=True)

#Training & testing the model on training-set with differrent ratio of Undersampling balancing method.
_balance ='_unsam_'
_ratio='80_20'
rs = rs.append(_train_and_test(LGB_model, data_train_80_20, _algo+_balance+_ratio),ignore_index=True)
_ratio='75_25'
rs = rs.append(_train_and_test(LGB_model, data_train_75_25, _algo+_balance+_ratio),ignore_index=True)
_ratio='60_40'
rs = rs.append(_train_and_test(LGB_model, data_train_60_40, _algo+_balance+_ratio),ignore_index=True)

#Training & testing the model on training-set with differrent Oversampling balancing method.
_balance ='_oversam_'
for i, sampler in enumerate((RandomOverSampler(sampling_strategy = 1, random_state=0), 
                             SMOTE(sampling_strategy = 1, random_state=0),
                             BorderlineSMOTE(sampling_strategy = 1, random_state=0, kind='borderline-1'),
                             SVMSMOTE(sampling_strategy = 1, random_state=0),
                             ADASYN(sampling_strategy = 1, random_state=0))):
  pipe_line = make_pipeline(sampler, LGB_model)
  _ratio = oversam[i]
  rs = rs.append(_train_and_test(pipe_line, data_train, _algo + _balance + _ratio),ignore_index=True)

#3.3 Creating the best-selected model using KNeighbors Classifier algorithm
import lightgbm as lgb

from sklearn.neighbors import KNeighborsClassifier

KNN_model = KNeighborsClassifier(n_neighbors = 5, 
                                      weights = 'distance',
                                      algorithm = 'kd_tree',
                                      metric = 'minkowski'
                                      )
_algo = 'KNN'

# Training & testing the model on the imbanlance training-set.
_balance ='_None_'
_ratio = '*'
rs = rs.append(_train_and_test(KNN_model, data_train, _algo + _balance + _ratio),ignore_index=True)

#Training & testing the model on training-set with differrent ratio of Undersampling balancing method.
_balance ='_unsam_'
_ratio='80_20'
rs = rs.append(_train_and_test(KNN_model, data_train_80_20, _algo+_balance+_ratio),ignore_index=True)
_ratio='75_25'
rs = rs.append(_train_and_test(KNN_model, data_train_75_25, _algo+_balance+_ratio),ignore_index=True)
_ratio='60_40'
rs = rs.append(_train_and_test(KNN_model, data_train_60_40, _algo+_balance+_ratio),ignore_index=True)

# Training & testing the model on training-set with differrent Oversampling balancing method.
_balance ='_oversam_'
for i, sampler in enumerate((RandomOverSampler(sampling_strategy = 1, random_state=0), 
                             SMOTE(sampling_strategy = 1, random_state=0),
                             BorderlineSMOTE(sampling_strategy = 1, random_state=0, kind='borderline-1'),
                             SVMSMOTE(sampling_strategy = 1, random_state=0),
                             ADASYN(sampling_strategy = 1, random_state=0))):
  pipe_line = make_pipeline(sampler, KNN_model)
  _ratio = oversam[i]
  rs = rs.append(_train_and_test(pipe_line, data_train, _algo + _balance + _ratio),ignore_index=True)
rs.to_csv('Class_BrainClass_KNN_rs.csv', header=True, sep=';', decimal=',') 

#3.4 Creating the best-selected model using Linear Logistic Regression algorithm
from sklearn.linear_model import LogisticRegression
LLR_model = LogisticRegression(C = 0.0001)
_algo = 'LLR'

# Training & testing the model on the imbanlance training-set.
_balance ='_None_'
_ratio = '*'
rs = rs.append(_train_and_test(LLR_model, data_train, _algo + _balance + _ratio),ignore_index=True)

#Training & testing the model on training-set with differrent ratio of Undersampling balancing method.
_balance ='_unsam_'
_ratio = '80_20'
rs = rs.append(_train_and_test(LLR_model, data_train_80_20, _algo + _balance + _ratio),ignore_index=True)
_ratio = '75_25'
rs = rs.append(_train_and_test(LLR_model, data_train_75_25, _algo+_balance+_ratio),ignore_index=True)
_ratio = '60_40'
rs = rs.append(_train_and_test(LLR_model, data_train_60_40, _algo+_balance+_ratio),ignore_index=True)

# Training & testing the model on training-set with differrent Oversampling balancing method.
from imblearn.pipeline import make_pipeline
from imblearn.over_sampling import (RandomOverSampler, SMOTE, BorderlineSMOTE, SVMSMOTE, ADASYN)

oversam = {0 : 'RandomOverSampler',
          1 : 'SMOTE',
          2 : 'BorderlineSMOTE',
          3 : 'SVMSMOTE',
          4 : 'ADASYN'}
_balance ='_oversam_'
for i, sampler in enumerate((RandomOverSampler(sampling_strategy = 1, random_state=0), 
                             SMOTE(sampling_strategy = 1, random_state=0),
                             BorderlineSMOTE(sampling_strategy = 1, random_state=0, kind='borderline-1'),
                             SVMSMOTE(sampling_strategy = 1, random_state=0),
                             ADASYN(sampling_strategy = 1, random_state=0))):
  pipe_line = make_pipeline(sampler, LLR_model)
  _ratio = oversam[i]
  rs = rs.append(_train_and_test(pipe_line, data_train, _algo + _balance + _ratio),ignore_index=True)

  
#3.5 Creating the best-selected model using Linear Support Vector Classification algorithm
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

SVM_model = LinearSVC(penalty='l2', 
                           loss='squared_hinge',
                           tol=0.0001,
                           C=0.9,
                           dual=False,
                           class_weight='balanced',
                           max_iter=1000
                          )
SVM_model = CalibratedClassifierCV(SVM_model) 
_algo = 'SVM'
# Training & testing the model on the imbanlance training-set.
_balance ='_None_'
_ratio = '*'
rs = rs.append(_train_and_test(SVM_model, data_train, _algo + _balance + _ratio),ignore_index=True)
#Training & testing the model on training-set with differrent ratio of Undersampling balancing method.
_balance ='_unsam_'
_ratio = '80_20'
rs = rs.append(_train_and_test(SVM_model, data_train_80_20, _algo + _balance + _ratio),ignore_index=True)
_ratio = '75_25'
rs = rs.append(_train_and_test(SVM_model, data_train_75_25, _algo+_balance+_ratio),ignore_index=True)
_ratio = '60_40'
rs = rs.append(_train_and_test(SVM_model, data_train_60_40, _algo+_balance+_ratio),ignore_index=True)
# Training & testing the model on training-set with differrent Oversampling balancing method.
from imblearn.pipeline import make_pipeline
from imblearn.over_sampling import (RandomOverSampler, SMOTE, BorderlineSMOTE, SVMSMOTE, ADASYN)

oversam = {0 : 'RandomOverSampler',
          1 : 'SMOTE',
          2 : 'BorderlineSMOTE',
          3 : 'SVMSMOTE',
          4 : 'ADASYN'}
_balance ='_oversam_'
for i, sampler in enumerate((RandomOverSampler(sampling_strategy = 1, random_state=0), 
                             SMOTE(sampling_strategy = 1, random_state=0),
                             BorderlineSMOTE(sampling_strategy = 1, random_state=0, kind='borderline-1'),
                             SVMSMOTE(sampling_strategy = 1, random_state=0),
                             ADASYN(sampling_strategy = 1, random_state=0))):
  pipe_line = make_pipeline(sampler, SVM_model)
  _ratio = oversam[i]
  rs = rs.append(_train_and_test(pipe_line, data_train, _algo + _balance + _ratio),ignore_index=True)
rs.to_csv('Class_BrainClass_SVM_rs.csv', header=True, sep=';', decimal=',') 