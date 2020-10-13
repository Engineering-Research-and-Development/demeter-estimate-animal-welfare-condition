/*
 * Animal Welfare Service Endpoints
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 09/10/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Implements the Animal Welfare Service interface and define the 
 * business service endpoints through the use of annotations.
 * 
 * The complete URL to call an endpoint is composed like:
 * http://SERVER_HOST/PROJECT_NAME/ENDPOINT_URL
 * 
 * The ENDPOINT_URL is composed by:
 * /Path value annotation of the class/Path value annotation of the method
 * 
 * Training complete URL example 
 * http://localhost:9080/EstimateAnimalWelfareConditionModule/v1/animalWelfareTraining
 * 
 * Training with configuration URL example 
 * http://localhost:9080/EstimateAnimalWelfareConditionModule/v1/animalWelfareTraining/randomstate/42/estimators/100
 * 
 * Prediction complete URL example 
 * http://localhost:9080/EstimateAnimalWelfareConditionModule/v1/animalWelfarePrediction
 * 
 * 
 * Method      : training
 * 
 * Endpoint    : /v1/animalWelfareTraining 
 * 
 * Type        : GET
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 *    
 * Description : Get the leatest training data
 * 
 * Request     : Json input data to be sent to random forest training module
 * 
 * Response    : Response containing json data output
 * 
 * 
 * 
 * Method      : prediction
 * 
 * Endpoint    : /v1/animalWelfarePrediction
 * 
 * Type        : GET
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 * 
 * Description : Get the leatest prediction data
 * 
 * Request     : Json input data to be sent to random forest prediction module
 * 
 * Response    : Response containing json data output
 * 
 * 
 * 
 * Method      : sendDatasetTraining
 * 
 * Endpoint    : /v1/animalWelfareTraining 
 * 
 * Type        : POST
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 *    
 * Description : Read the json content of the body inside the request, execute
 * 			     random forest training and store output data
 *               into file using readDataAndStore method.
 * 
 * Request     : Json input data to be stored for future training
 * 
 * Response    : Response containing the data stored and a message about the process
 * 
 * 
 * 
 * Method      : configAndSendDatasetTraining
 * 
 * Endpoint    : /v1/animalWelfareTraining/randomstate/{int randomstate}/estimators/{int estimators} 
 * 
 * Type        : POST
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 *    
 * Description : Read the json content of the body inside the request, 
 * 				 configure random state and estimators,
 * 				 execute random forest training and store output data and store it
 *               into file using readDataAndStore method.
 * 
 * Request     : Json input data to be stored for future training
 * 
 * Response    : Response containing the data stored and a message about the process
 * 
 * 
 * 
 * Method      : sendDatasetPrediction
 * 
 * Endpoint    : /v1/animalWelfarePrediction
 * 
 * Type        : POST
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 * 
 * Description : Read the json content of the body inside the request, execute
 * 			     random forest prediction and store output data into file 
 * 				 using readDataAndStore method.
 * 
 * Request     : Json input data to be stored for future training
 * 
 * Response    : Response containing the data stored and a message about the process
 * 
 * 
 * 
 * Method      : initDataAndSend 
 *    
 * Description : Retrieve the data from json file and send it as Response.
 * 				 The operation string is used to choose which data to get:
 *               	- "Training"   - Init training data and send it to training method
 *               	- "Prediction" - Init prediction data and send it to prediction method
 * 
 * Parameters  : String operation
 * 
 * Return 	   : String jsonDataOutput
 * 
 * 
 * 
 * Method      : readDataAndSend 
 *    
 * Description : Read the request body content and send it to the Python module executor class.
 * 				 The operation string is used to choose which task the python need to execute and
 * 				 also used by AWDataManagement class to store data into file, the file name is
 * 				 composed by a prefix that will depends on the value stored by the operation var:
 *               	- "Training"   - The method was called by a training POST service
 *               	- "Prediction" - The method was called by a prediction POST service
 * 
 * Parameters  : InputStream requestBody
 * 				 String 	 operation
 * 
 * Return 	   : String jsonDataOutput
 */

package it.eng.is3lab.animal_welfare.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jboss.resteasy.annotations.providers.jaxb.Formatted;

import it.eng.is3lab.animal_welfare.pyplugin.PyModuleExecutor;
import it.eng.is3lab.animal_welfare.pyplugin.RFConfigurator;

