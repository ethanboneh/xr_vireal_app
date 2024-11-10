import { Fontisto, AntDesign } from '@expo/vector-icons';
import { CameraCapturedPicture } from 'expo-camera';
import React from 'react';
import { TouchableOpacity, SafeAreaView, Image, StyleSheet, View } from 'react-native';
import { Video, ResizeMode } from 'expo-av';

interface MediaPreviewProps {
    media: CameraCapturedPicture | { uri: string };
    mediaType: 'photo' | 'video';
    handleRetake: () => void;
    handleUpload: () => void;
    isUploading: boolean;
}

const MediaPreviewSection = ({
    media,
    mediaType,
    handleRetake,
    handleUpload,
    isUploading
}: MediaPreviewProps) => (
  <SafeAreaView style={styles.container}>
    <View style={styles.box}>
        {mediaType === 'photo' ? (
            <Image
                style={styles.previewContainer}
                source={{
                    uri: 'base64' in media 
                        ? 'data:image/jpg;base64,' + media.base64 
                        : media.uri
                }}
            />
        ) : (
            <Video
                style={styles.previewContainer}
                source={{ uri: media.uri }}
                useNativeControls
                resizeMode={ResizeMode.CONTAIN}
                isLooping
            />
        )}
    </View>

    <View style={styles.buttonContainer}>
        <TouchableOpacity 
            style={styles.button} 
            onPress={handleRetake}
        >
            <Fontisto name='trash' size={36} color='white' />
        </TouchableOpacity>
        <TouchableOpacity 
            style={[styles.button, isUploading && styles.disabledButton]} 
            onPress={handleUpload}
            disabled={isUploading}
        >
            <AntDesign name='upload' size={36} color='white' />
        </TouchableOpacity>
    </View>
  </SafeAreaView>
);

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'black',
        alignItems: 'center',
        justifyContent: 'center'
    },
    box: {
        borderRadius: 15,
        width: '95%',
        height: '80%',  // Added fixed height
        backgroundColor: 'rgba(169, 169, 169, 0.3)',
        overflow: 'hidden', // This ensures content doesn't spill out
    },
    previewContainer: {
        width: '100%',  // Changed from 95%
        height: '100%', // Changed from 85%
        borderRadius: 15
    },
    buttonContainer: {
        marginTop: '4%',
        flexDirection: 'row',
        justifyContent: "center",
        width: '100%',
        gap: 20
    },
    button: {
        backgroundColor: '#666', // Matching camera.tsx center button
        width: 64,
        height: 64,
        borderRadius: 32,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 3,
        borderColor: '#999',
    },
    disabledButton: {
        opacity: 0.5
    }
});

export default MediaPreviewSection;