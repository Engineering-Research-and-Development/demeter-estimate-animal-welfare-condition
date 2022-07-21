/*
 * Animal Welfare Data Management
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 19/07/2022
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Store and Read output data from files.
 * All the file settings are loaded from serviceConf.properties file
 * 
 * 
 * 
 * Method      : storeToFile (CURRENTLY NOT USED)
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
 * Method      : readFromFile (CURRENTLY NOT USED)
 *    
 * Description : Read the data from file, the operation value is used to choose which file read
 * 
 * Parameters  : String    operation
 * 
 * Return 	   : String	   outData
 * 
 * 
 * 
 * Method      : readDataAndSend (CURRENTLY NOT USED)
 *    
 * Description : Read the request body content and send it to the Python module executor class.
 * 				 The operation string is used to choose which task the python need to execute and
 * 				 also used by AWDataManagement class to store data into file, the file name is
 * 				 composed by a prefix that will depends on the value stored by the operation var:
 *               	- "Training"   - The method was called by a training POST service
 *               	- "Prediction" - The method was called by a prediction POST service
 * 
 * Parameters  : InputStream requestBody
 * 				 String 	 operation
 * 
 * Return 	   : String jsonDataOutput
 * 
 * 
 * 
 * Method      : sendToPythonAndGetResult 
 *    
 * Description : Read the correct AIM URL based on operation and send it to the Python module executor class.
 * 				 The operation string is used to choose which task the python need to execute:
 *               	- "Training"   - The method was called by a training GET service
 *               	- "Prediction" - The method was called by a prediction GET service
 * 
 * Parameters  : String operation
 * 
 * Return 	   : String jsonDataOutput
 */

package it.eng.is3lab.animal_welfare.service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Date;
//import java.io.InputStream;
//import java.io.InputStreamReader;
import java.util.ResourceBundle;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;

import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.attribute.FileTime;
import java.time.Duration;

import it.eng.is3lab.animal_welfare.pyplugin.PyModuleExecutor;

public class AWDataManagement {
	private static final Logger log = LogManager.getLogger(AWDataManagement.class);
	private static ResourceBundle properties = ResourceBundle.getBundle("resources/serviceConf");
	private static String workDir = System.getenv(properties.getString("animalwelfare.workDirectory"));
	//private static String filePath = workDir + properties.getString("serviceDataManagement.filePath");
	private static String fileNameSuffix = properties.getString("serviceDataManagement.fileNameSuffix");
	private static String fileExtension = properties.getString("serviceDataManagement.fileExtension");
	
	private static String tempFilePath = workDir + properties.getString("serviceDataManagement.tempFilePath");
	
	private static void checkIfDirectoryExistOrCreate(String path) {
		log.debug("Directory checking: "+path);
		File directory = new File(path);
		if (!directory.exists()){
			log.debug("Directory not found, creating: "+path);
	        directory.mkdirs();
	        log.debug("Directory created!");
	    }
	}
	
	private static boolean checkIfDirectoryIsEmpty(String path) {
		log.debug("Checking if directory is empty: "+path);
		 File directory = new File(path);
	      if (directory.isDirectory()) {
	         String[] files = directory.list();
	         if (! (files.length > 0)) {
	        	 log.debug("The directory is empty!");
	        	 return true;
	         }
	      }
	      return false;
	}
	
	private static void deleteFile(String path) {
		File file = new File(path);
	    if (file.delete()) {
	    	log.debug("File deleted successfully: "+path);
	    }
	    else {
	    	log.debug("Failed to delete file: "+path);
	    }
	}
	
	private static void setFileCreationTime(String filePath) throws IOException {
        Path path = Paths.get(filePath);
        FileTime fileTime = FileTime.fromMillis(System.currentTimeMillis());
        /* Changing the Created Time Stamp */
        Files.setAttribute(path, "basic:creationTime", fileTime,LinkOption.NOFOLLOW_LINKS);
    }
	
	private static Date getFileCreationDate(String path) {
		log.debug("Getting creation date for the file: "+path);
		Date creationDate = null;
		try {
            Path file = Paths.get(path);
            BasicFileAttributes attr = Files.readAttributes(file, BasicFileAttributes.class);
            creationDate = Date.from(attr.creationTime().toInstant());
            log.debug("Creation date: "+creationDate.toString());

        } catch (IOException e) {
            e.printStackTrace();
        }
		return creationDate;
	}
	
	private static boolean isDateExpired(Date dateToCompare) {
		log.debug("Checking expiration file date");
		Date currentDateTime = new Date();
		log.debug("Current time: "+currentDateTime.toString());
		Date increasedDate = Date.from(dateToCompare.toInstant().plus(Duration.ofMinutes(5)));
		log.debug("Exipration time: "+increasedDate.toString());
		return increasedDate.before(currentDateTime);
	}
	
