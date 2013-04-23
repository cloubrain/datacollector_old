//////////////////////////////////////////////////////////////////////////////
// Author:: Ram Parashar (ramp@ngcomp.org>)
//
// Copyright 2012, Next Generation Computing.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
///////////////////////////////////////////////////////////////////////////////

package com.ngcomp.cloud.broker.thread;

import java.io.IOException;
import java.net.URL;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import com.ngcomp.cloud.broker.Rbmq;
import com.ngcomp.cloud.broker.util.PropUtils;
import com.ngcomp.cloud.broker.util.StatsHelper;
import com.ngcomp.cloud.database.LocalDatabase;
import com.vmware.vim25.PerfEntityMetricBase;
import com.vmware.vim25.PerfEntityMetricCSV;
import com.vmware.vim25.PerfMetricId;
import com.vmware.vim25.PerfMetricSeriesCSV;
import com.vmware.vim25.PerfQuerySpec;
import com.vmware.vim25.mo.InventoryNavigator;
import com.vmware.vim25.mo.ManagedEntity;
import com.vmware.vim25.mo.PerformanceManager;
import com.vmware.vim25.mo.ServiceInstance;
import com.vmware.vim25.mo.VirtualMachine;

public class RealtimePerfMonitor implements Runnable 
{

	private static final Logger logger = Logger.getLogger(RealtimePerfMonitor.class.getName());
	private String ip;
	/**
	 * 
	 * 
	 */
	
	public RealtimePerfMonitor(String ip)
	{
		this.ip = ip; 
	}
	@SuppressWarnings("unchecked")
	public void run() 
	{
		try 
		{
//			Map<String, Double> keyMap = new HashMap<String, Double>();
			logger.info("RealtimePerfMonitor=>" + new java.util.Date(System.currentTimeMillis()));
			PropUtils props = PropUtils.getInstance();
			
			String url = (String) props.getVal("vcenter_url");
			String uid = (String) props.getVal("vcenter_uid");
			String pwd = (String) props.getVal("vcenter_pwd");
			
			ServiceInstance si = new ServiceInstance(new URL(url), uid, pwd, true);
			PerformanceManager perfMgr = si.getPerformanceManager();
			InventoryNavigator nav = new InventoryNavigator(si.getRootFolder());

			
			ManagedEntity[] managedEntities = nav.searchManagedEntities("VirtualMachine");
			
			JSONObject jsonO = new JSONObject();
			JSONArray  jsonA = new JSONArray();
			
			List<String> vms = new LinkedList<String>();
			for (ManagedEntity managedEntity : managedEntities) 
			{
				
				VirtualMachine vm = (VirtualMachine)managedEntity;
				
				if("poweredoff".equalsIgnoreCase(vm.getRuntime().getPowerState().toString()))
					continue;
				
				//System.out.println(vm.getConfig().getUuid()  + " " + vm.getName());
				
				PerfQuerySpec qSpec = createPerfQuerySpec( managedEntity, StatsHelper.getMetricItems(), 1, 20);
				qSpec.setMaxSample(1);
				qSpec.setIntervalId(20);
				PerfEntityMetricBase[] pValues = perfMgr.queryPerf(new PerfQuerySpec[] { qSpec });
				if (pValues != null) 
				{
					String name = managedEntity.getName();
					vms.add(name);
					jsonA.add(displayValues(pValues, name, vm.getConfig().getUuid()));
				}
			}
			
			StringBuilder stbldr = new StringBuilder();

			for (String name : vms) 
			{
				stbldr.append(name).append(", ");
			}
			jsonO.put("VM_LIST", stbldr.toString());
			jsonO.put("STATS"  , jsonA);
			
			// ntdo: if upload=false just print out on console
			String upload = (String) props.getVal("upload");
			String host = (String) props.getVal("host");
			if (!(upload == null || upload.toLowerCase().equals("false"))) {
				Rbmq.postMessageToQueue(jsonO, host, this.ip);
			} 
			
			//System.out.println("VM list(CSV) =>" + stbldr.toString());
			stbldr = null;
		}
		catch (Exception e) 
		{
			logger.info(e.getMessage());
			e.printStackTrace();
		}
	}

	/**
	 * 
	 * @param val
	 * @return
	 */
	private static String parseVal(String val)
	{
		if(val.contains(",")) val = val.split(",")[0];
		return val;
	}
	
	/**
	 * 
	 * @param values
	 * @param vmName
	 * @throws IOException
	 * Push details for single Vm 
	 */
	@SuppressWarnings("unchecked")
	private static JSONObject displayValues(PerfEntityMetricBase[] values, String vmName, String uuid) throws IOException 
	{
		
		JSONObject json = new JSONObject();
		json.put("uuid", uuid);
		json.put("name", vmName);
		
		Map<String, Double> keyMap = new HashMap<String, Double>();
		StringBuilder key =  new StringBuilder();
		vmName = StatsHelper.getVmName(vmName);
		JSONArray jsonA = new JSONArray();
		for (int i = 0; i < values.length; ++i) 
		{
			if (values[i] instanceof PerfEntityMetricCSV) 
			{
				
				PerfMetricSeriesCSV[] csvs = ((PerfEntityMetricCSV) values[i]).getValue();
				
				for (int cntr = 0; cntr < csvs.length; cntr++) 
				{
					int keyId = csvs[cntr].getId().getCounterId();
					key.append(keyId);
					String val = parseVal(csvs[cntr].getValue());
					String k   = key.toString();
					if(!keyMap.containsKey(k))
					{
						keyMap.put(k, Double.valueOf(val));
					}
					else
					{
						double old    = keyMap.get(k);
						double latest = Long.valueOf(val);
						double newVal = 0;
						newVal = (old + latest)/2;
						keyMap.put(k, Double.valueOf(newVal));
					}
					key.delete(0, key.length());
				}
			}
		}
		
		for(String k : keyMap.keySet())
		{
			JSONObject j = new JSONObject();
			j.put("k", k);
			j.put("v", keyMap.get(k).toString());
			jsonA.add(j);
		}
		json.put("STATS", jsonA);
		
		// ntdo: add to local database if upload=false
		PropUtils props = PropUtils.getInstance();
		String upload = (String) props.getVal("upload");
		if (upload == null || upload.toLowerCase().equals("false")) {
			// connect to local database
			LocalDatabase.store(json);
		}
		System.out.println(json.toString());
		return json;
	}
	
	/**
	 * 
	 * @param me
	 * @param metricIds
	 * @param maxSample
	 * @param interval
	 * @return
	 */
	private static PerfQuerySpec createPerfQuerySpec(ManagedEntity me, PerfMetricId[] metricIds, int maxSample, int interval) 
	{
		PerfQuerySpec qSpec = new PerfQuerySpec();
		qSpec.setEntity(me.getMOR());
		qSpec.setMaxSample(new Integer(maxSample));
		qSpec.setMetricId(metricIds);
		qSpec.setFormat("csv");
		qSpec.setIntervalId(new Integer(interval));
		return qSpec;
	}

	/**
	 * 
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception 
	{
		/*
		PropUtils.init("/Users/rparashar/Desktop/vcenter_config.props");
		
		StatsHelper.initializePerfCounters();
		
		RealtimePerfMonitor realtimePerfMonitor = new RealtimePerfMonitor();
		Thread realtimePerfMonitorThread = new Thread(realtimePerfMonitor);
		realtimePerfMonitorThread.start();
		*/
	}
}
