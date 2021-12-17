FROM tomcat:7.0.104

# ARGUMENTS

ARG MODULE_NAME=EstimateAnimalWelfareConditionModule
ARG DIRECTORY_NAME=AW-WorkDir
ARG TOMCAT_DIRECTORY=/usr/local/tomcat
ARG HOST_IP=192.168.1.43
ARG TRASLATOR_SERVICE_HOST_PORT=9380

# DECLARING ENVIRONMENT VAR

ENV AW_WORK_DIRECTORY /usr/local/tomcat/
ENV AW_PY_RESOURCES /usr/local/tomcat/webapps/${MODULE_NAME}/WEB-INF/classes/python/resources/
ENV AW_AIM_TRASLATOR_TRAINING_URL http://${HOST_IP}:${TRASLATOR_SERVICE_HOST_PORT}/demeter-csvManager/rest/traslator/v1/AnimalWelfareTraining
ENV AW_AIM_TRASLATOR_PREDICTION_URL http://${HOST_IP}:${TRASLATOR_SERVICE_HOST_PORT}/demeter-csvManager/rest/traslator/v1/AnimalWelfarePrediction

# MAVEN INSTALLATION

ARG MAVEN_VERSION=3.6.3
ARG USER_HOME_DIR="/root"
ARG BASE_URL=https://apache.osuosl.org/maven/maven-3/${MAVEN_VERSION}/binaries

RUN mkdir -p /usr/share/maven /usr/share/maven/ref \
 && curl -fsSL -o /tmp/apache-maven.tar.gz ${BASE_URL}/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
 && tar -xzf /tmp/apache-maven.tar.gz -C /usr/share/maven --strip-components=1 \
 && rm -f /tmp/apache-maven.tar.gz \
 && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

ENV MAVEN_HOME /usr/share/maven
ENV MAVEN_CONFIG "$USER_HOME_DIR/.m2"

# ESTIMATE ANIMAL WELFARE MODULE SETUP

COPY ./Dependencies /usr/local/Dependencies

COPY ${MODULE_NAME}.war /tmp

RUN mkdir -p ${TOMCAT_DIRECTORY}/${DIRECTORY_NAME}/data \
 && mkdir -p ${TOMCAT_DIRECTORY}/webapps/${MODULE_NAME} \
 && unzip /tmp/${MODULE_NAME}.war -d ${TOMCAT_DIRECTORY}/webapps/${MODULE_NAME}/ \
 && rm /tmp/${MODULE_NAME}.war

# PYTHON INSTALLATION

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y python3.7 python3-pip

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade Pillow

RUN pip3 install 'pandas==1.2.1'

RUN pip3 install 'numpy==1.19.5'

RUN pip3 install 'scipy==1.6.0'

RUN pip3 install 'matplotlib==3.3.3'

RUN pip3 install 'scikit-learn==0.24.1'

RUN pip3 install 'sklearn==0.0'

RUN pip3 install 'requests==2.25.1'

RUN pip3 install 'cherrypy==18.6.0'

RUN pip3 install 'mysql-connector==2.2.9'

# JPY INSTALLATION

RUN cd /usr/local/Dependencies \
 && unzip jpy-master.zip \
 && cd jpy-master \
 && python3 setup.py --maven build \
 && mkdir -p /usr/local/jpy \
 && cp -a $(ls -d build/lib*/.) /usr/local/jpy/ \
 && cd /usr/local/jpy/ \
 && python3 jpyutil.py \
 && cp /usr/local/jpy/jpyconfig.properties ${AW_PY_RESOURCES}jpy/jpyconfig.properties \
 && rm -r /usr/local/Dependencies

# INSTALL MC

RUN apt-get install -y mc

# PORT EXPOSE

EXPOSE 8080