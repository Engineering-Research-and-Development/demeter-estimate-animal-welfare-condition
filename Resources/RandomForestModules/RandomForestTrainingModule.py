import pandas as pd
import datetime as dt
import joblib
import sys
import os
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from Logger import log

class RandomForest: 
    # FUNCTIONS         
    # True Positive, False Positive, True Negative, False Negative, False Positive Rate, True Positive Rate calculation function
    def measure(self, y_actual, y_predict):
        TP = 0
        FP = 0
        TN = 0
        FN = 0

        for i in range(len(y_predict)): 
            if y_actual[i] == y_predict[i] == 0:
                TP += 1
            if y_predict[i] == 0 and y_actual[i] != y_predict[i]:
                FP += 1
            if y_actual[i] == y_predict[i] == 1:
                TN += 1
            if y_predict[i] == 1 and y_actual[i] != y_predict[i]:
                FN += 1

        FPR = round((FP / (FP + TN)) * 100, 2)
        TPR = round((TP / (TP + FN)) * 100, 2)

        return(TP, FP, TN, FN, FPR, TPR)
  
    def execRFTraining(self, JsonData):
        # LOGGING SETTINGS
        functionName = sys._getframe().f_code.co_name
        myLog = log()
        
        # TRAINING SETTINGS
        rs = 0  # Random State
        
        # MODEL SETTINGS
        ModelFolderPath = './models'
        PrefixModel = 'Cow'
        LamenessModelName = PrefixModel + '_LamenessModel'
        KetosisModelName = PrefixModel + '_KetosisModel'
        MastitisModelName = PrefixModel + '_MastitisModel'

        # HEALTH PREDICTIONS TRAINING / TEST ALGORITHM
        with myLog.error_debug():
            try:
                myLog.writeMessage('Preparing to execute Random Forest training phase of Estimate Animal Welfare Condition ...',3,functionName)

                # Check if directory exists, or create it
                try:
                    myLog.writeMessage('Checking models directory ...',3,functionName)
                    os.makedirs(ModelFolderPath)
                    myLog.writeMessage('Warning: Directory not found! ',2,functionName)
                    myLog.writeMessage('Created directory: ' + os.path.realpath(ModelFolderPath), 1,functionName)
                except FileExistsError:
                    # Directory already exists
                    myLog.writeMessage('Directory already exists: ' + os.path.realpath(ModelFolderPath), 3,functionName)
                    pass

                # Dataset preparation
                myLog.writeMessage('Loading dataset ...',3,functionName)
                JsonObj = json.loads(JsonData)
                dataframe = pd.DataFrame(JsonObj)
                dataframe = dataframe.set_index('Index')
                cols = ['Total Daily Lying', 'ActualLameness', 'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'ActualKetosis',
                        'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3', 'ActualMastitis']
                dataset = dataframe[cols]
                myLog.writeMessage('Dataset successfully loaded!',1,functionName)

                # Encoding non numeric columns using Label Encoder.
                myLog.writeMessage('Encoding labels ...',3,functionName)
                leLameness = LabelEncoder()
                leLameness.fit(["Healthy", "Sick"])  # Healthy = 0 , Sick = 1
                leLameness.transform(dataset["ActualLameness"])
                dataset['ActualLameness'] = leLameness.transform(dataset['ActualLameness']).astype(int)

                leKetosis = LabelEncoder()
                leKetosis.fit(["Healthy", "Sick"])  # Healthy = 0 , Sick = 1
                leKetosis.transform(dataset["ActualKetosis"])
                dataset['ActualKetosis'] = leKetosis.transform(dataset['ActualKetosis']).astype(int)

                leMastitis = LabelEncoder()
                leMastitis.fit(["Healthy", "Sick"])  # Healthy = 0 , Sick = 1
                leMastitis.transform(dataset["ActualMastitis"])
                dataset['ActualMastitis'] = leMastitis.transform(dataset['ActualMastitis']).astype(int)
                myLog.writeMessage('Encoding labels successfully completed!',1,functionName)

                # Random forest classification preparation
                # Defining the values: X contains values and actual solutions
                #                      y contain only solution column 
                #                      i is the index column
                myLog.writeMessage('Values definintion for classification ...',3,functionName)
                Lameness_X = dataset.iloc[:, 0:1].values
                Lameness_y = dataset.iloc[:, 1].values
                Lameness_i = dataset.index.values

                Ketosis_X = dataset.iloc[:, 2:5].values
                Ketosis_y = dataset.iloc[:, 5].values
                Ketosis_i = dataset.index.values

                Mastitis_X = dataset.iloc[:, 6:9].values
                Mastitis_y = dataset.iloc[:, 9].values
                Mastitis_i = dataset.index.values
                myLog.writeMessage('Values definintion for classification successfully completed!',1,functionName)

                # Split data into training and test, and keep the index for each of them
                myLog.writeMessage('Defining training and test data ...',3,functionName)
                Lameness_X_train, Lameness_X_test, Lameness_y_train, Lameness_y_test, Lameness_i_train, Lameness_i_test = train_test_split(
                  Lameness_X, Lameness_y, Lameness_i, test_size=0.20, random_state=rs)

                Ketosis_X_train, Ketosis_X_test, Ketosis_y_train, Ketosis_y_test, Ketosis_i_train, Ketosis_i_test = train_test_split(
                  Ketosis_X, Ketosis_y, Ketosis_i, test_size=0.20, random_state=rs)

                Mastitis_X_train, Mastitis_X_test, Mastitis_y_train, Mastitis_y_test, Mastitis_i_train, Mastitis_i_test = train_test_split(
                  Mastitis_X, Mastitis_y, Mastitis_i, test_size=0.20, random_state=rs)
                myLog.writeMessage('Training and test data definition completed!',3,functionName)               

                # Training phase and testing
                myLog.writeMessage('Executing training and testing ...',3,functionName)
                LamenessClassifier = RandomForestClassifier(n_estimators=100, random_state=rs)
                LamenessClassifier.fit(Lameness_X_train, Lameness_y_train)
                Lameness_y_pred = LamenessClassifier.predict(Lameness_X_test)

                KetosisClassifier = RandomForestClassifier(n_estimators=100, random_state=rs)
                KetosisClassifier.fit(Ketosis_X_train, Ketosis_y_train)
                Ketosis_y_pred = KetosisClassifier.predict(Ketosis_X_test)

                MastitisClassifier = RandomForestClassifier(n_estimators=100, random_state=rs)
                MastitisClassifier.fit(Mastitis_X_train, Mastitis_y_train)
                Mastitis_y_pred = MastitisClassifier.predict(Mastitis_X_test)
                myLog.writeMessage('Training and testing completed!',1,functionName)

                # Saving models
                myLog.writeMessage('Saving models ...',3,functionName)
                joblib.dump(LamenessClassifier, ModelFolderPath + '/' + LamenessModelName + '.pkl')
                joblib.dump(KetosisClassifier, ModelFolderPath + '/' + KetosisModelName + '.pkl')
                joblib.dump(MastitisClassifier, ModelFolderPath + '/' + MastitisModelName + '.pkl')

                myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + LamenessModelName + '.pkl', 3,functionName)
                myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + KetosisModelName + '.pkl', 3,functionName)
                myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + MastitisModelName + '.pkl', 3,functionName)
                myLog.writeMessage('Models successfully saved!',1,functionName)

                # Metrics
                myLog.writeMessage('Executing metrics calculations ...',3,functionName)
                # Accuracy score
                myLog.writeMessage('Calculating accuracy score ...',3,functionName)
                LamenessAccuracy = accuracy_score(Lameness_y_test, Lameness_y_pred) * 100
                KetosisAccuracy = accuracy_score(Ketosis_y_test, Ketosis_y_pred) * 100
                MastitisAccuracy = accuracy_score(Mastitis_y_test, Mastitis_y_pred) * 100
                myLog.writeMessage('Accuracy score calculated!',1,functionName)

                # Precision score
                myLog.writeMessage('Calculating precision scores ...',3,functionName)
                LamenessPrecision = round(precision_score(Lameness_y_test, Lameness_y_pred, average='macro') * 100,1)
                KetosisPrecision = round(precision_score(Ketosis_y_test, Ketosis_y_pred, average='micro') * 100,1)
                MastitisPrecision = round(precision_score(Mastitis_y_test, Mastitis_y_pred, average='micro') * 100,1)
                myLog.writeMessage('Precision score calculated!',1,functionName)
                
                # True positive, false positive, true negative, false negative, true positive rate, false positive rate
                myLog.writeMessage('Calculating true positive rate and false positive rate ...',3,functionName)
                Lameness_TP, Lameness_FP, Lameness_TN, Lameness_FN, Lameness_FPR, Lameness_TPR = self.measure(Lameness_y_test, Lameness_y_pred)
                Ketosis_TP, Ketosis_FP, Ketosis_TN, Ketosis_FN, Ketosis_FPR, Ketosis_TPR = self.measure(Ketosis_y_test, Ketosis_y_pred)
                Mastitis_TP, Mastitis_FP, Mastitis_TN, Mastitis_FN, Mastitis_FPR, Mastitis_TPR = self.measure(Mastitis_y_test, Mastitis_y_pred)

                metricsDict = {'LAMENESS_TRUE_POSITIVE_RATE': [Lameness_TPR], 'LAMENESS_FALSE_POSITIVE_RATE': [Lameness_FPR], 'LAMENESS_PRECISION': [LamenessPrecision], 'LAMENESS_ACCURACY': [LamenessAccuracy],
                               'MASTITIS_TRUE_POSITIVE_RATE': [Mastitis_TPR], 'MASTITIS_FALSE_POSITIVE_RATE': [Mastitis_FPR], 'MASTITIS_PRECISION': [MastitisPrecision], 'MASTITIS_ACCURACY': [MastitisAccuracy],
                               'KETOSIS_TRUE_POSITIVE_RATE': [Ketosis_TPR], 'KETOSIS_FALSE_POSITIVE_RATE': [Ketosis_FPR], 'KETOSIS_PRECISION': [KetosisPrecision], 'KETOSIS_ACCURACY': [KetosisAccuracy]}
                myLog.writeMessage('True positive rate and false positive rate calculated!',1,functionName)
                dsMetrics = pd.DataFrame(metricsDict)
                myLog.writeMessage('Metrics calculations completed!',1,functionName)

                # Creating an output dataset with test data results
                myLog.writeMessage('Preparing output dataset ...',3,functionName)
                indices = Lameness_i_test
                dfActualLameness = pd.DataFrame(leLameness.inverse_transform(Lameness_y_test))
                dfActualLameness = dfActualLameness.set_index(indices)
                dfActualLameness.columns = ['ActualLameness']
                dfPredictedLameness = pd.DataFrame(leLameness.inverse_transform(Lameness_y_pred))
                dfPredictedLameness = dfPredictedLameness.set_index(indices)
                dfPredictedLameness.columns = ['PredictedLameness']
                dfActualKetosis = pd.DataFrame(leKetosis.inverse_transform(Ketosis_y_test))
                dfActualKetosis = dfActualKetosis.set_index(indices)
                dfActualKetosis.columns = ['ActualKetosis']
                dfPredictedKetosis = pd.DataFrame(leKetosis.inverse_transform(Ketosis_y_pred))
                dfPredictedKetosis = dfPredictedKetosis.set_index(indices)
                dfPredictedKetosis.columns = ['PredictedKetosis']
                dfActualMastitis = pd.DataFrame(leMastitis.inverse_transform(Mastitis_y_test))
                dfActualMastitis = dfActualMastitis.set_index(indices)
                dfActualMastitis.columns = ['ActualMastitis']
                dfPredictedMastitis = pd.DataFrame(leMastitis.inverse_transform(Mastitis_y_pred))
                dfPredictedMastitis = dfPredictedMastitis.set_index(indices)
                dfPredictedMastitis.columns = ['PredictedMastitis']

                cols = ['Date', 'Pedometer', 'Cow', 'MID', 'Lactations', 'Daily Production', 'Average Daily Production',
                        'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3',
                        'Activity 1', 'Activity 2', 'Activity 3', 'Total Daily Lying']

                dsPredictions = dataframe[cols].loc[indices].join([dfActualLameness, dfPredictedLameness, 
                                                          dfActualKetosis, dfPredictedKetosis, 
                                                          dfActualMastitis, dfPredictedMastitis])
                dsPredictions.sort_index(inplace=True)
                dsPredictions['Date'] = pd.to_datetime(dsPredictions['Date'], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')
                dsPredictions = dsPredictions.reset_index()
                myLog.writeMessage('Output dataset preparation completed!', 1,functionName)

                # Convert dataset predictions to json using records orientation
                myLog.writeMessage('Converting output datasets to JSON ...',3,functionName)
                jsonDataset = dsPredictions.to_json(orient='records')
                jsonMetrics = dsMetrics.to_json(orient='records')
                myLog.writeMessage('Conversion completed!',1,functionName)  

                # Decode the json data created to insert a custom root element
                myLog.writeMessage('Adding roots to JSON ...',3,functionName)
                jsonDataset_decoded = json.loads(jsonDataset)
                jsonDataset_decoded = {'animalData': jsonDataset_decoded}
                jsonMetrics_decoded = json.loads(jsonMetrics)
                jsonMetrics_decoded = {'metrics': jsonMetrics_decoded}
                myLog.writeMessage('Roots successfully added!',1,functionName)

                # Decode json that contains metrics element and update the prediction json
                myLog.writeMessage('Processing JSON output ...',3,functionName)
                jsonDataset_decoded.update(jsonMetrics_decoded)

                jsonResult = json.dumps(jsonDataset_decoded, indent=4, sort_keys=False)
                myLog.writeMessage('JSON output successfully processed!',1,functionName)
                myLog.writeMessage('Estimate Animal Welfare Condition training and test completed!',1,functionName)
                myLog.writeMessage('==============================================================',4,functionName)
                return jsonResult
            except:
                myLog.writeMessage('Warning an exception occured!', 2,functionName)
                raise
