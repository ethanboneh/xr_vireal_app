import PhotoPreviewSection from '@/components/MediaPreviewSection';
import { AntDesign } from '@expo/vector-icons';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { Audio } from 'expo-av';
import { useRef, useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, Platform } from 'react-native';

const SERVER_URL = 'http://3.145.161.54:5000/upload';

export default function Camera() {
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [audioPermission, requestAudioPermission] = Audio.usePermissions();
  const [media, setMedia] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaType, setMediaType] = useState<'photo' | 'video'>('photo');
  const cameraRef = useRef<CameraView | null>(null);
  const recordingPromiseRef = useRef<Promise<any> | null>(null);

  if (!permission || !audioPermission) {
    return <View />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <Button onPress={requestPermission} title="grant permission" />
      </View>
    );
  }
  if (!audioPermission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <Button onPress={requestAudioPermission} title="grant permission" />
      </View>
    );
  }

  function toggleCameraFacing() {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  }

  const handleTakePhoto = async () => {
    if(cameraRef.current) {
      const options = {
        quality: 1,
        base64: true,
        exif: false
      };
      const takenPhoto = await cameraRef.current.takePictureAsync(options);
      setMedia(takenPhoto);
      setMediaType('photo');
    }
  };

  const handleStartRecording = async () => {
    if (cameraRef.current && !isRecording) {
      try {
        setIsRecording(true);
        setMediaType('video');
        const videoOptions = {};
        recordingPromiseRef.current = cameraRef.current.recordAsync(videoOptions);
      } catch (error) {
        console.error('Recording error:', error);
      }
    }
  };

  const handleStopRecording = async () => {
    if (cameraRef.current) {
      try {
        setIsRecording(false);
        await cameraRef.current.stopRecording();

        if (recordingPromiseRef.current) {
          const recordedVideo = await recordingPromiseRef.current;
          setMedia(recordedVideo);
          recordingPromiseRef.current = null;
        }
      } catch (error) {
        console.error("Recording stop error:", error);
      }
    }
  };

  const handleRetake = () => {
    setMedia(null);
    setMediaType('photo');
  };

  const handleUpload = async () => {
    if (!media) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      const uri = Platform.OS === 'ios' ? media.uri.replace('file://', '') : media.uri;
      
      formData.append('file', {
        uri: uri,
        type: mediaType === 'photo' ? 'image/jpeg' : 'video/mp4',
        name: mediaType === 'photo' ? 'photo.jpg' : 'video.mp4'
      } as any);

      const response = await fetch(SERVER_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      alert(`${mediaType === 'photo' ? 'Photo' : 'Video'} uploaded successfully!`);
      setMedia(null);
    } catch (error) {
      alert(`Failed to upload ${mediaType}. Please try again.`);
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  if(media) {
    return (
      <PhotoPreviewSection 
        media={media}
        mediaType={mediaType}
        handleRetake={handleRetake}
        handleUpload={handleUpload}
        isUploading={isUploading}
      />
    );
  }

  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing={facing} ref={cameraRef} mode={isRecording ? 'video' : 'video'}>
        <View style={styles.header}>
          <Text style={styles.titleText}>ViReal</Text>
          <Text style={styles.subtitleText}>between worlds</Text>
        </View>
        <View style={styles.footer}>
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
              <AntDesign name='retweet' size={44} color='white' />
            </TouchableOpacity>
            <TouchableOpacity 
              style={[
                styles.button,
                styles.centerButton,
                isRecording && styles.recordingButton
              ]} 
              onPress={isRecording ? handleStopRecording : (mediaType === 'photo' ? handleTakePhoto : handleStartRecording)}
            >
              <AntDesign 
                name={mediaType === 'photo' ? 'camera' : (isRecording ? 'pause' : 'caretright')} 
                size={44} 
                color='white' 
              />
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.button} 
              onPress={() => setMediaType(current => current === 'photo' ? 'video' : 'photo')}
            >
              <AntDesign 
                name={mediaType === 'photo' ? 'caretright' : 'camera'} 
                size={44} 
                color='white' 
              />
            </TouchableOpacity>
          </View>
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  message: {
    textAlign: 'center',
    paddingBottom: 10,
  },
  camera: {
    flex: 1,
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    alignItems: 'center',
  },
  titleText: {
    color: 'white',
    fontSize: 36,
    fontWeight: '700',
    letterSpacing: 2,
    textShadowColor: 'rgba(0, 0, 0, 0.75)',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 5,
  },
  subtitleText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 16,
    fontWeight: '400',
    letterSpacing: 4,
    marginTop: 5,
    fontStyle: 'italic',
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 120,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  button: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    borderRadius: 10,
    padding: 10,
    width: 64,
    height: 64,
  },
  centerButton: {
    backgroundColor: '#666',
    width: 72,
    height: 72,
    borderRadius: 36,
    borderWidth: 3,
    borderColor: '#999',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 0,
  },
  recordingButton: {
    backgroundColor: '#FF4444',
    width: 72,
    height: 72,
    borderRadius: 36,
  },
});