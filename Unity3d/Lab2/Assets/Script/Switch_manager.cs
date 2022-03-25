using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using DG.Tweening;

public class Switch_manager : MonoBehaviour, IPointerDownHandler
{

    [SerializeField]
    private Image switchCircle;
    [SerializeField]
    private Image switchBackground;
    public Color onColor;
    public Color offColor;

    private float offX;
    private float onX;

    private bool isOn;

    [SerializeField]
    private float tweentime = 0.25f;

    public delegate void SwitchChange(bool value);
    public event SwitchChange onSwitchChange;

    private AudioSource clickaudio;
    
    //chi cho phep get value cua switch
    public bool _isOn
    {
        get { return isOn; }
    }
    // Start is called before the first frame update
    void Start()
    {
        offX = switchCircle.rectTransform.anchoredPosition.x;
        onX = -switchCircle.rectTransform.anchoredPosition.x;
        isOn = false;
        ToggleSwitch(isOn);
        clickaudio = GetComponent<AudioSource>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void OnPointerDown(PointerEventData eventData)
    {
        ToggleSwitch(!isOn);
    }

    public void ToggleSwitch(bool value)
    {
        if (value != isOn)
        {
            //do co luu thuoc tinh isOn, minh se han che viec toggle neu
            //button da o trang thai value roi (ko can toggle lai)
            isOn = value;

            ToggleBackground(isOn);
            MoveCircle(isOn);

            if (onSwitchChange != null)
            {
                //kich hoat event.
                onSwitchChange(isOn);
            }

            clickaudio.Play();

        }
    }

    private void ToggleBackground(bool value)
    {
        if(value == true)
        {
            switchBackground.DOColor(onColor, tweentime);
        } else
        {
            switchBackground.DOColor(offColor, tweentime);
        }
    }

    private void MoveCircle(bool value)
    {
        if(value == true)
        {
            switchCircle.rectTransform.DOAnchorPosX(onX, tweentime);
        } else
        {
            switchCircle.rectTransform.DOAnchorPosX(offX, tweentime);
        }
    }
}
