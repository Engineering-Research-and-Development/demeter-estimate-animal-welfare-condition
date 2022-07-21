"""
Estimate Animal Condition Module - Random Forest Training/Test and Prediction

Author: Luigi di Corrado
Mail: luigi.dicorrado@eng.it
Date: 17/12/2020
Company: Engineering Ingegneria Informatica S.p.A.

Introduction : This module is used to perform the training of the Random Forest algorithm,
               and create the models that will be used on prediction process to 
               estimate the health of the animals using two different classes of classification:
                   - Healthy
                   - Sick



Function     : initConfiguration

Description  : Set the current work directory and initialize the settings for Logger 
               and Random Forest Training/Prediction
               
Parameters   : string     confFile      contains the path to rfConf.properties to load
               string     workPath      path to work directory
               
Return       : 



Function     : measure

Description  : Execute the calculation of the following metrics data
               TP   - True Positive
               FP   - False Positive
               TN   - True Negative
               FN   - False Negative
               TPR  - True Positive Rate
               FPR  - False Positive Rate
               
Parameters   : dataframe  y_actual      contains the real solution data provided by the user
               dataframe  y_predict     contains the test prediction data provived by the training phase
               
Return       : float TP
               float FP
               float TN
               float FN
               float TPR
               float FPR



Function     : getDataFromTraslator

Description  : Retrieve the input data in AIM format from AIM Traslator service
               
Parameters   : str     url      AIM Traslator endpoint URL
               
Return       : dataset dataframe



Function     : execRFTraining

Description  : Converts the AIM input into a dataframe object, then process the data to fit the relative
               hillness and start the training phase for Random Forest algorithm.
               The data is splitted using 80% of the rows for Training and 20% for Testing.
               The random state "rs" argument is used to provide randomic rows while splitting the data.
               Once the training is complete a test prediction is executed on the dedicated rows and the
               models are saved into the configured folder.
               The metrics are calculated using accuracy_score, precision_score and measure functions.
               All the tested data and metrics are put together into the same Dataset
               and next converted into a CSV String and sent to AIM Traslator service.
               The response received will contain the AIM format of the output.
               
Parameters   : str   url                - String that contains AIM Traslator endpoint URL
               int   randomState        - Random state value for test phase, it choose random rows
               int   estimatorsNumbers  - Numbers of estimators to use on training phase
               
Return       : str   jsonResult   - String that contains all the AIM data to output



Function     : execRFPrediction

Description  : Converts the AIM input into a dataframe object, then process the data to fit the relative
               hillness and load the models before start the prediction using Random Forest.
               At the end of the process, the output data is converted into a CSV String and sent 
               to AIM Traslator service.
               
Parameters   : str   url          - String that contains AIM Traslator endpoint URL
               
Return       : str   jsonResult   - String that contains all the JSON data to output

"""

import pandas as pd
import datetime as dt
import joblib
import sys
import os
import json
import configparser
import requests
from decimal import Decimal
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from AWLogger import log

