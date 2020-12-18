/*
 * Random Forest Module Plugin
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 17/12/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Interface that will be used on PyModuleExecutor to proxify the calls
 * to functions inside the python modules for training and prediction.
 */

package it.eng.is3lab.animal_welfare.pyplugin;

public interface RFModulePlugin {
	
	public String execRFTraining(String url,int randomState,int estimatorsNumbers);
	
	public String execRFPrediction(String url);
	
	public void initConfiguration(String confFile,String workpath);

}
