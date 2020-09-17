/*
 * Python Module Executor
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 30/07/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Define all the process to configure and use the python interpreter
 * within the JPY library.
 * 
 * 
 * 
 * Method      : initInterpreter 
 *    
 * Description : Initialize all the required system properties like 'jpy.jpyLib' and others
 * 				 that are defined in jpyconfig.properties resource.
 * 				 Before running the python interpreter, process the python modules 
 * 				 defined inside the extraPaths list, clean their path and copy them 
 * 				 into Temp default directory inside a "lib-" folder.
 * 				 Then start Python with cleaned extraPaths that reference the modules
 * 				 inside the Temp/lib-XXXXX folder.
 * 
 * Parameters  : 
 * 
 * Return 	   : void   
 * 
 * 
 * 
 * Method      : doTraining
 * 
 * Description : Sends the data inside the jsonData string to the training function 
 * 				 of the RandomForest class defined inside the RandomForestTrainingModule
 * 
 * Parameters  : String with json data input
 * 
 * Return      : String with json data output
 * 
 * 
 * 
 * Method      : doPrediction
 * 
 * Description : Sends the data inside the jsonData string to the prediction function 
 * 				 of the RandomForest class defined inside the RandomForestPredictionModule
 * 
 * Parameters  : String with json data input
 * 
 * Return      : String with json data result
 */

package it.eng.is3lab.animal_welfare.pyplugin;

import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import org.jpy.PyLib;
import org.jpy.PyModule;
import org.jpy.PyObject;
import org.springframework.util.FileSystemUtils;
import org.springframework.util.ResourceUtils;

//import it.eng.is3lab.animal_welfare.service.AWServiceEndpoints;

public class PyModuleExecutor {
	private static final Logger log = LogManager.getLogger(PyModuleExecutor.class);

	private static void initInterpreter() throws Exception {
		log.debug("Initialize Python Interpreter");
		log.debug("Loading jpy configuration");
        Properties properties = new Properties();
        properties.load(new FileInputStream(ResourceUtils.getFile("classpath:jpyconfig.properties")));
        properties.forEach((k, v) -> {
        	log.debug("Setting: "+(String) k+" Value: "+(String) v);
        	System.setProperty((String) k, (String) v);
        });
        log.debug("Jpy Configuration completed!");
        if (!PyLib.isPythonRunning()) {
        	log.debug("Preparing to configure Python modules path");
            List<String> extraPaths = Arrays.asList(
                    "classpath:RandomForestModule.py",
                    "classpath:Logger.py"
            );
            List<String> cleanedExtraPaths = new ArrayList<>(extraPaths.size());

            Path tempDirectory = Files.createTempDirectory("lib-");
            // This Hook is not working. Need another solution
            Runtime.getRuntime().addShutdownHook(new Thread(() -> FileSystemUtils.deleteRecursively(((java.nio.file.Path) tempDirectory).toFile())));
            cleanedExtraPaths.add(tempDirectory.toString());
            log.debug("Created temporary directory: "+tempDirectory.toString());

            extraPaths.forEach(lib -> {
                if (lib.startsWith("classpath:")) {
                    try {
                        String finalLib = lib.replace("classpath:", "");
                        log.debug("Copying python module: "+finalLib);
                        java.nio.file.Path target = Paths.get(tempDirectory.toString(), finalLib);
                        try (InputStream stream = PyModuleExecutor.class.getClassLoader().getResourceAsStream(finalLib)) {
                            Files.copy(stream, target, StandardCopyOption.REPLACE_EXISTING);
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                } else {
                	log.debug("Loading python module: "+lib);
                    cleanedExtraPaths.add(lib);
                }
            });
            log.debug("Initialization completed!");

            PyLib.startPython(cleanedExtraPaths.toArray(new String[]{}));
        }
	}
	
	public String doTraining(String jsonData) {
		String jsonDataResult = "";
		try {
			initInterpreter();
			// Proxify the call to a python class.
	        PyModule rfModule = PyModule.importModule("RandomForestModule");
	        PyObject rfObject = rfModule.call("RandomForest");
	        RFModulePlugin rfPlugIn = rfObject.createProxy(RFModulePlugin.class);
	        // Execute the python function.
	        jsonDataResult = rfPlugIn.execRFTraining(jsonData);
	        PyLib.stopPython(); 
		} catch (Exception e) {
			e.printStackTrace();
		}
		return jsonDataResult;
	}
	
	public String doPrediction(String jsonData) {
		String jsonDataResult = "";
		try {
			initInterpreter();
			// Proxify the call to a python class.
	        PyModule rfModule = PyModule.importModule("RandomForestModule");
	        PyObject rfObject = rfModule.call("RandomForest");
	        RFModulePlugin rfPlugIn = rfObject.createProxy(RFModulePlugin.class);
	        // Execute the python function.
	        jsonDataResult = rfPlugIn.execRFPrediction(jsonData);
	        PyLib.stopPython(); 
		} catch (Exception e) {
			e.printStackTrace();
		}
		return jsonDataResult;
	}

}
