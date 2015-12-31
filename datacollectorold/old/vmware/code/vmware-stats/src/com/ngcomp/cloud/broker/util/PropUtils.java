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

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import org.apache.commons.io.IOUtils;

/**
 * 
 * @author rparashar
 *
 */
public class PropUtils {
	
	private static PropUtils instance;
	
	private Properties props;
	
	public static void init(String configFilePath) throws IOException 
	{
		PropUtils.instance = new PropUtils(configFilePath);
	}
	
	/**
	 * 
	 * @throws IOException
	 */
	private PropUtils(String configFilePath) throws IOException 
	{
		Properties p = new Properties();
		FileInputStream in = null;
		try {
			in = new FileInputStream(configFilePath);
			p.load(in);
		}
		finally 
		{
			IOUtils.closeQuietly(in);
		}
		this.props = p;
	}
	
	/**
	 * 
	 * @return
	 * @throws IOException
	 */
	public static PropUtils getInstance() {		
	     return PropUtils.instance;
	}
	
	/**
	 * 
	 * @param prop
	 * @param defaultVal
	 * @return
	 */
	public Object getVal(String prop, String defaultVal) 
	{
		if (this.props.containsKey(prop)) 
		{
			return this.props.getProperty(prop, defaultVal).trim();
		}
		else 
		{
			return defaultVal;
		}
	}
	
	/**
	 * 
	 * @param prop
	 * @return
	 */
	public Object getVal(String prop) 
	{
		if (this.props.containsKey(prop)) 
		{
			return this.props.getProperty(prop).trim();
		}
		else 
		{
			return null;
		}
	}
}
