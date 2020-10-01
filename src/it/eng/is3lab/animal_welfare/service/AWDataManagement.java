package it.eng.is3lab.animal_welfare.service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class AWDataManagement {
	private static final Logger log = LogManager.getLogger(AWDataManagement.class);
	
	public static void storeToFile(String dataToStore, String operation) {
		log.debug("Storing data into file.");
		String fileName = operation+"_AnimalWelfare.json";
		String filePath = System.getenv("JSON_FILE_PATH");
		log.debug("Data file directory: "+filePath+fileName);
		BufferedWriter writer = null;
	    try {
	    	log.debug("Writing data...");
	    	writer = new BufferedWriter(new FileWriter(filePath+fileName));
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
		String fileName = operation+"_AnimalWelfare.json";
		String filePath = System.getenv("JSON_FILE_PATH");
		String line;
		String outData = "";
		log.debug("Data file directory: "+filePath+fileName);
		BufferedReader reader = null;
		StringBuilder sb = new StringBuilder();
	    try {
	    	log.debug("Reading data...");
	    	reader = new BufferedReader(new FileReader(filePath+fileName));
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
