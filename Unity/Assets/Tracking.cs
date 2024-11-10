using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class Tracking : MonoBehaviour
{
    // URL of the Flask server
    public string serverUrl = "http://3.145.161.54:5000/gyro";

    // Time interval for sending data (in seconds)
    public float sendInterval = 0.1f;

    void Start()
    {
        // Start the coroutine to send data continuously
        StartCoroutine(SendDataContinuously());
    }

    IEnumerator SendDataContinuously()
    {
        while (true)
        {
            // Get the position and rotation of the object
            Vector3 position = transform.position;
            Vector3 rotation = transform.eulerAngles;

            // Manually create JSON to exactly match Flask's expected structure
            string jsonData = $"{{" +
                              $"\"positionX\": {position.x}, " +
                              $"\"positionY\": {position.y}, " +
                              $"\"positionZ\": {position.z}, " +
                              $"\"rotationX\": {rotation.x}, " +
                              $"\"rotationY\": {rotation.y}, " +
                              $"\"rotationZ\": {rotation.z}" +
                              $"}}";

            Debug.Log($"Sending JSON: {jsonData}");

            // Convert JSON string to byte array
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);

            // Create the UnityWebRequest
            using (UnityWebRequest request = new UnityWebRequest(serverUrl, "POST"))
            {
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");

                // Send the request and wait for a response
                yield return request.SendWebRequest();

                // Handle the response
                if (request.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"Error sending data: {request.error}");
                }
                else
                {
                    Debug.Log("Data sent successfully!");
                }
            }

            // Wait for the specified interval before sending the next request
            yield return new WaitForSeconds(sendInterval);
        }
    }
}