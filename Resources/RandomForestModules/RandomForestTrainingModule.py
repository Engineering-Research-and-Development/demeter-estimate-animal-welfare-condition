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

class RandomForest:


    # !!! INPUT DATASET
    #dataframe = pd.read_csv('HealthPredictions_Training_DS.csv', sep=";")
  
  
    # FUNCTIONS
    # Log file message, create a directory and write a file with log messages
    def LogMessage(self, Message, Result):
        folder = './logs'
        filename = 'Random_forest_log.log'
        fullpath = folder + '/' + filename
        try:
            # Check if directory exists, or create it
            os.makedirs(folder)
        except FileExistsError:
            # Directory already exists
            pass
        if os.path.exists(fullpath):
            append_write = 'a'  # append
        else:
            append_write = 'w'  # new file

        log = open(fullpath, append_write)
        try:
            log.write('[' + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] -- ' + Message + ' [' + Result + ']' + '\n')
        finally:
            log.close()
          
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
        # SETTINGS FOR TRAINING SETUP AND MODEL SAVE
        rs = 0  # Random State
        ModelFolderPath = './models'
        PrefixModel = 'Cow'
        LamenessModelName = PrefixModel + '_LamenessModel'
        KetosisModelName = PrefixModel + '_KetosisModel'
        MastitisModelName = PrefixModel + '_MastitisModel'
        # HEALTH PREDICTIONS TRAINING / TEST ALGORITHM
        try:
            self.LogMessage('Health predictions training and test algorithm start ...', 'OK')

            # Check if directory exists, or create it
            try:
                os.makedirs(ModelFolderPath)
                # self.LogMessage('Created directory : ' + os.path.realpath(ModelFolderPath), 'OK')
            except FileExistsError:
                # Directory already exists
                # self.LogMessage('Directory already exists : ' + os.path.realpath(ModelFolderPath), 'OK')
                pass

            # Dataset preparation
            JsonObj = json.loads(JsonData)
            dataframe = pd.DataFrame(JsonObj)
            dataframe = dataframe.set_index('Index')
            cols = ['Total Daily Lying', 'ActualLameness', 'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'ActualKetosis',
                    'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3', 'ActualMastitis']
            dataset = dataframe[cols]

            self.LogMessage('Dataset loading complete', 'OK')

            # Transform non numeric columns, into 0 and 1
            le = LabelEncoder()
            le.fit(["Healthy", "Sick"])  # Healthy = 0 , Sick = 1
            le.transform(dataset["ActualLameness"])
            dataset['ActualLameness'] = le.transform(dataset['ActualLameness']).astype(int)

            le1 = LabelEncoder()
            le1.fit(["Healthy", "Sick"])  # Healthy = 0 , Sick = 1
            le1.transform(dataset["ActualKetosis"])
            dataset['ActualKetosis'] = le1.transform(dataset['ActualKetosis']).astype(int)

            le2 = LabelEncoder()
            le2.fit(["Healthy", "Sick"])  # Healthy = 0 , Sick = 1
            le2.transform(dataset["ActualMastitis"])
            dataset['ActualMastitis'] = le2.transform(dataset['ActualMastitis']).astype(int)

            self.LogMessage('Encoding labels complete', 'OK')

            # RANDOM FOREST CLASSIFICATION SETUP
            # Defining the values: X will contains values and solutions, y will contain only solution column and i is the index column
            Lameness_X = dataset.iloc[:, 0:1].values
            Lameness_y = dataset.iloc[:, 1].values
            Lameness_i = dataset.index.values

            Ketosis_X = dataset.iloc[:, 2:5].values
            Ketosis_y = dataset.iloc[:, 5].values
            Ketosis_i = dataset.index.values

            Mastitis_X = dataset.iloc[:, 6:9].values
            Mastitis_y = dataset.iloc[:, 9].values
            Mastitis_i = dataset.index.values

            self.LogMessage('Values definition for random forest classification setup, complete', 'OK')

            # We split dataset into Training and test, and keep the index for each of them
            Lameness_X_train, Lameness_X_test, Lameness_y_train, Lameness_y_test, Lameness_i_train, Lameness_i_test = train_test_split(
              Lameness_X, Lameness_y, Lameness_i, test_size=0.20, random_state=rs)

            Ketosis_X_train, Ketosis_X_test, Ketosis_y_train, Ketosis_y_test, Ketosis_i_train, Ketosis_i_test = train_test_split(
              Ketosis_X, Ketosis_y, Ketosis_i, test_size=0.20, random_state=rs)

            Mastitis_X_train, Mastitis_X_test, Mastitis_y_train, Mastitis_y_test, Mastitis_i_train, Mastitis_i_test = train_test_split(
              Mastitis_X, Mastitis_y, Mastitis_i, test_size=0.20, random_state=rs)

            self.LogMessage('Defining training and test data complete', 'OK')

            # Model construction for random forest classification
            LamenessClassifier = RandomForestClassifier(n_estimators=100, random_state=rs)
            LamenessClassifier.fit(Lameness_X_train, Lameness_y_train)
            Lameness_y_pred = LamenessClassifier.predict(Lameness_X_test)

            KetosisClassifier = RandomForestClassifier(n_estimators=100, random_state=rs)
            KetosisClassifier.fit(Ketosis_X_train, Ketosis_y_train)
            Ketosis_y_pred = KetosisClassifier.predict(Ketosis_X_test)

            MastitisClassifier = RandomForestClassifier(n_estimators=100, random_state=rs)
            MastitisClassifier.fit(Mastitis_X_train, Mastitis_y_train)
            Mastitis_y_pred = MastitisClassifier.predict(Mastitis_X_test)

            self.LogMessage('Training and test complete', 'OK')

            # Savign Models
            joblib.dump(LamenessClassifier, ModelFolderPath + '/' + LamenessModelName + '.pkl')
            joblib.dump(KetosisClassifier, ModelFolderPath + '/' + KetosisModelName + '.pkl')
            joblib.dump(MastitisClassifier, ModelFolderPath + '/' + MastitisModelName + '.pkl')

            self.LogMessage('Models saved : ' + os.path.realpath(ModelFolderPath) + '/' + LamenessModelName + '.pkl, ' + 
                            os.path.realpath(ModelFolderPath) + '/' + KetosisModelName + '.pkl, ' + 
                            os.path.realpath(ModelFolderPath) + '/' + MastitisModelName + '.pkl', 'OK')

            # Getting Accuracy score
            LamenessAccuracy = accuracy_score(Lameness_y_test, Lameness_y_pred) * 100
            KetosisAccuracy = accuracy_score(Ketosis_y_test, Ketosis_y_pred) * 100
            MastitisAccuracy = accuracy_score(Mastitis_y_test, Mastitis_y_pred) * 100

            # Getting Precision score
            LamenessPrecision = precision_score(Lameness_y_test, Lameness_y_pred, average='macro') * 100
            KetosisPrecision = precision_score(Ketosis_y_test, Ketosis_y_pred, average='micro') * 100
            MastitisPrecision = precision_score(Mastitis_y_test, Mastitis_y_pred, average='micro') * 100

            self.LogMessage('Accuracy score values set complete', 'OK')

            # Creating a dataset with output test results
            # Setting the indexes picked for the test, we can choose any index from the three patologyes, they are all the same
            indices = Lameness_i_test
            df4 = pd.DataFrame(le.inverse_transform(Lameness_y_test))
            df4 = df4.set_index(indices)
            df4.columns = ['ActualLameness']
            df5 = pd.DataFrame(le.inverse_transform(Lameness_y_pred))
            df5 = df5.set_index(indices)
            df5.columns = ['PredictedLameness']
            df6 = pd.DataFrame(le1.inverse_transform(Ketosis_y_test))
            df6 = df6.set_index(indices)
            df6.columns = ['ActualKetosis']
            df7 = pd.DataFrame(le1.inverse_transform(Ketosis_y_pred))
            df7 = df7.set_index(indices)
            df7.columns = ['PredictedKetosis']
            df8 = pd.DataFrame(le2.inverse_transform(Mastitis_y_test))
            df8 = df8.set_index(indices)
            df8.columns = ['ActualMastitis']
            df9 = pd.DataFrame(le2.inverse_transform(Mastitis_y_pred))
            df9 = df9.set_index(indices)
            df9.columns = ['PredictedMastitis']

            cols = ['Date', 'Pedometer', 'Cow', 'MID', 'Lactations', 'Daily Production', 'Average Daily Production',
                    'Daily Fat', 'Daily Proteins', 'Daily Fat/Proteins', 'Conduttivity 1', 'Conduttivity 2', 'Conduttivity 3',
                   'Activity 1', 'Activity 2', 'Activity 3', 'Total Daily Lying']

            df10 = dataframe[cols].loc[indices].join([df4, df5, df6, df7, df8, df9])
            df10 = df10
            df10.sort_index(inplace=True)
            df10['Date'] = pd.to_datetime(df10['Date'], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')
            df10 = df10.reset_index()

            self.LogMessage('Output dataset construction complete', 'OK')

            # Metrics calculation
            Lameness_TP, Lameness_FP, Lameness_TN, Lameness_FN, Lameness_FPR, Lameness_TPR = self.measure(Lameness_y_test, Lameness_y_pred)
            Ketosis_TP, Ketosis_FP, Ketosis_TN, Ketosis_FN, Ketosis_FPR, Ketosis_TPR = self.measure(Ketosis_y_test, Ketosis_y_pred)
            Mastitis_TP, Mastitis_FP, Mastitis_TN, Mastitis_FN, Mastitis_FPR, Mastitis_TPR = self.measure(Mastitis_y_test, Mastitis_y_pred)

            Mydict = {'LAMENESS_TRUE_POSITIVE_RATE': [Lameness_TPR], 'LAMENESS_FALSE_POSITIVE_RATE': [Lameness_FPR], 'LAMENESS_PRECISION': [LamenessPrecision], 'LAMENESS_ACCURACY': [LamenessAccuracy],
                    'MASTITIS_TRUE_POSITIVE_RATE': [Mastitis_TPR], 'MASTITIS_FALSE_POSITIVE_RATE': [Mastitis_FPR], 'MASTITIS_PRECISION': [MastitisPrecision], 'MASTITIS_ACCURACY': [MastitisAccuracy],
                    'KETOSIS_TRUE_POSITIVE_RATE': [Ketosis_TPR], 'KETOSIS_FALSE_POSITIVE_RATE': [Ketosis_FPR], 'KETOSIS_PRECISION': [KetosisPrecision], 'KETOSIS_ACCURACY': [KetosisAccuracy]}

            self.LogMessage('Metrics calculation complete', 'OK')

            # !!! OUTPUT  DATASET PREDICTIONS AND DATASET METRICS
            dsPredictions = df10
            dsMetrics = pd.DataFrame(Mydict)

            # Convert dataset predictions to json using records orientation
            jsonDataset = dsPredictions.to_json(orient='records')
            jsonMetrics = dsMetrics.to_json(orient='records')
            self.LogMessage('Create JSON file from dataset test predictions','OK')  

            # Decode the json data created to insert a custom root element
            jsonDataset_decoded = json.loads(jsonDataset)
            jsonDataset_decoded = {'animalData': jsonDataset_decoded}
            jsonMetrics_decoded = json.loads(jsonMetrics)
            jsonMetrics_decoded = {'metrics': jsonMetrics_decoded}

            # Decode json that contains metrics element and update it with the prediction dataset json           
            jsonDataset_decoded.update(jsonMetrics_decoded)
            self.LogMessage('Updated JSON complete','OK')

            JsonResult = json.dumps(jsonDataset_decoded, indent=4, sort_keys=False)
            self.LogMessage('Health predictions training and test algorithm complete successfully', 'OK')
            # print(dsPredictions, dsMetrics)
            return JsonResult
        except:
            dsPredictions = None
            dsMetrics = None
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errline = str(exc_tb.tb_lineno)
            self.LogMessage("Unexpected error at line number " + errline + " : " + str(sys.exc_info()), 'ERROR')
