using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using DG.Tweening;

//Trong unity, item phia sau se duoc render de len item truoc!

public class Gauge_animation : MonoBehaviour
{
    public Image gaugeBorder;
    public float tweenTime = 0.25f;
    public float speed = 2;
    public float rotateVal = 0;
    private int rotateDirection = 0;

    // Start is called before the first frame update
    void Start()
    {
        gaugeBorder = GetComponent<Image>();
        //gaugeBorder.rectTransform.rotation = new Quaternion(0, 0, (Random.Range(0, 360) * gaugeBorder.rectTransform.position.x) % 360, 0);
        rotateVal = Random.Range(0, 360);
        rotateDirection = Random.Range(0, 2);
    }

    // Update is called once per frame
    void Update()
    {
        StartCoroutine(gaugeRotate());
    }

    IEnumerator gaugeRotate()
    {
        yield return new WaitForSeconds(1);
        if (rotateDirection == 0)
        {
            rotateVal = (rotateVal - speed);        //xoay cung chieu kim dong ho
            if (rotateVal < 360) rotateVal += 360;
        } else
        {
            rotateVal = (rotateVal + speed) % 360;        //xoay nguoc chieu kim dong ho
        }
        
        
        gaugeBorder.rectTransform.DORotate(new Vector3(0, 0, rotateVal), tweenTime);

    }
}
