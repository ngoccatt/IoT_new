/*
The MIT License (MIT)

Copyright (c) 2018 Giovanni Paolo Vigano'

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;
using M2MqttUnity;
using Newtonsoft.Json.Linq;
using System.Linq;
using Newtonsoft.Json;




/// <summary>
/// Examples for the M2MQTT library (https://github.com/eclipse/paho.mqtt.m2mqtt),
/// </summary>
namespace M2MqttUnity.yahalloMQTT
{

    //copy json string, edit -> paste special
    //cac thuoc tinh json duoc dat o ngoai class.
    public class Status
    {
        public int temperature { get; set; }
        public int humidity { get; set; }
        public Status(int temp, int humi)
        {
            this.temperature = temp;
            this.humidity = humi;
        }
    }


    public class Device
    {
        public string device { get; set; }
        public string status { get; set; }
        public Device(string deviceName, string status)
        {
            this.device = deviceName;
            this.status = status;
        }
    }



    public class Message
    {
        public string message { get; set; }
        public string topic { get; set; }
    }


    /// <summary>
    /// Script for testing M2MQTT with a Unity UI
    /// </summary>
    public class yahallo_script : M2MqttUnityClient
    {
        [SerializeField]
        private Manager_script manager_object;
        [Tooltip("Set this to true to perform a testing cycle automatically on startup")]
        public bool autoTest = false;
        public string[] Topics;
        //Topics[0] -> status
        //Topics[1] -> led
        //Topics[2] -> pump
        public string Msg_receive_from_topic_status;
        public string Msg_receive_from_topic_control;
        public string Msg_receive_from_topic_fan;


        
        //private bool first_time_connect = false;


        private List<Message> eventMessages = new List<Message>();


        public void TestPublish()
        {
            client.Publish("M2MQTT_Unity/test", System.Text.Encoding.UTF8.GetBytes("Test message"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Test message published");
            manager_object.AddUiMessage("Test message published.");
        }

       


        public override void Connect()
        {
            try
            {
                base.Connect();
            }
            catch
            {
                manager_object.Notification_message(true, "Something went wrong");
            }
        }

        protected override void OnConnecting()
        {
            base.OnConnecting();
            manager_object.Notification_message(false, "Connecting to broker on " + brokerAddress + ":" + brokerPort.ToString() + "...\n");
        }

        protected override void OnConnected()
        {
            base.OnConnected();
            manager_object.Notification_message(false, "Connected to broker on " + brokerAddress + "\n");

            manager_object.switch_layer();

            //if (!first_time_connect)
            //{
            //    first_time_connect = true;
            //    StartCoroutine(RequestDataEvery5Sec());
            //}
        }

        protected override void SubscribeTopics()
        {
            //client.Subscribe(new string[] { "v1/devices/me/rpc/request/+" }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
            //client.Subscribe(new string[] { "v1/devices/me/attributes" }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
            for (int i = 0; i < Topics.Length; i++)
            {
                client.Subscribe(new string[] { Topics[i] }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
            }

        }

        protected override void UnsubscribeTopics()
        {
            //client.Unsubscribe(new string[] { "v1/devices/me/rpc/request/+" });
            //client.Unsubscribe(new string[] { "v1/devices/me/attributes" });
            for (int i = 0; i < Topics.Length; i++)
            {
                client.Unsubscribe(new string[] { Topics[i] });
            }

        }

        public void Publish_message(string topic, string message)
        {
            //retain value must be true
            client.Publish(topic, System.Text.Encoding.UTF8.GetBytes(message),
                MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE, true);
        }

        protected override void OnConnectionFailed(string errorMessage)
        {
            manager_object.Notification_message(true, "Connection failed");
            base.OnConnectionFailed(errorMessage);
        }

        protected override void OnDisconnected()
        {
            manager_object.Notification_message(true, "Disconnected");
            manager_object.switch_layer();
            //UnsubscribeTopics(); ko can unsub o day. Khi nhan button logout, ham Disconnect duoc goi da unsub roi.
            base.OnDisconnected();
            //first_time_connect = false;
        }

        protected override void OnConnectionLost()
        {
            manager_object.Notification_message(true, "Connection lost!");
            base.OnConnectionLost();
        }

       

        protected override void Start()
        {
            manager_object.Notification_message(false, "Ready");
            base.Start();

        }

        //them event vao ham OnEnable
       

        //this function is called when a message is received.
        protected override void DecodeMessage(string topic, byte[] message)
        {
            string msg = System.Text.Encoding.UTF8.GetString(message);
            Message temp_message = new Message()
            {
                topic = topic,
                message = msg
            };
            Debug.Log("Received: " + msg + "\nFrom topic: " + topic);
            StoreMessage(temp_message);
        }

        private void StoreMessage(Message eventMsg)
        {
            eventMessages.Add(eventMsg);
        }

        private void ProcessMessage(Message msg)
        {
            if (msg.topic == Topics[0])         //status topic
            {
                manager_object.updateStatus(msg.message);
            }
            else if (msg.topic == Topics[1])    //led topic
            {
               manager_object.updateLed(msg.message);
            }
            else //msg.topic == Topic[2]        //pump topic
            {
                manager_object.updatePump(msg.message);
            }
        }

        protected override void Update()
        {
            base.Update(); // call ProcessMqttEvents()

            if (eventMessages.Count > 0)
            {
                foreach (Message msg in eventMessages)
                {
                    ProcessMessage(msg);
                }
                eventMessages.Clear();
            }
        }

        private void OnDestroy()
        {
            Disconnect();
        }

        private void OnValidate()
        {
            if (autoTest)
            {
                autoConnect = true;
            }
        }

    }
}
