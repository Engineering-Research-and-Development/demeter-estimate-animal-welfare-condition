/*
 * Random Forest Module Plugin
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 30/07/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Interface that will be used on PyModuleExecutor like a sort of proxy to call
 * functions inside the python modules for training and prediction.
 */

package it.eng.is3lab.animal_welfare.pyplugin;

public interface RFModulePlugin {
	
	public String execRFTraining(String jsonData);
	public String execRFPrediction(String jsonData);

}
