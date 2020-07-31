![](https://portal.ogc.org/files/?artifact_id=92076)
# Estimate animal welfare condition module

Machine learning module for animal welfare estimation using _**Random Forest**_ algorithm.
The values to predict are a discrete class label such as _**Healthy**_ or _**Sick**_.
During training, it is necessary to provide to the model any historical data that is relevant 
to the problem domain and the true value we want the model learns to predict. 
The model learns any relationships between the data and the values we want to predict. 
The decision tree forms a structure, calculating the best questions to ask to make the most accurate estimates possible.

## Table of contents
* [**Technologies**](#technologies)
* [**Requirements**](#requirements)
* [**Setup**](#setup)
* [**Features**](#features)
* [**Endpoints**](#endpoints)
* [**How to use**](#how-to-use)
* [**Troubleshoot**](#troubleshoot)
* [**Developers**](#developers)
* [**Status**](#status)
* [**License**](#license)

## Technologies

| Description                                      | Language | Version          |
| :----------------------------------------------  | :------: | :--------------: |
| [Java SE Development Kit 8][1]                   | Java     | 1.8.0_251        |
| [Python 3][2]                                    | Python   | 3.8.3            |
| [Apache Maven 3][3]                              |          | 3.6.3            |
| [Apache Tomcat 7][4]                             |          | 7.0.104          |
| [Scikit-learn API][5]                            | Python   | 0.23.1           |
| [JPY API][6]                                     | Java     | 0.10.SNAPSHOT    |
| [RESTEasy API][7]                                | Java     | 3.12.1.Final     |
| [Spring Framework][8]                            | Java     | 4.3.3.RELEASE    |
| [Json][9]                                        |          | 20200518         |
| [Eclipse IDE for Enterprise Java Developers][10] | Java     | 2020-06 (4.16.0) |
| [PyDev Python IDE for Eclipse][11]               | Python   | 7.6.0            |

[1]: https://www.oracle.com/it/java/technologies/javase/javase-jdk8-downloads.html
[2]: https://www.python.org/downloads/release/python-383/
[3]: http://maven.apache.org/ 
[4]: https://tomcat.apache.org/download-70.cgi#7.0.104 
[5]: https://scikit-learn.org/stable/index.html 
[6]: https://jpy.readthedocs.io/en/latest/intro.html 
[7]: https://resteasy.github.io/ 
[8]: https://spring.io/projects/spring-framework
[9]: http://www.JSON.org/
[10]: https://www.eclipse.org/downloads/ 
[11]: http://www.pydev.org/ 

## Requirements

* Java 1.8
* Python 3
* Maven
* Tomcat 7

## Setup
**TO DO**

## Features

* **Algorithm Training, Testing and Metrics calculation:** 
Receives a dataset of _training features_ as input to perfom the training, test and metrics calculations. 
Return an object with the _training result_ that will show all the test records used after the training with the predictions made by the algorithm and the metrics.

* **Predict health condition:** 
Receive a dataset of _prediction features_ as input to perform predictions and return an object with the _prediction result_. 

## Endpoints

| URL                            | Type     | Used for                                         | Input                                  | Output                                                  |
| :----------------------------- | :------: | :----------------------------------------------- | :------------------------------------- | :------------------------------------------------------ |
| **/animalWelfare/Traininig**   | **POST** | Train the algorithm and calculate the metrics    | Json data with actual health condition | Json with test predicted health condition and metrics   |
| **/animalWelfare/Predictions** | **POST** | Estimate the health condition                    | Json with data to be processed         | Json with predicted health condition                    |

## How to use
**TO DO**

## Troubleshoot
**TO DO**

## Developers

* [Luigi di Corrado](https://github.com/luidicorra) 

## Status
Project is: _in progress_

## License
<!--- If you're not sure which open license to use see https://choosealicense.com/--->
This project uses the following license: [<license_name>](<link>).
