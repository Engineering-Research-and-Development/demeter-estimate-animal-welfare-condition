/*
 * Animal Welfare Service Interface
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 09/10/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 */

package it.eng.is3lab.animal_welfare.service;

import java.io.IOException;
import java.io.InputStream;

import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.Response;

public interface AWService {
	
	public Response training();
	
	public Response prediction();
	
	public Response sendDatasetTraining(@Context HttpServletRequest request, InputStream requestBody) throws IOException;
	
	public Response sendDatasetPrediction(@Context HttpServletRequest request, InputStream requestBody) throws IOException;
	
	public Response configAndSendDatasetTraining(@Context HttpServletRequest request, int randomstate, int estimators, InputStream requestBody) throws IOException;

}
