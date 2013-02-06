package com.ngcomp.cloud.visualization;

import java.awt.Color;
import java.io.IOException;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.DefaultCategoryDataset;

public class VMachine {
	private String name;
	private Hashtable<String, List<String>> resources = new Hashtable<String, List<String>>();
	
	public VMachine(String name) {
		this.name = name;
	}
	
	public void addResource(String resource, String value) {
		if (resources.containsKey(resource)) {
			resources.get(resource).add(value);
		} else {
			LinkedList<String> list = new LinkedList<String>();
			list.add(value);
			resources.put(resource, list);
		}
	}
	
	@Override
	public String toString() {
		String result = name + "\n";
		for (Iterator<String> iter = resources.keySet().iterator(); iter.hasNext();) {
			String name = iter.next();
			result += name + ":";
			List<String> list = resources.get(name);
			for (String t : list) {
				result += " " + t;
			}
			result += "\n";
		}
		return result;
	}
	
	public void importVisualization() throws IOException {
		List<JFreeChart> listCharts = new LinkedList<JFreeChart>();
		for (Iterator<String> iter = resources.keySet().iterator(); iter.hasNext();) {
			String ref = iter.next();
			List<String> list = resources.get(ref);
			int time = 0;
			
			DefaultCategoryDataset dataset = new DefaultCategoryDataset();
			for (String t : list) {
				double value = Double.parseDouble(t);
				dataset.addValue(value, ref, String.valueOf(time++));
			}
		    JFreeChart chart = ChartFactory.createAreaChart(name + "_" + ref, ref, "Usage", dataset, PlotOrientation.VERTICAL, true,true, false);
			chart.setBackgroundPaint(Color.yellow);
			chart.getTitle().setPaint(Color.blue); 
			
			Visualization.saveToImage(chart, name + "_" + ref);
		}
	}
}