	public static String manageDataToStoreTemporary(String operation) {
		log.debug("Manage data to store.");
		String dataToStore = "";
		String completeTempPath = tempFilePath+operation+"/";
		checkIfDirectoryExistOrCreate(completeTempPath);
		String fileNamePrefix = operation;
		String fileName = fileNamePrefix+fileNameSuffix+fileExtension;
		String fullPath = completeTempPath+fileName;
		log.debug("Data file directory: "+fullPath);
		if (checkIfDirectoryIsEmpty(completeTempPath)) {
			// DIRECTORY IS EMPTY LET'S SAVE OUR DATA AFTER GET IT
			dataToStore = sendToPythonAndGetResult(operation);
			log.debug("Saving temporary data file");
			storeDataToFile(dataToStore,fullPath);
		} else {
			// GET FILE CREATION DATE
			Date fileCreatedAt = getFileCreationDate(fullPath);
			if (fileCreatedAt!= null) {
				if (isDateExpired(fileCreatedAt)) {
					// TEMPORARY DATA FILE IS EXPIRED , DELETE AND CREATE A NEW ONE AFTER GET THE RESULTS FROM PYTHON
					log.debug("File expired, delete.");
					deleteFile(fullPath);
					dataToStore = sendToPythonAndGetResult(operation);
					log.debug("Saving temporary data file");
					storeDataToFile(dataToStore,fullPath);
				} else {
					// TEMPORARY FILE NOT EXPIRED, LET'S READ THE CONTENT AND RETURN IT AS STRING
					log.debug("File not expired, reading the content...");
					dataToStore = readDataFromFile(fullPath);
				}
			} else {
				log.debug("Creation Date is null!");
			}
		}
		return dataToStore;
	}
	
	private static void storeDataToFile(String dataToStore, String fullPath) {
		log.debug("Storing data into file.");
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
    				writer.close();
    				setFileCreationTime(fullPath);
    			}
    			catch (IOException e) {
    				log.error("An exception occured!",e);
    				e.printStackTrace();
    			}
    		}	
		}    		
	}
	
	private static String readDataFromFile(String fullPath) {
		log.debug("Reading data from file.");
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
			log.error("File "+fullPath+" does not exists!");
			JSONObject err = new JSONObject();
    		err.put("Code", "1");
    		err.put("Type", "Function Error: readDataFromFile");
    		err.put("Description", "The file "+fullPath+" does not exists!");
    		outData = err.toString();
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
	
	// (CURRENTLY NOT USED)
	/*
	public static void storeToFile(String dataToStore, String operation) {
		log.debug("Storing data into file.");
		String fileNamePrefix = operation;
		String fileName = fileNamePrefix+fileNameSuffix+fileExtension;
		String fullPath = filePath+fileName;
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
	
	// (CURRENTLY NOT USED)
	public static String readFromFile(String operation) {
		log.debug("Reading data from file.");
		String fileNamePrefix = operation;
		String fileName = fileNamePrefix+fileNameSuffix+fileExtension;
		String fullPath = filePath+fileName;
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
			log.error("File "+fullPath+" does not exists!");
			JSONObject err = new JSONObject();
    		err.put("Code", "1");
    		err.put("Type", "Service Error: "+operation);
    		err.put("Description", "The file "+fullPath+" does not exists!");
    		outData = err.toString();
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

	// (CURRENTLY NOT USED)
    public static String readDataAndSend(InputStream requestBody,String operation) {
    	log.debug("Init reading data and store method...");
    	String jsonDataOutput = "";
    	String line;
    	PyModuleExecutor pyExe = new PyModuleExecutor();
    	InputStreamReader inputStream = new InputStreamReader(requestBody);
		BufferedReader reader = new BufferedReader(inputStream);
        StringBuilder jsonDataInput = new StringBuilder();
        log.debug("Initialization completed!");
    	try {
    		log.debug("Reading request body.");
	        while ((line = reader.readLine()) != null) {
	        	jsonDataInput.append(line);
	        }
	        log.debug("Sending data to python executor class.");
        	jsonDataOutput = pyExe.executeFunction(jsonDataInput.toString(),operation);
        	log.debug("Store dataset to file.");
	        storeToFile(jsonDataOutput,operation);
		} catch (IOException e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
		} finally {
    		if (reader != null) {
    			try {
    				log.debug("Closing the reader.");
    				reader.close();
    			}
    			catch (IOException e) {
    				log.error("An exception occured!",e);
    				e.printStackTrace();
    			}
    		}
    	}
		return jsonDataOutput;
    }
    */
    public static String sendToPythonAndGetResult(String operation) {
    	log.debug("Init send to python and get result method...");
    	String jsonDataOutput = "";
    	String urlAIMTraslator = "";
    	PyModuleExecutor pyExe = new PyModuleExecutor();
        log.debug("Initialization completed!");
    	try {
    		switch(operation) 
	        { 
	            case "Training": 
	            	log.debug("Set TRAINING URL for AIM Traslator");
	            	urlAIMTraslator = System.getenv(properties.getString("animalwelfare.AIMTraslatorServiceURL.Training"));
	                break; 
	            case "Prediction": 
	            	log.debug("Set PREDICTION URL for AIM Traslator");
	            	urlAIMTraslator = System.getenv(properties.getString("animalwelfare.AIMTraslatorServiceURL.Prediction"));
	            	break;
	        }
	        log.debug("Sending data to python executor class.");
        	jsonDataOutput = pyExe.executeFunction(urlAIMTraslator,operation);
		} catch (Exception e) {
			log.error("An exception occured!",e);
			e.printStackTrace();
		}
		return jsonDataOutput;
    }
}
