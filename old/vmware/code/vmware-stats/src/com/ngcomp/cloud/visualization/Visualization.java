package com.ngcomp.cloud.visualization;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Scanner;

import javax.imageio.ImageIO;

import org.jfree.chart.JFreeChart;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.util.JSON;
import com.ngcomp.cloud.database.LocalDatabase;

public class Visualization {
	public Visualization() {
		
	}
	
	public static void importVisualization() throws IOException {
		Hashtable<String, VMachine> setMachines = new Hashtable<String, VMachine>();
		
		try {
			// try to read from locla database mongoDB server
			Mongo m = new Mongo("localhost", 27017);
			DB db = m.getDB("vmware");
			DBCollection collection = db.getCollection("vms");
			
			DBCursor cursorDB = collection.find();
			
			
			while (cursorDB.hasNext()) {
				DBObject temp = cursorDB.next();
				if (temp.containsField("STATS")) {
					String name = temp.get("name").toString();
					if (!setMachines.containsKey(name)) {
						VMachine newMachine = new VMachine(name);
						setMachines.put(name, newMachine);
					}
					
					List<DBObject> list = (List<DBObject>) temp.get("STATS");
					for (DBObject value : list) {
						setMachines.get(name).addResource(value.get("k").toString(), value.get("v").toString());
					}
				}
			}
		} catch (Exception ex) {
			// reading from files
			File file = new File(LocalDatabase.getDate(), "data.txt");
			if (file.exists()) {
				Scanner scan = new Scanner(file);
				while (scan.hasNext()) {
					DBObject temp = (DBObject) JSON.parse(scan.nextLine());
					if (temp.containsField("STATS")) {
						String name = temp.get("name").toString();
						if (!setMachines.containsKey(name)) {
							VMachine newMachine = new VMachine(name);
							setMachines.put(name, newMachine);
						}
						
						List<DBObject> list = (List<DBObject>) temp.get("STATS");
						for (DBObject value : list)
							setMachines.get(name).addResource(value.get("k").toString(), value.get("v").toString());
					}
				}
			}
		}
		
		for (Iterator<String> iter = setMachines.keySet().iterator(); iter.hasNext();) {
			String name = iter.next();
			VMachine machine = setMachines.get(name);
			machine.importVisualization();
			System.out.println(machine);
		}
		
	}
	
	public static void saveToImage(JFreeChart chart, String fileName) throws IOException {
		BufferedImage objBufferedImage= chart.createBufferedImage(600,800);
		ByteArrayOutputStream bas = new ByteArrayOutputStream();
		        try {
		            ImageIO.write(objBufferedImage, "png", bas);
		        } catch (IOException e) {
		            e.printStackTrace();
		        }

		byte[] byteArray=bas.toByteArray();
		
		InputStream in = new ByteArrayInputStream(byteArray);
		BufferedImage image = ImageIO.read(in);
		File outputfile = new File(fileName + ".png");
		ImageIO.write(image, "png", outputfile);
	}
	
	public static void main(String[] args) throws IOException {
		Visualization.importVisualization();
	}
}
