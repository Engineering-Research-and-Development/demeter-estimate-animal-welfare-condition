package it.eng.is3lab.animal_welfare.pyplugin;

import java.io.File;
import java.util.ResourceBundle;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;

public class RFConfigurator {
	private int randomState;
	private int estimators;
	private String configFilePath;
	private String workDir;
	
	public String getConfigFilePath() {
		return configFilePath;
	}

	private void setConfigFilePath(String configFilePath) {
		this.configFilePath = configFilePath;
	}

	public String getWorkDir() {
		return workDir;
	}

	private void setWorkDir(String workDir) {
		this.workDir = workDir;
	}

	private void setRandomState(int rs) {
		this.randomState = rs;
	}
	
	private void setEstimators(int esti) {
		this.estimators = esti;
	}
	
	public int getRandomState() {
		return randomState;
	}

	public int getEstimators() {
		return estimators;
	}

	public void setConfiguration(int randomState, int estimators) throws ConfigurationException {
		File propertiesFile = new File(RFConfigurator.class.getClassLoader().getResource("resources/serviceConf.properties").getFile());
		PropertiesConfiguration config = new PropertiesConfiguration(propertiesFile);           
		config.setProperty("animalwelfare.randomForest.trainingSettings.randomState", randomState);
		config.setProperty("animalwelfare.randomForest.trainingSettings.estimators", estimators);
		config.save();
	}
	
	public void loadConfiguration() throws ConfigurationException {
		ResourceBundle configuration = ResourceBundle.getBundle("resources/serviceConf");
		this.setRandomState(Integer.parseInt(configuration.getString("animalwelfare.randomForest.trainingSettings.randomState")));
		this.setEstimators(Integer.parseInt(configuration.getString("animalwelfare.randomForest.trainingSettings.estimators")));
		this.setConfigFilePath(configuration.getString("animalwelfare.randomForest.configFilePath"));
		this.setWorkDir(configuration.getString("animalwelfare.randomForest.workDirectory"));
	}

}
