/*
 * Animal Welfare Service Endpoints
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 31/07/2020
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
 * http://localhost:8080/EstimateAnimalWelfareConditionModule/animalWelfare/Training
 * 
 * Prediction complete URL example 
 * http://localhost:8080/EstimateAnimalWelfareConditionModule/animalWelfare/Predictions
 * 
 * 
 * Method      : training
 * 
 * Endpoint    : /animalWelfare/Training 
 * 
 * Type        : POST
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 				 Accept       | application/json
 *    
 * Description : Read the json string content of the body inside the request and send it
 * 				 as input to the Python module executor.
 * 				 After processing the data within random forest training module, 
 * 				 the response will send a json string as output with the processed data.
 * 
 * Request     : Json with input data to be sent to random forest training module
 * 
 * Response    : Json with output data
 * 
 * 
 * 
 * Method      : prediction
 * 
 * Endpoint    : /animalWelfare/Predictions
 * 
 * Type        : POST
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 				 Accept       | application/json
 * 
 * Description : Read the json string content of the body inside the request and send it
 * 				 as input to the Python module executor.
 * 				 After processing the data within random forest prediction module, 
 * 				 the response will send a json string as output with the processed data.
 * 
 * Request     : String Json input data to be sent to random forest prediction module
 * 
 * Response    : String with json data output
 */

package it.eng.is3lab.animal_welfare.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.Consumes;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;

import org.jboss.resteasy.annotations.providers.jaxb.Formatted;

import it.eng.is3lab.animal_welfare.pyplugin.PyModuleExecutor;

@Path("/animalWelfare")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class AWServiceEndpoints implements AWService {

    @POST
    @Path("/Training")
    @Formatted
	public String training(@Context HttpServletRequest request, InputStream requestBody) throws IOException {
		PyModuleExecutor pyExe = new PyModuleExecutor();
		String jsonDataOutput = "";
		BufferedReader reader = new BufferedReader(new InputStreamReader(requestBody));
        StringBuilder jsonDataInput = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
        	jsonDataInput.append(line);
        }
        System.out.println(jsonDataInput.toString());
        reader.close();   
        try {			
        	jsonDataOutput = pyExe.doTraining(jsonDataInput.toString()); 
		} catch (Exception e) {
			e.printStackTrace();
		}
        // TO-DO: GESTIONE ERRORI LOG. Inviare un messaggio di errore in caso di stringa nulla
		return jsonDataOutput;
	}

    @POST
    @Path("/Predictions")
    @Formatted
	public String prediction(@Context HttpServletRequest request, InputStream requestBody) throws IOException {
		PyModuleExecutor pyExe = new PyModuleExecutor();
		String jsonDataOutput = "";
		BufferedReader reader = new BufferedReader(new InputStreamReader(requestBody));
        StringBuilder jsonDataInput = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
        	jsonDataInput.append(line);
        }
        System.out.println(jsonDataInput.toString());
        reader.close();   
        try {			
        	jsonDataOutput = pyExe.doPrediction(jsonDataInput.toString()); 
		} catch (Exception e) {
			e.printStackTrace();
		}
        // TO-DO: GESTIONE ERRORI LOG. Inviare un messaggio di errore in caso di stringa nulla
		return jsonDataOutput;
	}

}
