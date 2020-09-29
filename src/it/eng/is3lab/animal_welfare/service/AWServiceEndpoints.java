/*
 * Animal Welfare Service Endpoints
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 28/09/2020
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
 * Prediction complete URL example 
 * http://localhost:9080/EstimateAnimalWelfareConditionModule/v1/animalWelfarePrediction
 * 
 * 
 * Method      : training
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
 * Description : Read the json content of the body inside the request and send it
 * 				 as input to the Python module executor.
 * 				 After processing the data within random forest training module, 
 * 				 the response will send a json string as output with the processed data.
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
 * Type        : POST
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 * 
 * Description : Read the json string content of the body inside the request and send it
 * 				 as input to the Python module executor.
 * 				 After processing the data within random forest prediction module, 
 * 				 the response will send a json string as output with the processed data.
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
 * Description : Read the json content of the body inside the request and store it
 *               into file using readDataAndStore method.
 * 
 * Request     : Json input data to be stored for future training
 * 
 * Response    : Response containing a message about the process
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
 * Description : Read the json content of the body inside the request and store it
 *               into file using readDataAndStore method.
 * 
 * Request     : Json input data to be stored for future training
 * 
 * Response    : Response containing a message about the process
 * 
 * 
 * 
 * Method      : initDataAndSend 
 *    
 * Description : Initialize the data and send it to the Python module executor class.
 * 				 The operation string is used to choose the file that contains the data.
 * 				 The class AWDataManagement is used to read that file and init the string that will
 * 				 be sent to the python module executor to select the task to perform:
 *               	- "Training"   - Init training data and send it to training method
 *               	- "Prediction" - Init prediction data and send it to prediction method
 * 
 * Parameters  : String operation
 * 
 * Return 	   : String jsonDataOutput
 * 
 * 
 * 
 * Method      : readDataAndStore 
 *    
 * Description : Read the request body content and store the data into file system.
 * 				 The class AWDataManagement is used to store data into file, the file name is
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
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import org.jboss.resteasy.annotations.providers.jaxb.Formatted;

import it.eng.is3lab.animal_welfare.pyplugin.PyModuleExecutor;

@Path("/v1")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class AWServiceEndpoints implements AWService {
	private static final Logger log = LogManager.getLogger(AWServiceEndpoints.class);

    @GET
    @Path("/animalWelfareTraining")
    @Formatted
	public Response training() {
    	try {
    		log.debug("Training endpoint reached!");
    		String jsonDataOutput = this.initDataAndSend("Training");
    		return Response.ok(jsonDataOutput).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			return Response.ok(e).build();
		}
	}

    @GET
    @Path("/animalWelfarePrediction")
    @Formatted
	public Response prediction() {
    	try {
    		log.debug("Prediction endpoint reached!");
    		String jsonDataOutput = this.initDataAndSend("Prediction");
    		return Response.ok(jsonDataOutput).build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			return Response.ok(e).build();
		}
	}
    
    @POST
    @Path("/animalWelfareTraining")
    @Formatted
	public Response sendDatasetTraining(@Context HttpServletRequest request, InputStream requestBody) {
    	try {
    		log.debug("Send dataset training endpoint reached!");
    		this.readDataAndStore(requestBody,"Training");
    		return Response.ok("Data received successfully!").build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			return Response.ok(e).build();
		}
	}
    
    @POST
    @Path("/animalWelfarePrediction")
    @Formatted
	public Response sendDatasetPrediction(@Context HttpServletRequest request, InputStream requestBody) {
    	try {
    		log.debug("Send dataset prediction endpoint reached!");
    		this.readDataAndStore(requestBody,"Prediction");
    		return Response.ok("Data received successfully!").build();
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
			return Response.ok(e).build();
		}
	}
    
    private String initDataAndSend(String operation) {
    	log.debug("Initializing input data.");
    	String jsonDataOutput = "";
    	String jsonDataInput = "";
    	PyModuleExecutor pyExe = new PyModuleExecutor();
        log.debug("Initialization completed!");
    	try {
    		log.debug("Reading data...");
    		jsonDataInput = AWDataManagement.readFromFile(operation);
	        log.debug("Sending data to python executor class.");
        	jsonDataOutput = pyExe.executeFunction(jsonDataInput,operation);
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
		} 
		return jsonDataOutput;
    }
    
    private void readDataAndStore(InputStream requestBody,String operation) {
    	log.debug("Init reading data and store method...");
    	String line;
    	InputStreamReader inputStream = new InputStreamReader(requestBody);
		BufferedReader reader = new BufferedReader(inputStream);
        StringBuilder jsonDataInput = new StringBuilder();
        log.debug("Initialization completed!");
    	try {
    		log.debug("Reading request body.");
	        while ((line = reader.readLine()) != null) {
	        	jsonDataInput.append(line);
	        }
	        log.debug("Store dataset to file.");
	        AWDataManagement.storeToFile(jsonDataInput.toString(),operation);	        
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
    }

}
