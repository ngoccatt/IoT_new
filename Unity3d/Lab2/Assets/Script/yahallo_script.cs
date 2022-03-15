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
        [Tooltip("Set this to true to perform a testing cycle automatically on startup")]
        public bool autoTest = false;
        [Header("User Interface")]
        public InputField BrokerURL;
        public InputField Username;
        public InputField Password;
        public InputField Notification;
        public Button ConnectButton;
        public GameObject Mainmenu, Data;
        public GameObject TempHolder, HumidHolder;
        public Switch_manager led1, pump1;
        public GameObject gauge1, gauge2;
        public string[] Topics;
        //Topics[0] -> status
        //Topics[1] -> led
        //Topics[2] -> pump
        public string Msg_receive_from_topic_status;
        public string Msg_receive_from_topic_control;
        public string Msg_receive_from_topic_fan;


        private int humidity, temperature;
        //private bool first_time_connect = false;


        private List<Message> eventMessages = new List<Message>();
        private bool updateUI = false;

        public void TestPublish()
        {
            client.Publish("M2MQTT_Unity/test", System.Text.Encoding.UTF8.GetBytes("Test message"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Test message published");
            AddUiMessage("Test message published.");
        }

        public void SetBrokerAddress(string brokerAddress)
        {
            if (BrokerURL && !updateUI)
            {
                this.brokerAddress = brokerAddress;
            }
        }

        public void SetUsername(string username)
        {
            if (Username && !updateUI)
            {
                this.mqttUserName = username;
            }
        }

        public void SetPassword(string password)
        {
            if (Password && !updateUI)
            {
                this.mqttPassword = password;
            }
        }

        public void SetEncrypted(bool isEncrypted)
        {
            this.isEncrypted = isEncrypted;
        }


        public void SetUiMessage(string msg)
        {
            if (Notification != null)
            {
                Notification.text = msg;
                updateUI = true;
            }

        }

        public override void Connect()
        {
            try
            {
                base.Connect();
            }
            catch
            {
                Notification.image.color = new Color32(255, 118, 117, 127);
                AddUiMessage("Something went wrong");
            }
        }

        public void AddUiMessage(string msg)
        {
            if (Notification != null)
            {
                Notification.text += msg + "\n";
                updateUI = true;
            }
        }

        protected override void OnConnecting()
        {
            base.OnConnecting();
            Notification.image.color = new Color32(85, 239, 196, 127);
            SetUiMessage("Connecting to broker on " + brokerAddress + ":" + brokerPort.ToString() + "...\n");
        }

        protected override void OnConnected()
        {
            base.OnConnected();
            Notification.image.color = new Color32(85, 239, 196, 127);
            SetUiMessage("Connected to broker on " + brokerAddress + "\n");

            Mainmenu.SetActive(false);
            Data.SetActive(true);

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

        protected override void OnConnectionFailed(string errorMessage)
        {
            Notification.image.color = new Color32(255, 118, 117, 127);
            SetUiMessage("CONNECTION FAILED! " + errorMessage);
            base.OnConnectionFailed(errorMessage);
        }

        protected override void OnDisconnected()
        {
            Notification.image.color = new Color32(255, 118, 117, 127);
            SetUiMessage("Disconnected.");
            Data.SetActive(false);
            Mainmenu.SetActive(true);
            //UnsubscribeTopics(); ko can unsub o day. Khi nhan button logout, ham Disconnect duoc goi da unsub roi.
            base.OnDisconnected();
            //first_time_connect = false;
        }

        protected override void OnConnectionLost()
        {
            Notification.image.color = new Color32(255, 118, 117, 127);
            SetUiMessage("CONNECTION LOST!");
            base.OnConnectionLost();
        }

        private void UpdateUI()
        {
            if (BrokerURL != null)
            {
                BrokerURL.text = brokerAddress;
            }
            if (Username != null)
            {
                Username.text = mqttUserName;
            }
            if (Password != null)
            {
                Password.text = mqttPassword;
            }
            updateUI = false;
        }

        protected override void Start()
        {
            SetUiMessage("Ready.");
            Notification.image.color = new Color32(85, 239, 196, 127);
            updateUI = true;
            Mainmenu.SetActive(true);
            Data.SetActive(false);
            base.Start();

        }

        public void OnEnable()
        {
            led1.onSwitchChange += Led1_onSwitchChange;
            pump1.onSwitchChange += Pump1_onSwitchChange;
        }

        public void OnDisable()
        {
            //phai luon nho *cat* cai event ra.
            led1.onSwitchChange -= Led1_onSwitchChange;
            pump1.onSwitchChange -= Pump1_onSwitchChange;
        }

        private void Pump1_onSwitchChange(bool value)
        {
            //string jsonString = "{\"device\":\"PUMP\", \"status\":" + (value ? "\"ON\"" : "\"OFF\"") + "}";
            Device jsonDevice = new Device("PUMP", value ? "ON" : "OFF");
            string jsonString = JsonConvert.SerializeObject(jsonDevice);
            //retain value must be true
            client.Publish("/bkiot/1912750/pump", System.Text.Encoding.UTF8.GetBytes(jsonString), MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE, true);
        }

        private void Led1_onSwitchChange(bool value)
        {
            //string jsonString = "{\"device\":\"LED\", \"status\":" + (value ? "\"ON\"" : "\"OFF\"") + "}";
            Device jsonDevice = new Device("LED", value ? "ON" : "OFF");
            string jsonString = JsonConvert.SerializeObject(jsonDevice);
            //retain value must be true
            client.Publish("/bkiot/1912750/led", System.Text.Encoding.UTF8.GetBytes(jsonString), MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE, true);
        }

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
                Status jsonStatus = JsonConvert.DeserializeObject<Status>(msg.message);
                temperature = jsonStatus.temperature;
                humidity = jsonStatus.humidity;
                TempHolder.GetComponentsInChildren<Text>()[1].text = temperature + "°C";
                HumidHolder.GetComponentsInChildren<Text>()[1].text = humidity + "%";

                //gauge1: temperature
                gauge1.GetComponent<Image>().fillAmount = (float)temperature / 100;
                gauge1.GetComponentInChildren<Text>().text = temperature + "°C";
                //gauge2: humidity
                gauge2.GetComponent<Image>().fillAmount = (float)humidity / 100;
                gauge2.GetComponentInChildren<Text>().text = humidity + "%";
            }
            else if (msg.topic == Topics[1])    //led topic
            {
                Device jsonDevice = JsonConvert.DeserializeObject<Device>(msg.message);
                if (jsonDevice.status == "ON")
                {
                    led1.ToggleSwitch(true);
                } else if (jsonDevice.status == "OFF")
                {
                    led1.ToggleSwitch(false);
                }
            }
            else //msg.topic == Topic[2]        //pump topic
            {
                Device jsonDevice = JsonConvert.DeserializeObject<Device>(msg.message);
                if (jsonDevice.status == "ON")
                {
                    pump1.ToggleSwitch(true);
                }
                else if (jsonDevice.status == "OFF")
                {
                    pump1.ToggleSwitch(false);
                }
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
            if (updateUI)
            {
                UpdateUI();
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
