package com.ngcomp.cloud.database;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.logging.Logger;

import org.json.simple.JSONObject;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.util.JSON;

public class LocalDatabase {
	private static final Logger logger = Logger.getLogger(LocalDatabase.class.getName());

	public LocalDatabase() {
		
	}
	
	public static void init() {
		
	}
	
	public static void store(JSONObject json) {
		logger.info("INFO: Running offline and store to mongoDB server.");
		
		try { 
			Mongo m = new Mongo("localhost", 27017);
			DB db = m.getDB("vmware");
			DBCollection collection = db.getCollection("vms");
			
			DBObject dbObject = (DBObject) JSON.parse(json.toJSONString());
			collection.insert(dbObject);
		} catch (Exception ex) {
			logger.info("INFO: Can't connect to mongoDB server. Store everything to files");
			
			File directory = new File(getDate());
			boolean success = directory.mkdir();
			if (success) {
				logger.info("INFO: creating a new directory to store data files.");
			}
			
			try{
				// Create file 
				FileWriter fstream = new FileWriter(new File(directory, "data.txt"),true);
				BufferedWriter out = new BufferedWriter(fstream);
				out.write(json.toJSONString() + "\n");
				//Close the output stream
				out.close();
			}catch (Exception e){//Catch exception if any
				System.err.println("Error: " + e.getMessage());
			}
		}
	}
	
	public static String getDate() {
        Calendar today = new GregorianCalendar();
        
        SimpleDateFormat df = new SimpleDateFormat();
        df.applyPattern("dd-MM-yyyy");
        return df.format(today.getTime());
	}
}
