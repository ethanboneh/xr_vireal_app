using UnityEngine;
using TMPro;

public class LoveCounter : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private int hearts = 87;
    private bool loved = false;
    private TextMeshProUGUI _text;
    void Start()
    {
        _text = GetComponent<TextMeshProUGUI>();
        UpdateText();
    }

    public void UpdateCounter()
    {
        if (!loved) {
            hearts += 1;
            loved = true;
        }
        else {
            hearts -= 1;
            loved = false;
        }
        UpdateText();
    }

    // Update is called once per frame
    private void UpdateText()
    {
       _text.text = hearts.ToString();
    }
}
