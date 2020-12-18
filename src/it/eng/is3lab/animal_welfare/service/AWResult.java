/*
 * Result
 * 
 * Author: Luigi di Corrado
 * Mail: luigi.dicorrado@eng.it
 * Date: 09/10/2020
 * Company: Engineering Ingegneria Informatica S.p.A.
 * 
 * Simple class to send error results as response.
 * 
 * - boolean result       Used to show "false" when an error occure
 * - String  errorCode    Used to show an error code to identify the kind of error:
 * 						  Code: 1 - Used for service exceptions errors
 * 						  Code: 2 - Used for python exceptions errors
 * - String  errorDesc    Description of the error.
 */

package it.eng.is3lab.animal_welfare.service;

public class AWResult {
	private boolean result;
	private String errorCode;
	private String errorDesc;
	
	public boolean isResult() {
		return result;
	}
	
	public void setResult(boolean result) {
		this.result = result;
	}
	
	public String getErrorCode() {
		return errorCode;
	}
	
	public void setErrorCode(String errorCode) {
		this.errorCode = errorCode;
	}
	
	public String getErrorDesc() {
		return errorDesc;
	}
	
	public void setErrorDesc(String errorDesc) {
		this.errorDesc = errorDesc;
	}
	
}