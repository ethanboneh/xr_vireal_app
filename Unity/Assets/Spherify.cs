using UnityEngine;

public class Spherify : MonoBehaviour
{
    public float radius = 1f; // The radius of the sphere
    public float latMin = -50f; // Min latitude (corresponding to 100 degrees)
    public float latMax = 50f;  // Max latitude
    public float lonMin = -45f; // Min longitude (corresponding to 90 degrees)
    public float lonMax = 45f;  // Max longitude
    public int longitudeSegments = 50;  // Number of longitude segments
    public int latitudeSegments = 50;   // Number of latitude segments

    public Material sphereMaterial; // Material to apply to the sphere

    void Start()
    {
        // Generate the sphere fragment mesh
        Mesh mesh = GenerateSphereFragment();
        MeshFilter meshFilter = GetComponent<MeshFilter>();
        meshFilter.mesh = mesh;

        // Apply the material to the renderer
        Renderer renderer = GetComponent<Renderer>();
        if (sphereMaterial != null && renderer != null)
        {
            renderer.material = sphereMaterial; // Set the material to the object
        }
    }

    Mesh GenerateSphereFragment()
    {
        Mesh mesh = new Mesh();
        Vector3[] vertices = new Vector3[(latitudeSegments + 1) * (longitudeSegments + 1)];
        int[] triangles = new int[latitudeSegments * longitudeSegments * 6]; // Each quad is split into two triangles
        Vector2[] uv = new Vector2[vertices.Length]; // UV coordinates for texture mapping

        float latStep = (latMax - latMin) / latitudeSegments;
        float lonStep = (lonMax - lonMin) / longitudeSegments;

        int vertexIndex = 0;
        int triangleIndex = 0;

        // Create the vertices and UVs
        for (int lat = 0; lat <= latitudeSegments; lat++)
        {
            for (int lon = 0; lon <= longitudeSegments; lon++)
            {
                // Calculate the latitude and longitude in radians
                float latAngle = Mathf.Deg2Rad * (latMin + lat * latStep);
                float lonAngle = Mathf.Deg2Rad * (lonMin + lon * lonStep);

                // Convert spherical to Cartesian coordinates
                float x = radius * Mathf.Cos(latAngle) * Mathf.Cos(lonAngle);
                float y = radius * Mathf.Sin(latAngle);
                float z = radius * Mathf.Cos(latAngle) * Mathf.Sin(lonAngle);

                // Store the vertex
                vertices[vertexIndex] = new Vector3(x, y, z);

                // Assign UV coordinates
                uv[vertexIndex] = new Vector2((float)lon / longitudeSegments, (float)lat / latitudeSegments);

                // Create triangles for the mesh
                if (lat < latitudeSegments && lon < longitudeSegments)
                {
                    int current = vertexIndex;
                    int nextLat = current + longitudeSegments + 1;
                    int nextLon = current + 1;
                    int nextLatLon = nextLat + 1;

                    // First triangle (in reverse winding order)
                    triangles[triangleIndex++] = nextLon;
                    triangles[triangleIndex++] = nextLat;
                    triangles[triangleIndex++] = current;

                    // Second triangle (in reverse winding order)
                    triangles[triangleIndex++] = nextLon;
                    triangles[triangleIndex++] = nextLatLon;
                    triangles[triangleIndex++] = nextLat;
                }

                vertexIndex++;
            }
        }

        // Assign vertices, triangles, and UVs to the mesh
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uv;

        // Recalculate normals
        mesh.RecalculateNormals();

        // Reverse the normals by multiplying each normal by -1
        Vector3[] normals = mesh.normals;
        for (int i = 0; i < normals.Length; i++)
        {
            normals[i] = -normals[i];
        }
        mesh.normals = normals;

        return mesh;
    }
}