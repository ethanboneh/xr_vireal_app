// import { Image, StyleSheet, Platform } from 'react-native';

// import { HelloWave } from '@/components/HelloWave';
// import ParallaxScrollView from '@/components/ParallaxScrollView';
// import { ThemedText } from '@/components/ThemedText';
// import { ThemedView } from '@/components/ThemedView';

// export default function HomeScreen() {
//   return (
//     <ParallaxScrollView
//       headerBackgroundColor={{ light: '#A1CEDC', dark: '#1D3D47' }}
//       headerImage={
//         <Image
//           source={require('@/assets/images/partial-react-logo.png')}
//           style={styles.reactLogo}
//         />
//       }>
//       <ThemedView style={styles.titleContainer}>
//         <ThemedText type="title">Welcome!</ThemedText>
//         <HelloWave />
//       </ThemedView>
//       <ThemedView style={styles.stepContainer}>
//         <ThemedText type="subtitle">Step 1: Try it</ThemedText>
//         <ThemedText>
//           Edit <ThemedText type="defaultSemiBold">app/(tabs)/index.tsx</ThemedText> to see changes.
//           Press{' '}
//           <ThemedText type="defaultSemiBold">
//             {Platform.select({ ios: 'cmd + d', android: 'cmd + m' })}
//           </ThemedText>{' '}
//           to open developer tools.
//         </ThemedText>
//       </ThemedView>
//       <ThemedView style={styles.stepContainer}>
//         <ThemedText type="subtitle">Step 2: Explore</ThemedText>
//         <ThemedText>
//           Tap the Explore tab to learn more about what's included in this starter app.
//         </ThemedText>
//       </ThemedView>
//       <ThemedView style={styles.stepContainer}>
//         <ThemedText type="subtitle">Step 3: Get a fresh start</ThemedText>
//         <ThemedText>
//           When you're ready, run{' '}
//           <ThemedText type="defaultSemiBold">npm run reset-project</ThemedText> to get a fresh{' '}
//           <ThemedText type="defaultSemiBold">app</ThemedText> directory. This will move the current{' '}
//           <ThemedText type="defaultSemiBold">app</ThemedText> to{' '}
//           <ThemedText type="defaultSemiBold">app-example</ThemedText>.
//         </ThemedText>
//       </ThemedView>
//     </ParallaxScrollView>
//   );
// }

// const styles = StyleSheet.create({
//   titleContainer: {
//     flexDirection: 'row',
//     alignItems: 'center',
//     gap: 8,
//   },
//   stepContainer: {
//     gap: 8,
//     marginBottom: 8,
//   },
//   reactLogo: {
//     height: 178,
//     width: 290,
//     bottom: 0,
//     left: 0,
//     position: 'absolute',
//   },
// });

// app/(tabs)/explore.tsx
import React from 'react';
import {
  StyleSheet,
  FlatList,
  SafeAreaView,
  Dimensions,
  Alert,
  ImageSourcePropType,
  View,
  Text,
  Platform,
} from 'react-native';
import { ExplorePanel } from '../../components/ExplorePanel';

const { width, height } = Dimensions.get('window');

const FLASK_SERVER_URL = 'http://3.145.161.54:5000/analytics';

const scenes = [
  { 
    id: '1', 
    thumbnail: require('@/assets/images/beach.jpg'), 
    title: 'Beach VR' 
  },
  { 
    id: '2', 
    thumbnail: require('@/assets/images/city.jpg'), 
    title: 'City Night' 
  },
  { 
    id: '3', 
    thumbnail: require('@/assets/images/mountain.jpg'), 
    title: 'Mountain View' 
  },
  { 
    id: '4', 
    thumbnail: require('@/assets/images/concert.jpg'), 
    title: 'Concert View' 
  },
];

export default function ExploreScreen() {
  const handlePanelClick = async (sceneId: string) => {
    try {
      const response = await fetch(`${FLASK_SERVER_URL}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scene_id: sceneId,
          timestamp: new Date().toISOString(),
          platform: Platform.OS
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Server response:', data);
    } catch (error) {
      console.error('Error sending click to server:', error);
      Alert.alert(
        'Connection Error',
        'Unable to connect to server. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const renderPanel = ({ item }) => (
    <ExplorePanel
      thumbnail={item.thumbnail}
      id={item.id}
      onPress={handlePanelClick}
    />
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerText}>ViReal: Explore Other Worlds</Text>
      </View>
      <FlatList
        data={scenes}
        renderItem={renderPanel}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        snapToInterval={height * 0.6 + 16}
        decelerationRate="fast"
        snapToAlignment="start"
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    width: '100%',
    paddingVertical: 15,
    paddingHorizontal: 20,
    backgroundColor: '#000', // Same as container background
    borderBottomWidth: 1,
    borderBottomColor: '#333', // Subtle border
    marginBottom: 5,
  },
  headerText: {
    color: '#fff',
    fontSize: 30,
    fontWeight: '600',
    textAlign: 'center',
  },
  listContainer: {
    paddingVertical: 8,
  },
});