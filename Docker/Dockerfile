FROM tomcat:7.0.104

# ARGUMENTS

ARG MODULE_NAME=EstimateAnimalWelfareConditionModule
ARG DIRECTORY_NAME=AW-WorkDir
ARG TOMCAT_DIRECTORY=/usr/local/tomcat

# DECLARING ENVIRONMENT VAR

ENV AW_WORK_DIRECTORY /usr/local/tomcat/
ENV AW_PY_RESOURCES /usr/local/tomcat/webapps/${MODULE_NAME}/WEB-INF/classes/python/resources/

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

RUN pip3 install pandas \
 && pip3 install numpy \
 && pip3 install scipy \
 && pip3 install matplotlib \
 && pip3 install scikit-learn \
 && pip3 install sklearn \
 && pip3 install requests \
 && pip3 install cherrypy \
 && pip3 install mysql-connector

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