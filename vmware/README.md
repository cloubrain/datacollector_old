Data collector for VMWare 

There are two ways for us to collect the data from your VMWare: online and offline. The online version will send your data via Internet to your server. And the offline version will store your data locally as mongoDB database. 
We are going to collect your data via VCenter in VMWare. 

1. Set up your environment (There will be different between different platforms): install java, install mongoDB. 
2. Install: 
Create "vCenter.config" file as below

  vcenter_url=https://your.vcenter.link/sdk                                                                                     
  vcenter_uid=your.user.name                                                                                                    
  vcenter_pwd=your.pass.word                                                                                                  
  upload=false                                                                                                                
  perf_items=cpu.usagemhz.average,mem.usage.average
  
  
upload option
  true: online version
  false: offline version
  
3. Run

Collect your data from vCenter
  java -jar collect.jar <your.config.file>
  
  
Will create image files of visualization for your data
  java -jar collect.jar visualization



