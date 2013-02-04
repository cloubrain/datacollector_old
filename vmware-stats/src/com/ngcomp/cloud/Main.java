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

package com.ngcomp.cloud;

import java.io.IOException;

import com.ngcomp.cloud.broker.thread.RealtimePerfMonitor;
import com.ngcomp.cloud.broker.util.PropUtils;
import com.ngcomp.cloud.broker.util.StatsHelper;

public class Main 
{
	public static void main(String...strings) throws IOException, InterruptedException
	{
		
		if (strings.length < 1)
		{
			System.err.println("Usage: java -jar stats.jar <config.props>");
			System.exit(1);
		}

		final String configFilePath = strings[0];
		PropUtils.init(configFilePath);
		
		StatsHelper.initializePerfCounters();
		
		Thread.sleep(10000);
		
		StatsHelper.pushStatsCounterToQueue();
		
		while(true)
		{
			try
			{
				RealtimePerfMonitor realtimePerfMonitor = new RealtimePerfMonitor();
				Thread realtimePerfMonitorThread        = new Thread(realtimePerfMonitor);
				realtimePerfMonitorThread.start();
			}
			catch(Exception ex)
			{
				
			}
			finally
			{
				Thread.sleep(20000);
			}
		}
	}
}
