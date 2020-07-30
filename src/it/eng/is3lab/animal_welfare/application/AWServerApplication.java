/*
 * Animal Welfare Server Application
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 28/07/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Standard JAX-RS class that provide information about the deployment. 
 * This class lists all JAX-RS root resources and providers, and it is 
 * annotated with the @ApplicationPath annotation.
 */

package it.eng.is3lab.animal_welfare.application;

import java.util.HashSet;
import java.util.Set;
import javax.ws.rs.ApplicationPath;
import javax.ws.rs.core.Application;
import it.eng.is3lab.animal_welfare.service.AWServiceEndpoints;

@ApplicationPath("/")
public class AWServerApplication extends Application {
	
	private Set<Object> singletons = new HashSet<Object>();
	private Set<Class<?>> empty = new HashSet<Class<?>>();

	public AWServerApplication() {
		singletons.add(new AWServiceEndpoints());
	}
	
	@Override
	public Set<Class<?>> getClasses() {
		return empty;
	}

	@Override
	public Set<Object> getSingletons() {
		return singletons;
	}

}
