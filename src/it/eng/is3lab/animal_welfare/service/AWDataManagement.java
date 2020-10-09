/*
 * Animal Welfare Data Management
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 09/10/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Store and Read output data from files.
 * All the file settings are loaded from serviceConf.properties file
 * 
 * 
 * 
 * Method      : storeToFile
 *    
 * Description : Save data into file, the file name prefix is defined by operation value
 * 
 * Parameters  : String    dataToStore
 * 				 String    operation
 * 
 * Return 	   : void
 * 
 * 
 * 
 * Method      : readFromFile
 *    
 * Description : Read the data from file, the operation value is used to choose which file read
 * 
 * Parameters  : String    operation
 * 
 * Return 	   : String	   outData
 */

package it.eng.is3lab.animal_welfare.service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ResourceBundle;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class AWDataManagement {
	private static final Logger log = LogManager.getLogger(AWDataManagement.class);
	private static ResourceBundle properties = ResourceBundle.getBundle("resources/serviceConf");
	private static String workDir = System.getenv(properties.getString("animalwelfare.workDirectory"));
	private static String filePath = workDir + properties.getString("serviceDataManagement.filePath");
	private static String fileNameSuffix = properties.getString("serviceDataManagement.fileNameSuffix");
	private static String fileExtension = properties.getString("serviceDataManagement.fileExtension");
	
	public static void storeToFile(String dataToStore, String operation) {
		log.debug("Storing data into file.");
		String fileNamePrefix = operation;
		String fileName = fileNamePrefix+fileNameSuffix+fileExtension;
		String fullPath = filePath+fileName;
		//String filePath = System.getenv("JSON_FILE_PATH");
		log.debug("Data file directory: "+fullPath);
		BufferedWriter writer = null;
	    try {
	    	log.debug("Writing data...");
	    	writer = new BufferedWriter(new FileWriter(fullPath));
			writer.write(dataToStore);
			log.debug("Writing data complete!");
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (writer != null) {
    			try {
    				log.debug("Closing the writer.");
    				writer.close();;
    			}
    			catch (IOException e) {
    				log.error("An exception occured!",e);
    				e.printStackTrace();
    			}
    		}
			
		}    		
	}
	
	public static String readFromFile(String operation) {
		log.debug("Reading data from file.");
		String fileNamePrefix = operation;
		String fileName = fileNamePrefix+fileNameSuffix+fileExtension;
		String fullPath = filePath+fileName;
		//String filePath = System.getenv("JSON_FILE_PATH");
		String line;
		String outData = "";
		log.debug("Data file directory: "+fullPath);
		BufferedReader reader = null;
		StringBuilder sb = new StringBuilder();
	    try {
	    	log.debug("Reading data...");
	    	reader = new BufferedReader(new FileReader(fullPath));
	    	while ((line = reader.readLine()) != null) {
	    		sb.append(line);
		    }
			log.debug("Reading data complete!");
			outData = sb.toString();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (reader != null) {
    			try {
    				log.debug("Closing the reader.");
    				reader.close();;
    			}
    			catch (IOException e) {
    				log.error("An exception occured!",e);
    				e.printStackTrace();
    			}
    		}
			
		}
		return outData;    		
	}

}
