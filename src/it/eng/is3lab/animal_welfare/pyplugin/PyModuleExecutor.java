/*
 * Python Module Executor
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 09/10/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Define all the process to configure and use the python interpreter
 * within the JPY library.
 * All the resources paths are get from the serviceConf.properties file.
 * 
 * 
 * 
 * Method      : initInterpreter 
 *    
 * Description : Initialize all the required system properties like 'jpy.jpyLib' and others
 * 				 that are defined in jpyconfig.properties resource.
 * 				 Before running the python interpreter, process the python modules 
 * 				 defined inside the extraPaths list, clean their path and copy them 
 * 				 into Temp default directory inside a temporary folder that will be deleted
 * 				 on server shutdown.
 * 				 Then start Python with cleaned extraPaths that reference the modules
 * 				 inside the Temp/AnimalWelfare-PyMod-XXXXX folder.
 * 
 * Parameters  : 
 * 
 * Return 	   : void   
 * 
 * 
 * 
 * Method      : executeFunction
 * 
 * Description : Sends the jsonData string to the training or prediction function 
 * 				 of the RandomForest class defined inside the RandomForestModule.
 * 				 The value of "operation" var is used to choose which function execute:
 * 					- "Training" - Execute training function
 *               	- "Prediction" - Execute prediction function
 * 				 If the output data received from python is not empty, 
 *               then return the output data, else build a JsonObject containing an error.
 * 
 * Parameters  : String jsonData    - Contains the json string with input data
 * 				 String operation   - Used to choose which function execute
 * 
 * Return      : String jsonDataResult
 */

package it.eng.is3lab.animal_welfare.pyplugin;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.ResourceBundle;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import org.jpy.PyLib;
import org.jpy.PyModule;
import org.jpy.PyObject;
import org.json.JSONObject;
import org.springframework.util.FileSystemUtils;

public class PyModuleExecutor {
	private static final Logger log = LogManager.getLogger(PyModuleExecutor.class);
	private static ResourceBundle configuration = ResourceBundle.getBundle("resources/serviceConf");
	private static String pyModulesRoot = configuration.getString("animalwelfare.pyModuleExecutor.pyModulesRoot");
	private static String pyModulesUtilities = configuration.getString("animalwelfare.pyModuleExecutor.pyModulesUtilities");
	private static String jpyConfigPath = configuration.getString("animalwelfare.pyModuleExecutor.jpyConfigPath");
	// Load Python Modules Paths
	private static String AWRandomForestModule = configuration.getString("animalwelfare.pyModuleExecutor.AWRandomForestModule");
	private static String AWLogger = configuration.getString("animalwelfare.pyModuleExecutor.AWLogger");

	private static void initInterpreter() throws Exception {
		log.debug("Initialize Python Interpreter");
		log.debug("Loading jpy configuration");
        Properties properties = new Properties();
        InputStream jpyconfig = PyModuleExecutor.class.getClassLoader().getResourceAsStream(jpyConfigPath);
        properties.load(jpyconfig);
        properties.forEach((k, v) -> {
        	log.debug("Setting: "+(String) k+" Value: "+(String) v);
        	System.setProperty((String) k, (String) v);
        });
        log.debug("Jpy Configuration completed!");
        if (!PyLib.isPythonRunning()) {
        	log.debug("Preparing to configure Python modules path");
            List<String> extraPaths = Arrays.asList(
                    AWRandomForestModule,
                    AWLogger
            );
            List<String> cleanedExtraPaths = new ArrayList<>(extraPaths.size());

            Path tempDirectory = Files.createTempDirectory("AnimalWelfare-PyMod-");
            Runtime.getRuntime().addShutdownHook(new Thread(() -> FileSystemUtils.deleteRecursively(((java.nio.file.Path) tempDirectory).toFile())));
            cleanedExtraPaths.add(tempDirectory.toString());
            log.debug("Created temporary directory: "+tempDirectory.toString());

            extraPaths.forEach(lib -> {
                try {
                	String finalLib = "";
                	InputStream stream = PyModuleExecutor.class.getClassLoader().getResourceAsStream(lib);
                	if (lib.startsWith(pyModulesUtilities)) {
                		finalLib = lib.replace(pyModulesUtilities, "");
                	}
                	else {
                		finalLib = lib.replace(pyModulesRoot, "");
                	}
                    log.debug("Copying python module: "+finalLib);
                    java.nio.file.Path target = Paths.get(tempDirectory.toString(), finalLib);
                    
                    Files.copy(stream, target, StandardCopyOption.REPLACE_EXISTING);
                    
                } catch (Exception e) {
                	log.error("An exception occured!",e);
                    e.printStackTrace();
                }
            });
            log.debug("Python interpreter configured!");
            PyLib.startPython(cleanedExtraPaths.toArray(new String[]{}));
        }
	}
	
	public String executeFunction(String jsonData, String operation) {
		String jsonDataResult = "";
		try {
			initInterpreter();
			RFConfigurator rfConf = new RFConfigurator();
        	rfConf.loadConfiguration();
        	String configFilePath = rfConf.getConfigFilePath();
        	String workDir = rfConf.getWorkDir();
			log.debug("Importing random forest module into interpreter.");
			// Proxify the call to a python class.
	        PyModule rfModule = PyModule.importModule("AWRandomForestModule");
	        log.debug("Calling the random forest module class.");
	        PyObject rfObject = rfModule.call("AnimalWelfareRandomForest");
	        RFModulePlugin rfPlugIn = rfObject.createProxy(RFModulePlugin.class);
	        log.debug("Initialize random forest module configuration");
	        log.debug("Random Forest configuration file path: "+configFilePath);
	        log.debug("Working directory: "+workDir);
	        rfPlugIn.initConfiguration(configFilePath, workDir);
	        // Execute the python function.
	        switch(operation) 
	        { 
	            case "Training": 
	            	log.debug("TRAINING: Executing training function.");
	            	int rs = rfConf.getRandomState();
	            	int est = rfConf.getEstimators();
	            	jsonDataResult = rfPlugIn.execRFTraining(jsonData,rs,est);
	                break; 
	            case "Prediction": 
	            	log.debug("PREDICTION: Executing prediction function.");
	            	jsonDataResult = rfPlugIn.execRFPrediction(jsonData);
	            	break;
	        }
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
		} finally {
			//log.debug("Stopping python interpreter.");
	        //PyLib.stopPython(); Bugged

			if (jsonDataResult == "") {
        		log.error("Output data is empty! An error occured while executing python module."
        				+ "Check the Random forest log for more info.");
        		JSONObject err = new JSONObject();
        		err.put("Code", "2");
        		err.put("Type", "Random forest module error");
        		err.put("Description", "An error occured while processing the data for "+operation+" task!");
        		jsonDataResult = err.toString();
        		return jsonDataResult;
        	}
		}
		log.debug("Sending output data.");
		return jsonDataResult;
	}

}