@Path("/v1")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class AWServiceEndpoints implements AWService {
	private static final Logger log = LogManager.getLogger(AWServiceEndpoints.class);

    @GET
    @Path("/animalWelfareTraining")
    @Formatted
	public Response training() {
    	Result result = new Result();
    	try {
    		log.debug("Training endpoint reached!");   		
    		String jsonDataOutput = this.initDataAndSend("Training");
    		log.debug("Training dataset successfully retrieved!");
    		log.debug("==========================================================");
    		return Response.status(200).entity(jsonDataOutput).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			result.setErrorCode("1");
			result.setErrorDesc(e.toString());
			result.setResult(false);
			return Response.status(500).entity(result).build();
		}
	}

    @GET
    @Path("/animalWelfarePrediction")
    @Formatted
	public Response prediction() {
    	Result result = new Result();
    	try {
    		log.debug("Prediction endpoint reached!");
    		String jsonDataOutput = this.initDataAndSend("Prediction");
    		log.debug("Prediction dataset successfully retrieved!");
    		log.debug("==========================================================");
    		return Response.status(200).entity(jsonDataOutput).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			result.setErrorCode("1");
			result.setErrorDesc(e.toString());
			result.setResult(false);
			return Response.status(500).entity(result).build();
		}
	}
    
    @POST
    @Path("/animalWelfareTraining")
    @Formatted
	public Response sendDatasetTraining(@Context HttpServletRequest request, InputStream requestBody) {
    	Result result = new Result();
    	String outputData = "";
    	try {
    		log.debug("Send training dataset endpoint reached!");
    		outputData = this.readDataAndSend(requestBody, "Training");
    		log.debug("Send training dataset complete!");
    		log.debug("==========================================================");
    		return Response.status(200).entity("RESULT "+outputData).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			result.setErrorCode("1");
			result.setErrorDesc(e.toString());
			result.setResult(false);
			return Response.status(500).entity(result).build();
		}
	}
    
    @POST
    @Path("/animalWelfareTraining/randomstate/{randomstate}/estimators/{estimators}")
    @Formatted
	public Response configAndSendDatasetTraining(@Context HttpServletRequest request, 
			@PathParam("randomstate") int randomstate,
			@PathParam("estimators") int estimators,
			InputStream requestBody) {
    	Result result = new Result();
    	String outputData = "";
    	try {
    		log.debug("Config Send training dataset endpoint reached!");
    		RFConfigurator rfConf = new RFConfigurator();
    		rfConf.setConfiguration(randomstate,estimators);
    		outputData = this.readDataAndSend(requestBody, "Training");
    		log.debug("Send training dataset complete!");
    		log.debug("==========================================================");
    		return Response.status(200).entity("RESULT "+outputData).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			result.setErrorCode("1");
			result.setErrorDesc(e.toString());
			result.setResult(false);
			return Response.status(500).entity(result).build();
		}
	}
    
    @POST
    @Path("/animalWelfarePrediction")
    @Formatted
	public Response sendDatasetPrediction(@Context HttpServletRequest request, InputStream requestBody) {
    	Result result = new Result();
    	String outputData = "";
    	try {
    		log.debug("Send prediction dataset endpoint reached!");
    		outputData = this.readDataAndSend(requestBody, "Prediction");
    		log.debug("Send prediction dataset complete!");
    		log.debug("==========================================================");
    		return Response.status(200).entity("RESULT "+outputData).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			result.setErrorCode("1");
			result.setErrorDesc(e.toString());
			result.setResult(false);
			return Response.status(500).entity(result).build();
		}
	}
    
    private String initDataAndSend(String operation) {
    	log.debug("Initializing input data.");
    	String jsonDataOutput = "";
        log.debug("Initialization completed!");
    	try {
    		log.debug("Reading data...");
    		jsonDataOutput = AWDataManagement.readFromFile(operation);
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
		} 
		return jsonDataOutput;
    }

    private String readDataAndSend(InputStream requestBody,String operation) {
    	log.debug("Init reading data and store method...");
    	String jsonDataOutput = "";
    	String line;
    	PyModuleExecutor pyExe = new PyModuleExecutor();
    	InputStreamReader inputStream = new InputStreamReader(requestBody);
		BufferedReader reader = new BufferedReader(inputStream);
        StringBuilder jsonDataInput = new StringBuilder();
        log.debug("Initialization completed!");
    	try {
    		log.debug("Reading request body.");
	        while ((line = reader.readLine()) != null) {
	        	jsonDataInput.append(line);
	        }
	        log.debug("Sending data to python executor class.");
        	jsonDataOutput = pyExe.executeFunction(jsonDataInput.toString(),operation);
        	log.debug("Store dataset to file.");
	        AWDataManagement.storeToFile(jsonDataOutput,operation);
		} catch (IOException e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
		} finally {
    		if (reader != null) {
    			try {
    				log.debug("Closing the reader.");
    				reader.close();
    			}
    			catch (IOException e) {
    				log.error("An exception occured!",e);
    				e.printStackTrace();
    			}
    		}
    	}
		return jsonDataOutput;
    }

}
