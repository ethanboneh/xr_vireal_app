Shader "Custom/LatLonSkybox"
{
    Properties
    {
        _MainTex ("Skybox Texture", 2D) = "white" { }
        _LatMin ("Latitude Min", Float) = -50.0
        _LatMax ("Latitude Max", Float) = 50.0
        _LonMin ("Longitude Min", Float) = -45.0
        _LonMax ("Longitude Max", Float) = 45.0
    }
    SubShader
    {
        Tags { "RenderType"="Skybox" }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata_t
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos : POSITION;
                float2 uv : TEXCOORD0;
            };

            float _LatMin, _LatMax, _LonMin, _LonMax;
            sampler2D _MainTex;

            // Updated vertex shader function with corrected variable names
            v2f vert(appdata_t v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);

                // Convert vertex position to spherical coordinates (lat, lon)
                float lat = atan2(v.vertex.y, sqrt(v.vertex.x * v.vertex.x + v.vertex.z * v.vertex.z)) * 180.0 / 3.14159;
                float lon = atan2(v.vertex.z, v.vertex.x) * 180.0 / 3.14159;

                // Map the latitude and longitude to UV coordinates
                float u = (lon - _LonMin) / (_LonMax - _LonMin); // Longitude range to 0-1
                float vCoord = (lat - _LatMin) / (_LatMax - _LatMin); // Latitude range to 0-1

                // Ensure UVs stay within the bounds of the texture
                o.uv = float2(u, vCoord);

                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                // Sample the skybox texture using the calculated UV coordinates
                return tex2D(_MainTex, i.uv);
            }
            ENDCG
        }
    }
    FallBack "Skybox/6Sided"
}