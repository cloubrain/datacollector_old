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

package com.ngcomp.cloud.broker.util;

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import com.ngcomp.cloud.broker.Rbmq;
import com.ngcomp.cloud.database.LocalDatabase;
import com.vmware.vim25.PerfCounterInfo;
import com.vmware.vim25.PerfMetricId;
import com.vmware.vim25.mo.PerformanceManager;
import com.vmware.vim25.mo.ServiceInstance;

public class StatsHelper {
	
	public static final String VCD_VN_NAMES_KEY = "vcd_vm_names";
	
	public static Map<String, String> perfCounterNameMap = new HashMap<String, String>();
	public static Map<String, String>   perfCounterIdMap = new HashMap<String, String>();
	
	@SuppressWarnings("unchecked")
	public static void pushStatsCounterToQueue() throws IOException
	{
		PropUtils props = PropUtils.getInstance();
		String upload = (String) props.getVal("upload");
		boolean online = true;
		if (upload == null || upload.toLowerCase().equals("false")) {
			online = false;
		}
		JSONObject jsonO = new JSONObject();
		jsonO.put("name", "perfCounterNameMap");
		
		JSONArray jsonA = new JSONArray();
		for(String k : StatsHelper.perfCounterNameMap.keySet())
		{
			JSONObject j = new JSONObject();
			j.put("k", k);
			j.put("v", StatsHelper.perfCounterNameMap.get(k));
			jsonA.add(j);
		}
		jsonO.put("COUNTERS", jsonA);
		System.out.println(jsonO.toString());
		if (online) {
			Rbmq.postMessageToQueue(jsonO);
		} else {
			// TODO: send this data to local database or store to file
			LocalDatabase.store(jsonO);
		}
		

		
		jsonO = new JSONObject();
		jsonO.put("name", "perfCounterIdMap");
		
		jsonA = new JSONArray();
		for(String k : StatsHelper.perfCounterIdMap.keySet())
		{
			JSONObject j = new JSONObject();
			j.put("k", k);
			j.put("v", StatsHelper.perfCounterIdMap.get(k));
			jsonA.add(j);
		}
		jsonO.put("COUNTERS", jsonA);
		System.out.println(jsonO.toString());
		if (online) {
			Rbmq.postMessageToQueue(jsonO);
		} else {
			// TODO: store to local database or store to file
			LocalDatabase.store(jsonO);
		}
	}
	
	/**
	 * 
	 */
	public static final void initializePerfCounters() throws IOException 
	{

		PropUtils props = PropUtils.getInstance();
		String url = (String) props.getVal("vcenter_url");
		String uid = (String) props.getVal("vcenter_uid");
		String pwd = (String) props.getVal("vcenter_pwd");
		ServiceInstance si = new ServiceInstance(new URL(url), uid, pwd, true);

		PerformanceManager perfMgr = si.getPerformanceManager();
		PerfCounterInfo[] counters = perfMgr.getPerfCounter();
		if (counters != null) 
		{
			for (PerfCounterInfo counter : counters) 
			{
				String key = counter.getGroupInfo().getKey() + "." + counter.getNameInfo().getKey() + "." + counter.getRollupType().toString();
				StatsHelper.perfCounterNameMap.put(key, Integer.toString(counter.getKey()));
				//System.out.println(key + " =>" + counter.getKey());
				
				StatsHelper.perfCounterIdMap  .put(Integer.toString(counter.getKey()), key);
			}
		}
	}
	
	public static PerfMetricId[] getMetricItems() throws IOException
	{	
		
		List<PerfMetricId> perfList = new ArrayList<PerfMetricId>();
		PropUtils props = PropUtils.getInstance();
		String csvItems = (String)props.getVal("perf_items");

//		System.out.println(csvItems);
		
		for(String item : csvItems.split(","))
		{
			PerfMetricId metric = new PerfMetricId();			
			metric.setCounterId(Integer.valueOf(StatsHelper.perfCounterNameMap.get(item)));
			metric.setInstance("*");		
			perfList.add(metric);
			//metric = null;
		}
		
		int size = perfList.size();
		PerfMetricId[] perfMetricIdArray = new PerfMetricId[size];
		for(int counter=0; counter < size; counter++)
		{
			perfMetricIdArray[counter] = perfList.get(counter);
		}
		return perfMetricIdArray;	
	}

  public static String getVmName(String name) throws IOException
  {	  
	  if(name.contains("(") && name.contains(")"))
	  {
		  String[] tokens = name.split("\\(");
		  String       id = tokens[1].replace(")", "").trim();
		  return id;
	  }
	  else
	  {
		  name = name.replaceAll(" ", "_");
		  return name;
	  }
  }
	
}