class AnimalWelfareRandomForest:
    def __init__(self):
       self.config = configparser.ConfigParser()
       self.myLog = log()
    
    def initConfiguration(self, confFile, workpath):
      os.chdir(workpath)
      self.config.read(confFile)
      self.myLog.initConfiguration(confFile)
      
    def measure(self, y_actual, y_predict):
        TP = 0
        FP = 0
        TN = 0
        FN = 0
        FPR = 0
        TPR = 0

        for i in range(len(y_predict)): 
            if y_actual[i] == y_predict[i] == 0:
                TP += 1
            if y_predict[i] == 0 and y_actual[i] != y_predict[i]:
                FP += 1
            if y_actual[i] == y_predict[i] == 1:
                TN += 1
            if y_predict[i] == 1 and y_actual[i] != y_predict[i]:
                FN += 1
        if (FP+TN) > 0:
            FPR = round((FP / (FP + TN)) * 100, 2)
        if (TP+FN) > 0:
            TPR = round((TP / (TP + FN)) * 100, 2)

        return(TP, FP, TN, FN, FPR, TPR)
      
    def getDataFromTraslator(self, url):
        functionName = sys._getframe().f_code.co_name
        self.myLog.writeMessage('Send request to: '+url,"DEBUG",functionName)
        resp = requests.post(url)
        self.myLog.writeMessage('Response received!',"DEBUG",functionName)
        try:
          # Json validation on loading
          myAIM = json.loads(resp.text)
        except:
          self.myLog.writeMessage('Exception! Invalid Json ...', "ERROR",functionName)
          self.myLog.writeMessage('Response BODY Content: '+resp.text, "ERROR",functionName)
          raise
        myGraph = myAIM['@graph']
        cols = ['Index','Date','Pedometer', 'Cow', 'MID', 'Lactations', 'Daily Production', 'Average Daily Production',
               'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3', 'Activity 1', 
               'Activity 2', 'Activity 3', 'Average Rumination Time 1', 'Average Rumination Time 2', 'Average Rumination Time 3', 
               'Average Ingestion Time 1', 'Average Ingestion Time 2', 'Average Ingestion Time 3', 'Total Daily Lying', 'ActualLameness', 'PredictedLameness',
               'ActualMastitis', 'PredictedMastitis', 'ActualKetosis', 'PredictedKetosis', 'ActualHeatStress', 'PredictedHeatStress']
        rows = []
        
        # Start the count at 1, because the @graph[0] element refer to metrics data storage.
        count = 1
        while count < len(myGraph):
            cow = myGraph[count]['livestockNumber']
            index = myGraph[count+1]['indentifier']
            date = myGraph[count+2]['resultTime']
            pedometer = myGraph[count+7]['hasResult'][0]['numericValue']
            mid = myGraph[count+8]['hasResult'][0]['numericValue']
            lactations = myGraph[count+9]['hasResult'][0]['numericValue']
            dailyprod = myGraph[count+10]['hasResult'][0]['numericValue']
            averagedp = myGraph[count+11]['hasResult'][0]['numericValue']
            dailyfat = myGraph[count+12]['hasResult'][0]['numericValue']
            dailyproteins = myGraph[count+13]['hasResult'][0]['numericValue']
            dailyfatproteins = myGraph[count+14]['hasResult'][0]['numericValue']
            tdl = myGraph[count+15]['hasResult'][0]['numericValue']
            
            if '#healthStatus-Healthy' in myGraph[count+16]['hasResult']:
                actuallameness = 'Healthy'
            elif '#healthStatus-Sick' in myGraph[count+16]['hasResult']:
                actuallameness = 'Sick'
            else:
                actuallameness = ''
                
            if '#healthStatus-Healthy' in myGraph[count+17]['hasResult']:
                predictedlameness = 'Healthy'
            elif '#healthStatus-Sick' in myGraph[count+17]['hasResult']:
                predictedlameness = 'Sick'
            else:
                predictedlameness = ''
            
            if '#healthStatus-Healthy' in myGraph[count+18]['hasResult']:
                actualketosis = 'Healthy'
            elif '#healthStatus-Sick' in myGraph[count+18]['hasResult']:
                actualketosis = 'Sick'
            else:
                actualketosis = ''
                
            if '#healthStatus-Healthy' in myGraph[count+19]['hasResult']:
                predictedketosis = 'Healthy'
            elif '#healthStatus-Sick' in myGraph[count+19]['hasResult']:
                predictedketosis = 'Sick'
            else:
                predictedketosis = ''
            
            if '#healthStatus-Healthy' in myGraph[count+20]['hasResult']:
                actualmastitis = 'Healthy'
            elif '#healthStatus-Sick' in myGraph[count+20]['hasResult']:
                actualmastitis = 'Sick'
            else:
                actualmastitis = ''
            
            if '#healthStatus-Healthy' in myGraph[count+21]['hasResult']:
                predictedmastitis = 'Healthy'
            elif '#healthStatus-Sick' in myGraph[count+21]['hasResult']:
                predictedmastitis = 'Sick'
            else:
                predictedmastitis = ''
                
            if '#healthStatus-Healthy' in myGraph[count+22]['hasResult']:
                actualHeatStress = 'Healthy'
            elif '#healthStatus-Stressed' in myGraph[count+22]['hasResult']:
                actualHeatStress = 'Stressed'
            else:
                actualHeatStress = ''
            
            if '#healthStatus-Healthy' in myGraph[count+23]['hasResult']:
                predictedHeatStress = 'Healthy'
            elif '#healthStatus-Stressed' in myGraph[count+23]['hasResult']:
                predictedHeatStress = 'Stressed'
            else:
                predictedHeatStress = ''
            
            cond1 = myGraph[count+24]['hasResult'][0]['numericValue']
            cond2 = myGraph[count+25]['hasResult'][0]['numericValue']
            cond3 = myGraph[count+26]['hasResult'][0]['numericValue']
            act1 = myGraph[count+27]['hasResult'][0]['numericValue']
            act2 = myGraph[count+28]['hasResult'][0]['numericValue']
            act3 = myGraph[count+29]['hasResult'][0]['numericValue']
            rum1 = myGraph[count+30]['hasResult'][0]['numericValue']
            rum2 = myGraph[count+31]['hasResult'][0]['numericValue']
            rum3 = myGraph[count+32]['hasResult'][0]['numericValue']
            ing1 = myGraph[count+33]['hasResult'][0]['numericValue']
            ing2 = myGraph[count+34]['hasResult'][0]['numericValue']
            ing3 = myGraph[count+35]['hasResult'][0]['numericValue']
        
            rows.append([index, date, pedometer, cow, mid, lactations, dailyprod, averagedp, dailyfat, dailyproteins, dailyfatproteins,
                         cond1, cond2, cond3, act1, act2, act3, rum1, rum2, rum3, ing1, ing2, ing3, tdl, actuallameness, predictedlameness,
                        actualmastitis, predictedmastitis, actualketosis, predictedketosis, actualHeatStress, predictedHeatStress])
            
            # Each animal takes 26 elements to store each data that will be used by Random Forest
            count += 36 
        
        dataframe = pd.DataFrame(rows, columns=cols)
        dataframe = dataframe.set_index('Index')
        dataframe = dataframe.apply(pd.to_numeric,errors='ignore')
        return dataframe
      
    def execRFTraining(self, url, randomState, estimatorsNumbers):
        # GET FUNCTION NAME
        functionName = sys._getframe().f_code.co_name       
        # Estimate Animal Welfare Condition - Training and Testing
        with self.myLog.error_debug():
            try:
                self.myLog.writeMessage("Working directory set to: "+os.path.abspath(os.getcwd()),"DEBUG",functionName)
                self.myLog.writeMessage("Module temp directory in use: "+os.path.join(os.path.dirname(__file__)),"DEBUG",functionName)
                # LOADING CONFIGURATION FROM PROPERTIES FILE
                self.myLog.writeMessage("Loading configuration from properties file...","DEBUG",functionName)
                
                # TRAINING SETTINGS
                #rs = int(config.get('PyRandomForest', 'animalwelfare.randomForest.trainingSettings.randomState'))  # Random State
                rs = randomState
                self.myLog.writeMessage("Random state set at: "+str(rs),"DEBUG",functionName)
                #estimators = int(config.get('PyRandomForest', 'animalwelfare.randomForest.trainingSettings.estimators'))
                estimators = estimatorsNumbers
                self.myLog.writeMessage("Estimators set at: "+str(estimators),"DEBUG",functionName)
                DataFolderPath = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.datafilePath')
                csvFileName = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.csvFileName')
                
                # Removed from configuration file.
                #metricsFileName = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.trainingMetricsFileName')
                
                # MODEL SETTINGS
                ModelFolderPath = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.modelfilePath')
                self.myLog.writeMessage("Model directory set at: "+ModelFolderPath,"DEBUG",functionName)
                PrefixModel = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.modelNamePrefix')
                self.myLog.writeMessage("Model name prefix set at: "+PrefixModel,"DEBUG",functionName)
                LamenessModelName = PrefixModel + 'LamenessModel'
                KetosisModelName = PrefixModel + 'KetosisModel'
                MastitisModelName = PrefixModel + 'MastitisModel'
                HeatStressModelName = PrefixModel + 'HeatStressModel'

                self.myLog.writeMessage('Preparing to execute Random Forest training phase of Estimate Animal Welfare Condition ...',"INFO",functionName)
                # Check if directory exists, or create it
                try:
                    self.myLog.writeMessage('Checking models directory ...',"DEBUG",functionName)
                    os.makedirs(ModelFolderPath)
                    self.myLog.writeMessage('Warning: Directory not found! ',"WARN",functionName)
                    self.myLog.writeMessage('Created directory: ' + os.path.realpath(ModelFolderPath), "DEBUG",functionName)
                except FileExistsError:
                    # Directory already exists
                    self.myLog.writeMessage('Directory already exists: ' + os.path.realpath(ModelFolderPath), "DEBUG",functionName)
                    pass
                
                try:
                    self.myLog.writeMessage('Checking models directory ...',"DEBUG",functionName)
                    os.makedirs(DataFolderPath)
                    self.myLog.writeMessage('Warning: Directory not found! ',"WARN",functionName)
                    self.myLog.writeMessage('Created directory: ' + os.path.realpath(DataFolderPath), "DEBUG",functionName)
                except FileExistsError:
                    # Directory already exists
                    self.myLog.writeMessage('Directory already exists: ' + os.path.realpath(DataFolderPath), "DEBUG",functionName)
                    pass

                # Dataset preparation
                self.myLog.writeMessage('Loading dataset ...',"DEBUG",functionName)
                #JsonObj = json.loads(JsonData)
                #dataframe = pd.DataFrame(JsonObj)
                dataframe= self.getDataFromTraslator(url)
                
                cols = ['Total Daily Lying', 'ActualLameness', 'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'ActualKetosis',
                        'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3', 'ActualMastitis', 'Average Rumination Time 1', 'Average Rumination Time 2', 
                        'Average Rumination Time 3', 'Average Ingestion Time 1', 'Average Ingestion Time 2', 'Average Ingestion Time 3', 'ActualHeatStress']
                dataset = dataframe[cols]
                self.myLog.writeMessage('Dataset successfully loaded!',"DEBUG",functionName)

                # Encoding non numeric columns using Label Encoder.
                self.myLog.writeMessage('Encoding labels ...',"DEBUG",functionName)
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
                
                leHeatStress = LabelEncoder()
                leHeatStress.fit(["Healthy", "Stressed"])  # Healthy = 0 , Stressed = 1
                leHeatStress.transform(dataset["ActualHeatStress"])
                dataset['ActualHeatStress'] = leHeatStress.transform(dataset['ActualHeatStress']).astype(int)
                
                self.myLog.writeMessage('Encoding labels successfully completed!',"DEBUG",functionName)

                # Random forest classification preparation
                # Defining the values: X contains values and actual solutions
                #                      y contain only solution column 
                #                      i is the index column
                self.myLog.writeMessage('Values definintion for classification ...',"DEBUG",functionName)
                Lameness_X = dataset.iloc[:, 0:1].values
                Lameness_y = dataset.iloc[:, 1].values
                Lameness_i = dataset.index.values

                Ketosis_X = dataset.iloc[:, 2:5].values
                Ketosis_y = dataset.iloc[:, 5].values
                Ketosis_i = dataset.index.values

                Mastitis_X = dataset.iloc[:, 6:9].values
                Mastitis_y = dataset.iloc[:, 9].values
                Mastitis_i = dataset.index.values
                
                HeatStress_X = dataset.iloc[:, 10:16].values
                HeatStress_y = dataset.iloc[:, 16].values
                HeatStress_i = dataset.index.values
                self.myLog.writeMessage('Values definintion for classification successfully completed!',"DEBUG",functionName)

                # Split data into training and test, and keep the index for each of them
                self.myLog.writeMessage('Defining training and test data ...',"DEBUG",functionName)
                Lameness_X_train, Lameness_X_test, Lameness_y_train, Lameness_y_test, Lameness_i_train, Lameness_i_test = train_test_split(
                  Lameness_X, Lameness_y, Lameness_i, test_size=0.20, random_state=rs)

                Ketosis_X_train, Ketosis_X_test, Ketosis_y_train, Ketosis_y_test, Ketosis_i_train, Ketosis_i_test = train_test_split(
                  Ketosis_X, Ketosis_y, Ketosis_i, test_size=0.20, random_state=rs)

                Mastitis_X_train, Mastitis_X_test, Mastitis_y_train, Mastitis_y_test, Mastitis_i_train, Mastitis_i_test = train_test_split(
                  Mastitis_X, Mastitis_y, Mastitis_i, test_size=0.20, random_state=rs)
                
                HeatStress_X_train, HeatStress_X_test, HeatStress_y_train, HeatStress_y_test, HeatStress_i_train, HeatStress_i_test = train_test_split(
                  HeatStress_X, HeatStress_y, HeatStress_i, test_size=0.20, random_state=rs)
                self.myLog.writeMessage('Training and test data definition completed!',"DEBUG",functionName)               

                # Training phase and testing
                self.myLog.writeMessage('Executing training and testing ...',"DEBUG",functionName)
                LamenessClassifier = RandomForestClassifier(n_estimators=estimators, random_state=rs)
                LamenessClassifier.fit(Lameness_X_train, Lameness_y_train)
                Lameness_y_pred = LamenessClassifier.predict(Lameness_X_test)

                KetosisClassifier = RandomForestClassifier(n_estimators=estimators, random_state=rs)
                KetosisClassifier.fit(Ketosis_X_train, Ketosis_y_train)
                Ketosis_y_pred = KetosisClassifier.predict(Ketosis_X_test)

                MastitisClassifier = RandomForestClassifier(n_estimators=estimators, random_state=rs)
                MastitisClassifier.fit(Mastitis_X_train, Mastitis_y_train)
                Mastitis_y_pred = MastitisClassifier.predict(Mastitis_X_test)
                
                HeatStressClassifier = RandomForestClassifier(n_estimators=estimators, random_state=rs)
                HeatStressClassifier.fit(HeatStress_X_train, HeatStress_y_train)
                HeatStress_y_pred = HeatStressClassifier.predict(HeatStress_X_test)
                self.myLog.writeMessage('Training and testing completed!',"DEBUG",functionName)

                # Saving models
                self.myLog.writeMessage('Saving models ...',"DEBUG",functionName)
                joblib.dump(LamenessClassifier, ModelFolderPath + '/' + LamenessModelName + '.pkl')
                joblib.dump(KetosisClassifier, ModelFolderPath + '/' + KetosisModelName + '.pkl')
                joblib.dump(MastitisClassifier, ModelFolderPath + '/' + MastitisModelName + '.pkl')
                joblib.dump(HeatStressClassifier, ModelFolderPath + '/' + HeatStressModelName + '.pkl')

                self.myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + LamenessModelName + '.pkl', "DEBUG",functionName)
                self.myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + KetosisModelName + '.pkl', "DEBUG",functionName)
                self.myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + MastitisModelName + '.pkl', "DEBUG",functionName)
                self.myLog.writeMessage('Model saved : ' + os.path.realpath(ModelFolderPath) + '/' + HeatStressModelName + '.pkl', "DEBUG",functionName)
                self.myLog.writeMessage('Models successfully saved!',"DEBUG",functionName)

                # Metrics
                self.myLog.writeMessage('Executing metrics calculations ...',"DEBUG",functionName)
                # Accuracy score
                self.myLog.writeMessage('Calculating accuracy score ...',"DEBUG",functionName)
                LamenessAccuracy = accuracy_score(Lameness_y_test, Lameness_y_pred) * 100
                KetosisAccuracy = accuracy_score(Ketosis_y_test, Ketosis_y_pred) * 100
                MastitisAccuracy = accuracy_score(Mastitis_y_test, Mastitis_y_pred) * 100
                HeatStressAccuracy = accuracy_score(HeatStress_y_test, HeatStress_y_pred) * 100
                self.myLog.writeMessage('Accuracy score calculated!',"DEBUG",functionName)

                # Precision score
                self.myLog.writeMessage('Calculating precision scores ...',"DEBUG",functionName)
                LamenessPrecision = round(precision_score(Lameness_y_test, Lameness_y_pred, average='macro') * 100,1)
                KetosisPrecision = round(precision_score(Ketosis_y_test, Ketosis_y_pred, average='micro') * 100,1)
                MastitisPrecision = round(precision_score(Mastitis_y_test, Mastitis_y_pred, average='micro') * 100,1)
                HeatStressPrecision = round(precision_score(HeatStress_y_test, HeatStress_y_pred, average='micro') * 100,1)
                self.myLog.writeMessage('Precision score calculated!',"DEBUG",functionName)
                
                # True positive, false positive, true negative, false negative, true positive rate, false positive rate
                self.myLog.writeMessage('Calculating true positive rate and false positive rate ...',"DEBUG",functionName)
                Lameness_TP, Lameness_FP, Lameness_TN, Lameness_FN, Lameness_FPR, Lameness_TPR = self.measure(Lameness_y_test, Lameness_y_pred)
                Ketosis_TP, Ketosis_FP, Ketosis_TN, Ketosis_FN, Ketosis_FPR, Ketosis_TPR = self.measure(Ketosis_y_test, Ketosis_y_pred)
                Mastitis_TP, Mastitis_FP, Mastitis_TN, Mastitis_FN, Mastitis_FPR, Mastitis_TPR = self.measure(Mastitis_y_test, Mastitis_y_pred)
                HeatStress_TP, HeatStress_FP, HeatStress_TN, HeatStress_FN, HeatStress_FPR, HeatStress_TPR = self.measure(HeatStress_y_test, HeatStress_y_pred)

                metricsDict = {'lamenessTruePositiveRate': [Lameness_TPR], 'lamenessFalsePositiveRate': [Lameness_FPR], 'lamenessPrecision': [LamenessPrecision], 'lamenessAccuracy': [LamenessAccuracy],
                               'mastitisTruePositiveRate': [Mastitis_TPR], 'mastitisFalsePositiveRate': [Mastitis_FPR], 'mastitisPrecision': [MastitisPrecision], 'mastitisAccuracy': [MastitisAccuracy],
                               'ketosisTruePositiveRate': [Ketosis_TPR], 'ketosisFalsePositiveRate': [Ketosis_FPR], 'ketosisPrecision': [KetosisPrecision], 'ketosisAccuracy': [KetosisAccuracy],
                               'heatStressTruePositiveRate': [HeatStress_TPR], 'heatStressFalsePositiveRate': [HeatStress_FPR], 'heatStressPrecision': [HeatStressPrecision], 'heatStressAccuracy': [HeatStressAccuracy]}
                self.myLog.writeMessage('True positive rate and false positive rate calculated!',"DEBUG",functionName)
                dsMetrics = pd.DataFrame(metricsDict)
                self.myLog.writeMessage('Metrics calculations completed!',"DEBUG",functionName)

                # Creating an output dataset with test data results
                self.myLog.writeMessage('Preparing output dataset ...',"DEBUG",functionName)
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
                dfActualHeatStress = pd.DataFrame(leHeatStress.inverse_transform(HeatStress_y_test))
                dfActualHeatStress = dfActualHeatStress.set_index(indices)
                dfActualHeatStress.columns = ['ActualHeatStress']
                dfPredictedHeatStress = pd.DataFrame(leHeatStress.inverse_transform(HeatStress_y_pred))
                dfPredictedHeatStress = dfPredictedHeatStress.set_index(indices)
                dfPredictedHeatStress.columns = ['PredictedHeatStress']

                cols = ['Date', 'Pedometer', 'Cow', 'MID', 'Lactations', 'Daily Production', 'Average Daily Production',
                        'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3',
                        'Activity 1', 'Activity 2', 'Activity 3', 'Total Daily Lying',
                        'Average Rumination Time 1', 'Average Rumination Time 2', 'Average Rumination Time 3', 
                        'Average Ingestion Time 1', 'Average Ingestion Time 2', 'Average Ingestion Time 3']

                dsPredictions = dataframe[cols].loc[indices].join([dfActualLameness, dfPredictedLameness, 
                                                          dfActualKetosis, dfPredictedKetosis, 
                                                          dfActualMastitis, dfPredictedMastitis, 
                                                          dfActualHeatStress, dfPredictedHeatStress])
                dsPredictions.sort_index(inplace=True)
                #dsPredictions['Date'] = pd.to_datetime(dsPredictions['Date'], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')
                dsPredictions = dsPredictions.reset_index()
                self.myLog.writeMessage('Output dataset preparation completed!', "DEBUG",functionName)
                
                # Convert dataset predictions to AIM using traslator service
                self.myLog.writeMessage('Converting output datasets to AIM ...',"DEBUG",functionName)

                # Convert dataset predictions to CSV
                self.myLog.writeMessage('Creating CSV file: '+DataFolderPath+'/'+csvFileName,"DEBUG",functionName)
                dsPredictions = pd.concat([dsPredictions,dsMetrics],axis=1, sort=False)
                csvDataset = dsPredictions.to_csv(DataFolderPath+'/'+csvFileName, sep=';', index=False)
                
                # Convert dataset predictions to json using records orientation
                jsonMetrics = dsMetrics.to_json(orient='records')
                self.myLog.writeMessage('Conversion completed!',"DEBUG",functionName)  
                
                self.myLog.writeMessage('Converting CSV to String...',"DEBUG",functionName) 
                with open(DataFolderPath+'/'+csvFileName) as csvFile:
                  csvContent = csvFile.read()
                self.myLog.writeMessage('Conversion completed!',"DEBUG",functionName)
                
                self.myLog.writeMessage('Send request to: '+url,"DEBUG",functionName)
                resp = requests.post(url,data = csvContent)
                jsonDataset = resp.text

                self.myLog.writeMessage('Processing JSON output ...',"DEBUG",functionName)
                # Decode the json data created to insert a custom root element
                #self.myLog.writeMessage('Adding roots to JSON ...',"DEBUG",functionName)
                jsonDataset_decoded = json.loads(jsonDataset)
                #jsonDataset_decoded = {'animalData': jsonDataset_decoded}
                #jsonMetrics_decoded = json.loads(jsonMetrics)
                #jsonMetrics_decoded = {'metricsData': jsonMetrics_decoded}
                #self.myLog.writeMessage('Roots successfully added!',"DEBUG",functionName)

                # Decode json that contains metrics element and update the prediction json
                #self.myLog.writeMessage('Processing JSON output ...',"DEBUG",functionName)
                #jsonDataset_decoded.update(jsonMetrics_decoded)
                #with open(DataFolderPath+'/'+metricsFileName, 'w') as outfile:
                #  json.dump(jsonMetrics_decoded, outfile)

                jsonResult = json.dumps(jsonDataset_decoded, indent=4, sort_keys=False)
                self.myLog.writeMessage('JSON output successfully processed!',"DEBUG",functionName)
                
                #self.myLog.writeMessage('Removing useless files ...',"DEBUG",functionName)
                #if os.path.exists(DataFolderPath+'/'+csvFileName):
                #  os.remove(DataFolderPath+'/'+csvFileName)
                #else:
                #  self.myLog.writeMessage('The file '+DataFolderPath+'/'+csvFileName+' does not exists!',"DEBUG",functionName)
                #self.myLog.writeMessage('Removing useless files successfully completed!',"DEBUG",functionName)
                
                self.myLog.writeMessage('Estimate Animal Welfare Condition training and test completed!',"INFO",functionName)
                self.myLog.writeMessage('==============================================================',"INFO",functionName)
                return jsonResult
            except:
                self.myLog.writeMessage('An exception occured!', "ERROR",functionName)
                raise
                
    def execRFPrediction(self, url):    
        # GET FUNCTION NAME
        functionName = sys._getframe().f_code.co_name
        
        with self.myLog.error_debug():
            try:
                self.myLog.writeMessage("Working directory set to: "+os.path.abspath(os.getcwd()),"DEBUG",functionName)
                self.myLog.writeMessage("Module temp directory in use: "+os.path.join(os.path.dirname(__file__)),"DEBUG",functionName)
                
                # LOADING CONFIGURATION FROM PROPERTIES FILE
                self.myLog.writeMessage("Loading configuration from properties file...","DEBUG",functionName)
                
                # LOADING MODELS SETTINGS
                modelsNotExists = False
                ModelFolderPath = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.modelfilePath')
                self.myLog.writeMessage("Model directory set at: "+ModelFolderPath,"DEBUG",functionName)
                PrefixModel = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.modelNamePrefix')
                self.myLog.writeMessage("Model name prefix set at: "+PrefixModel,"DEBUG",functionName)
                LamenessModelName = PrefixModel + 'LamenessModel'
                KetosisModelName = PrefixModel + 'KetosisModel'
                MastitisModelName = PrefixModel + 'MastitisModel'
                HeatStressModelName = PrefixModel + 'HeatStressModel'
                DataFolderPath = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.datafilePath')
                csvFileName = self.config.get('PyRandomForest', 'animalwelfare.randomForest.commonSettings.csvFileName')

  
                self.myLog.writeMessage('Preparing to execute Random Forest Predictions of Estimate Animal Welfare Condition ...',"INFO",functionName)
                # Estimate Animal Welfare Condition - Prediction
        
                
                # Check if models folder exists
                self.myLog.writeMessage('Checking models folder ...',"DEBUG",functionName)
                if (os.path.exists(ModelFolderPath)):
                    pass
                else :
                    self.myLog.writeMessage('Error! Folder '+ModelFolderPath+' not found!',"ERROR",functionName)
                    self.myLog.writeMessage('Sending error message ...',"DEBUG",functionName)
                    errorData = {"Code": "2",
                                 "Type" : "Models directory not found",
                                 "Description": "The models directory is missing. Please execute the training first."}
                    jsonResult = json.dumps(errorData, indent=4, sort_keys=False)
                    self.myLog.writeMessage('Error sent!',"DEBUG",functionName)
                    return jsonResult
                
                # Check if models file exists
                self.myLog.writeMessage('Checking saved models files ...',"DEBUG",functionName)
                if (os.path.exists(ModelFolderPath + '/' + LamenessModelName + '.pkl') and
                    os.path.exists(ModelFolderPath + '/' + KetosisModelName + '.pkl') and
                    os.path.exists(ModelFolderPath + '/' + MastitisModelName + '.pkl') and
                    os.path.exists(ModelFolderPath + '/' + HeatStressModelName + '.pkl')):
                    self.myLog.writeMessage('Models files found!',"DEBUG",functionName)
                    pass
                else :
                    # Models not exists
                    self.myLog.writeMessage('Error! Models files not found!',"ERROR",functionName)
                    self.myLog.writeMessage('Listing existing fiels ...',"DEBUG",functionName)
                    filesNames = []
                    modelsNotExists = True
                    existingfiles = [f for f in os.listdir(ModelFolderPath) if os.path.isfile(os.path.join(ModelFolderPath, f))]
                    for i in existingfiles :
                        modelPrefix = i.split('_')[:-1]
                        if not(modelPrefix in filesNames):
                            filesNames.append(modelPrefix)
                    self.myLog.writeMessage('Listing existing files completed!',"DEBUG",functionName)

                if not(modelsNotExists):
                    # Dataset preparation
                    self.myLog.writeMessage('Loading dataset ...',"DEBUG",functionName)
                    #JsonObj = json.loads(JsonData)
                    #dataframe = pd.DataFrame(JsonObj)
                    #dataframe = dataframe.set_index('Index')
                    dataframe= self.getDataFromTraslator(url)

                    LamenessCols = ['Total Daily Lying']
                    KetosisCols = ['Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins']
                    MastitisCols = ['Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3']
                    HeatStressCols = ['Average Rumination Time 1', 'Average Rumination Time 2', 'Average Rumination Time 3', 
                                      'Average Ingestion Time 1', 'Average Ingestion Time 2', 'Average Ingestion Time 3']

                    LamenessDS = dataframe[LamenessCols]
                    KetosisDS = dataframe[KetosisCols]
                    MastitisDS = dataframe[MastitisCols]
                    HeatStressDS = dataframe[HeatStressCols]
                    self.myLog.writeMessage('Dataset successfully loaded!',"DEBUG",functionName)

                    # Loading random forest saved models
                    self.myLog.writeMessage('Loading models ...',"DEBUG",functionName)
                    LamenessClassifier = joblib.load(ModelFolderPath + '/' + LamenessModelName + '.pkl')
                    KetosisClassifier = joblib.load(ModelFolderPath + '/' + KetosisModelName + '.pkl')
                    MastitisClassifier = joblib.load(ModelFolderPath + '/' + MastitisModelName + '.pkl')
                    HeatStressClassifier = joblib.load(ModelFolderPath + '/' + HeatStressModelName + '.pkl')
                    self.myLog.writeMessage('Models successfully loaded!',"DEBUG",functionName)

                    # Execute predictions
                    self.myLog.writeMessage('Executing predictions ...',"DEBUG",functionName)
                    LamenessPred = LamenessClassifier.predict(LamenessDS)
                    KetosisPred = KetosisClassifier.predict(KetosisDS)
                    MastitisPred = MastitisClassifier.predict(MastitisDS)
                    HeatStressPred = HeatStressClassifier.predict(HeatStressDS)
                    self.myLog.writeMessage('Predictions successfully completed!',"DEBUG",functionName)

                    # Predictions output preparation
                    self.myLog.writeMessage('Output preparation ...',"DEBUG",functionName)
                    le = LabelEncoder()
                    leHeatStress = LabelEncoder()
                    le.fit(['Healthy','Sick']) # Healthy = 0 , Sick = 1
                    leHeatStress.fit(['Healthy','Stressed']) # Healthy = 0 , Stressed = 1
                    dataframe['PredictedLameness'] = le.inverse_transform(LamenessPred)
                    dataframe['PredictedKetosis'] = le.inverse_transform(KetosisPred)
                    dataframe['PredictedMastitis'] = le.inverse_transform(MastitisPred)
                    dataframe['PredictedHeatStress'] = leHeatStress.inverse_transform(HeatStressPred)
                    dataframe = dataframe.reset_index()
                    self.myLog.writeMessage('Output preparation completed!',"DEBUG",functionName)
                    
                    # Convert dataset predictions to AIM using traslator service
                    self.myLog.writeMessage('Converting output datasets to AIM ...',"DEBUG",functionName)
                    
                    # Convert dataset predictions to CSV
                    self.myLog.writeMessage('Creating CSV file: '+DataFolderPath+'/'+csvFileName,"DEBUG",functionName)
                    csvDataset = dataframe.to_csv(DataFolderPath+'/'+csvFileName, sep=';', index=False)
                    
                    self.myLog.writeMessage('Converting CSV to String...',"DEBUG",functionName) 
                    with open(DataFolderPath+'/'+csvFileName) as csvFile:
                      csvContent = csvFile.read()
                    self.myLog.writeMessage('Conversion completed!',"DEBUG",functionName)
                    
                    self.myLog.writeMessage('Send request to: '+url,"DEBUG",functionName)
                    resp = requests.post(url,data = csvContent)
                    jsonDataset = resp.text

                    # Convert dataset predictions to json using records orientation
                    #self.myLog.writeMessage('Converting output dataset to JSON ...',"DEBUG",functionName)
                    #jsonDataset = dataframe.to_json(orient='records')
                    #self.myLog.writeMessage('Conversion completed!',"DEBUG",functionName)  

                    # Decode the json data created to insert a custom root element
                    #self.myLog.writeMessage('Adding roots to JSON ...',"DEBUG",functionName)
                    jsonDataset_decoded = json.loads(jsonDataset)
                    #jsonDataset_decoded = {'animalData': jsonDataset_decoded}
                    #self.myLog.writeMessage('Roots successfully added!',"DEBUG",functionName)

                    # Process JSON output
                    self.myLog.writeMessage('Processing JSON output ...',"DEBUG",functionName)
                    jsonResult = json.dumps(jsonDataset_decoded, indent=4, sort_keys=False)
                    self.myLog.writeMessage('JSON output successfully processed!',"DEBUG",functionName)
                    
                    #self.myLog.writeMessage('Removing useless files ...',"DEBUG",functionName)
                    #if os.path.exists(DataFolderPath+'/'+csvFileName):
                    #  os.remove(DataFolderPath+'/'+csvFileName)
                    #else:
                    #  self.myLog.writeMessage('The file '+DataFolderPath+'/'+csvFileName+' does not exists!',"DEBUG",functionName)
                    #self.myLog.writeMessage('Removing useless files successfully completed!',"DEBUG",functionName)
                    
                    self.myLog.writeMessage('Estimate Animal Welfare Condition predictions completed!',"INFO",functionName)
                    self.myLog.writeMessage('==============================================================',"INFO",functionName)
                    return jsonResult
                else :
                    if len(existingfiles) < 1 :
                        self.myLog.writeMessage('Error! The folder is empty!',"ERROR",functionName)
                        self.myLog.writeMessage('Sending error message ...',"DEBUG",functionName)
                        errorData = {"Code": "2",
                                     "Type" : "No models saved",
                                     "Description": "There are no models saved. Please execute the training first."}
                        jsonResult = json.dumps(errorData, indent=4, sort_keys=False)
                        self.myLog.writeMessage('Error sent!',"DEBUG",functionName)
                        return jsonResult
                    else :
                        self.myLog.writeMessage('Error! Model name not found!',"ERROR",functionName)
                        self.myLog.writeMessage('Found '+str(len(filesNames))+' models names:'+ str(filesNames),"ERROR",functionName)
                        self.myLog.writeMessage('Sending error message ...',"DEBUG",functionName)
                        errorData = {"Code": "2",
                                     "Type" : "Models not found",
                                     "Description": "Models not found for the animal type: "+PrefixModel}
                        jsonResult = json.dumps(errorData, indent=4, sort_keys=False)
                        self.myLog.writeMessage('Error sent!',"DEBUG",functionName)
                        return jsonResult
            except:
                self.myLog.writeMessage('An exception occured!', "ERROR",functionName)
                raise