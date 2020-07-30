/*
 * Python Module Executor
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 28/07/2020
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
import org.jpy.PyLib;
import org.jpy.PyModule;
import org.jpy.PyObject;
import org.springframework.util.FileSystemUtils;
import org.springframework.util.ResourceUtils;

public class PyModuleExecutor {
	
	private static void initInterpreter() throws Exception {
        Properties properties = new Properties();
        properties.load(new FileInputStream(ResourceUtils.getFile("classpath:jpyconfig.properties")));
        properties.forEach((k, v) -> {
        	System.setProperty((String) k, (String) v);
        });
        if (!PyLib.isPythonRunning()) {
            List<String> extraPaths = Arrays.asList(
                    "classpath:RandomForestTrainingModule.py",
                    "classpath:RandomForestPredictionModule.py"
            );
            List<String> cleanedExtraPaths = new ArrayList<>(extraPaths.size());

            Path tempDirectory = Files.createTempDirectory("lib-");
            Runtime.getRuntime().addShutdownHook(new Thread(() -> FileSystemUtils.deleteRecursively(((java.nio.file.Path) tempDirectory).toFile())));
            cleanedExtraPaths.add(tempDirectory.toString());

            extraPaths.forEach(lib -> {
                if (lib.startsWith("classpath:")) {
                    try {
                        String finalLib = lib.replace("classpath:", "");
                        java.nio.file.Path target = Paths.get(tempDirectory.toString(), finalLib);
                        try (InputStream stream = PyModuleExecutor.class.getClassLoader().getResourceAsStream(finalLib)) {
                            Files.copy(stream, target, StandardCopyOption.REPLACE_EXISTING);
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                } else {
                    cleanedExtraPaths.add(lib);
                }
            });

            PyLib.startPython(cleanedExtraPaths.toArray(new String[]{}));
        }
	}
	
	public String doTraining(String jsonData) {
		String jsonDataResult = "";
		try {
			initInterpreter();
			// Proxify the call to a python class.
	        PyModule rfModule = PyModule.importModule("RandomForestTrainingModule");
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
	        PyModule rfModule = PyModule.importModule("RandomForestPredictionModule");
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
