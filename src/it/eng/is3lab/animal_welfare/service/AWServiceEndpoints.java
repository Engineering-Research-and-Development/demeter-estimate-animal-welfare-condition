/*
 * Animal Welfare Service Endpoints
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 17/12/2020
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
 * Description : Trigger Python random forest module to execute the training
 * 
 * Request     : 
 * 
 * Response    : AIM containing training results
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
 * Description : Trigger Python random forest module to execute the prediction
 * 
 * Request     : 
 * 
 * Response    : AIM containing prediction results
 * 
 * 
 * 
 * Method      : configAndSendDatasetTraining
 * 
 * Endpoint    : /v1/animalWelfareTraining/randomstate/{int randomstate}/estimators/{int estimators} 
 * 
 * Type        : GET
 * 
 *               KEY          | VALUE
 *               -------------|-----------------
 * Headers     : Content-Type | application/json
 * 		         Accept       | application/json
 *    
 * Description : Configure random state and estimators,
 * 				 execute random forest training and send the output as response.
 * 
 * Request     : 
 * 
 * Response    : AIM containing training results
 */

package it.eng.is3lab.animal_welfare.service;

import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jboss.resteasy.annotations.providers.jaxb.Formatted;
//import it.eng.is3lab.animal_welfare.pyplugin.RFConfigurator;

@Path("/v1")
@Consumes(MediaType.APPLICATION_JSON+";charset=UTF-8")
@Produces(MediaType.APPLICATION_JSON+";charset=UTF-8")
public class AWServiceEndpoints implements AWService {
	private static final Logger log = LogManager.getLogger(AWServiceEndpoints.class);

    @GET
    @Path("/animalWelfareTraining")
    @Formatted
	public synchronized Response training() {
    	AWResult result = new AWResult();
    	try {
    		log.debug("Training endpoint reached!");   		
    		//String jsonDataOutput = AWDataManagement.sendToPythonAndGetResult("Training");
    		String jsonDataOutput = AWDataManagement.manageDataToStoreTemporary("Training");
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
	public synchronized Response prediction() {
    	AWResult result = new AWResult();
    	try {
    		log.debug("Prediction endpoint reached!");
    		//String jsonDataOutput = AWDataManagement.sendToPythonAndGetResult("Prediction");
    		String jsonDataOutput = AWDataManagement.manageDataToStoreTemporary("Prediction");
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
    
    /* TEMPORARY OFFLINE...
    @GET
    @Path("/animalWelfareTraining/randomstate/{randomstate}/estimators/{estimators}")
    @Formatted
	public Response configAndSendDatasetTraining(@PathParam("randomstate") int randomstate,	@PathParam("estimators") int estimators) {
    	AWResult result = new AWResult();
    	try {
    		log.debug("Config Send training dataset endpoint reached!");
    		RFConfigurator rfConf = new RFConfigurator();
    		rfConf.setConfiguration(randomstate,estimators);
    		String jsonDataOutput = AWDataManagement.sendToPythonAndGetResult("Training");
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
	}*/
}
