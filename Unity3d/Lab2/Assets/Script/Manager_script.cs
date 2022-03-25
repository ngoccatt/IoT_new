using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Newtonsoft.Json.Linq;
using System.Linq;
using Newtonsoft.Json;
using DG.Tweening;

namespace M2MqttUnity.yahalloMQTT
{
    public class Manager_script : MonoBehaviour
    {
        [SerializeField]
        private yahallo_script MQTT_object;
        [Header("User Interface")]
        public InputField BrokerURL;
        public InputField Username;
        public InputField Password;
        public InputField Notification;
        public Button ConnectButton;
        public CanvasGroup Mainmenu, Data;
        public GameObject TempHolder, HumidHolder;
        public Switch_manager led1, pump1;
        public GameObject gauge1, gauge2;

        private bool updateUI = false;

        private Tween twenFade;

        private int humidity, temperature;

        public void SetBrokerAddress(string brokerAddress)
        {
            if (BrokerURL)
            {
                MQTT_object.brokerAddress = brokerAddress;
            }
        }

        public void SetUsername(string username)
        {
            if (Username)
            {
                MQTT_object.mqttUserName = username;
            }
        }

        public void SetPassword(string password)
        {
            if (Password)
            {
                MQTT_object.mqttPassword = password;
            }
        }

        public void SetUiMessage(string msg)
        {
            if (Notification != null)
            {
                Notification.text = msg;
                updateUI = true;
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

        public void Notification_message(bool error, string message)
        {
            if (error == true)  //error
            {
                Notification.image.color = new Color32(255, 118, 117, 127);
            } else //not error
            {
                Notification.image.color = new Color32(85, 239, 196, 127);
            }
            SetUiMessage(message);
        }

        // Start is called before the first frame update
        void Start()
        {
            updateUI = true;
            Mainmenu.alpha = 1;
            Mainmenu.interactable = true;
            Mainmenu.blocksRaycasts = true;
            Data.alpha = 0;
            Data.interactable = false;
            Data.blocksRaycasts = false;
        }

        // Update is called once per frame
        void Update()
        {
            if (updateUI)
            {
                UpdateUI();
            }
        }

        public void Fade(CanvasGroup _canvas, float endvalue, float duration, TweenCallback onFinish)
        {
            if (twenFade != null)
            {
                twenFade.Kill(false);
            }
            twenFade = _canvas.DOFade(endvalue, duration);
            twenFade.onComplete += onFinish;
        }

        public void FadeIn(CanvasGroup _canvas, float duration)
        {
            Fade(_canvas, 1f, duration, () =>
            {
                _canvas.interactable = true;
                _canvas.blocksRaycasts = true;
            });
        }

        public void FadeOut(CanvasGroup _canvas, float duration)
        {
            Fade(_canvas, 0f, duration, () =>
            {
                _canvas.interactable = false;
                _canvas.blocksRaycasts = false;
            });
        }

        IEnumerator _IESwitchLayer()
        {
            if (Mainmenu.interactable == true)
            {
                FadeOut(Mainmenu, 0.25f);
                yield return new WaitForSeconds(0.5f);
                FadeIn(Data, 0.25f);
            } else
            {
                FadeOut(Data, 0.25f);
                yield return new WaitForSeconds(0.5f);
                FadeIn(Mainmenu, 0.25f);
            }
        }

        public void switch_layer()
        {
            StartCoroutine(_IESwitchLayer());
        }

        public void OnEnable()
        {
            //them event vao.
            led1.onSwitchChange += Led1_onSwitchChange;
            pump1.onSwitchChange += Pump1_onSwitchChange;
        }

        //xoa event trong ham OnDisable
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
            MQTT_object.Publish_message("/bkiot/1912750/pump", jsonString);
        }

        private void Led1_onSwitchChange(bool value)
        {
            //string jsonString = "{\"device\":\"LED\", \"status\":" + (value ? "\"ON\"" : "\"OFF\"") + "}";
            Device jsonDevice = new Device("LED", value ? "ON" : "OFF");
            string jsonString = JsonConvert.SerializeObject(jsonDevice);
            MQTT_object.Publish_message("/bkiot/1912750/led", jsonString);
        }

        private void UpdateUI()
        {
            if (BrokerURL != null)
            {
                BrokerURL.text = MQTT_object.brokerAddress;
            }
            if (Username != null)
            {
                Username.text = MQTT_object.mqttUserName;
            }
            if (Password != null)
            {
                Password.text = MQTT_object.mqttPassword;
            }
            updateUI = false;
        }

        public void updateStatus(string jsonString)
        {
            Status jsonStatus = JsonConvert.DeserializeObject<Status>(jsonString);
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

        public void updateLed(string jsonString)
        {
            Device jsonDevice = JsonConvert.DeserializeObject<Device>(jsonString);
            if (jsonDevice.status == "ON")
            {
                led1.ToggleSwitch(true);
            }
            else if (jsonDevice.status == "OFF")
            {
                led1.ToggleSwitch(false);
            }
        }

        public void updatePump(string jsonString)
        {
            Device jsonDevice = JsonConvert.DeserializeObject<Device>(jsonString);
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
}
