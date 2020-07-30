/*
 * Animal Welfare Service Interface
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 30/07/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 */

package it.eng.is3lab.animal_welfare.service;

import java.io.IOException;
import java.io.InputStream;

import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.core.Context;

public interface AWService {
	
	public String training(@Context HttpServletRequest request, InputStream requestBody) throws IOException;
	public String prediction(@Context HttpServletRequest request, InputStream requestBody) throws IOException;

}
