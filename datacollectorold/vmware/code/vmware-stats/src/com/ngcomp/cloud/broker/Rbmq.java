package com.ngcomp.cloud.broker;

import java.io.IOException;

import org.json.simple.JSONObject;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

public class Rbmq {

	public static void postMessageToQueue(JSONObject jsonO, String host) throws IOException
	{
		ConnectionFactory factory = new ConnectionFactory();
		factory.setUsername    ("guest");
		factory.setPassword    ("guest");
		factory.setVirtualHost ("/");
		//factory.setHost        ("ec2-23-20-50-212.compute-1.amazonaws.com");
		//factory.setHost        ("ec2-50-17-115-221.compute-1.amazonaws.com");
		factory.setHost        (host);
	    
	    Connection connection = factory.newConnection();
	    Channel channel = connection.createChannel();
	    
	    channel.exchangeDeclare("CLSTR_MOITORING_EXCHANGE", "fanout"                      , true);
	    channel.queueBind      ("CLSTR_MOITORING"         , "CLSTR_MOITORING_EXCHANGE", "");
	    
	    channel.basicPublish("CLSTR_MOITORING_EXCHANGE", "", null, jsonO.toString().getBytes());
	    
	    channel.close();
	    connection.close();
	}
	
	
	public static void main(String[] argv)throws java.io.IOException 
	{
		
		ConnectionFactory factory = new ConnectionFactory();
		factory.setUsername    ("guest");
		factory.setPassword    ("guest");
		factory.setVirtualHost ("/");
		//factory.setHost        ("ec2-23-20-50-212.compute-1.amazonaws.com");
		//factory.setHost        ("ec2-50-17-115-221.compute-1.amazonaws.com");
		factory.setHost        ("ec2-54-224-154-194.compute-1.amazonaws.com");
	    
	    Connection connection = factory.newConnection();
	    Channel channel = connection.createChannel();
	    
	    channel.exchangeDeclare("CLSTR_MOITORING_EXCHANGE", "fanout"                      , true);
	    channel.queueBind      ("CLSTR_MOITORING"         , "CLSTR_MOITORING_EXCHANGE", "");
	    
	    String message = "Hello World!";	    
	    channel.basicPublish("CLSTR_MOITORING_EXCHANGE", "", null, message.getBytes());
	    System.out.println(" [x] Sent '" + message + "'");
	    
	    channel.close();
	    connection.close();
	}
	
}
