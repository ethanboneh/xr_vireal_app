using UnityEngine;
using UnityEngine.Networking; // Required for UnityWebRequest
using System.Collections;

public class MaterialCycler : MonoBehaviour
{
    [Tooltip("URL for Flask server to fetch images.")]
    public string imageURL = "http://3.145.161.54:5000/vrside"; // URL to the Flask server
    public float cycleInterval = 5f; // Interval in seconds between GET requests

    private Renderer objectRenderer; // Reference to the GameObject's Renderer
    private Material skyboxMaterial; // Reference to the Skybox material (for Skybox updates)

    void Start()
    {
        // Try to get the Renderer component
        objectRenderer = GetComponent<Renderer>();

        if (objectRenderer == null)
        {
            // If no Renderer found, check if the object is supposed to update the Skybox
            if (RenderSettings.skybox != null)
            {
                skyboxMaterial = RenderSettings.skybox;
                Debug.Log("Skybox material found, updating the Skybox texture.");
            }
            else
            {
                Debug.LogError("No Renderer found, and no Skybox material is set.");
                return;
            }
        }

        // Start the coroutine to fetch the texture and update it at regular intervals
        StartCoroutine(FetchImageAndApply());
    }

    IEnumerator FetchImageAndApply()
    {
        while (true)
        {
            // Make the GET request to the Flask server to fetch the image
            UnityWebRequest request = UnityWebRequestTexture.GetTexture(imageURL);
            yield return request.SendWebRequest();

            if (request.isNetworkError || request.isHttpError)
            {
                Debug.LogError("Failed to load image: " + request.error);
            }
            else
            {
                // Extract the texture from the response
                Texture2D texture = ((DownloadHandlerTexture)request.downloadHandler).texture;

                // Apply texture to the material or Skybox
                if (objectRenderer != null)
                {
                    // Apply the texture to the object's material if Renderer is available
                    objectRenderer.material.mainTexture = texture;
                    Debug.Log("Texture applied to object material from: " + request.uri);
                }
                else if (skyboxMaterial != null)
                {
                    // Apply texture to the Skybox material if Renderer is not available
                    skyboxMaterial.SetTexture("_MainTex", texture);
                    Debug.Log("Texture applied to Skybox from: " + request.uri);
                }
            }

            // Wait for the specified interval before making the next GET request
            yield return new WaitForSeconds(cycleInterval);
        }
    }
}