/*
 * Random Forest Module Plugin
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 09/10/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Interface that will be used on PyModuleExecutor to proxify the calls
 * to functions inside the python modules for training and prediction.
 */

package it.eng.is3lab.animal_welfare.pyplugin;

public interface RFModulePlugin {
	
	public String execRFTraining(String jsonData,int randomState,int estimatorsNumbers);
	
	public String execRFPrediction(String jsonData);
	
	public void initConfiguration(String confFile,String workpath);

}
