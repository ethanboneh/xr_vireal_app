// components/ExplorePanel.tsx
import React from 'react';
import {
  TouchableOpacity,
  Image,
  StyleSheet,
  Dimensions,
  ImageSourcePropType,
} from 'react-native';

const { width, height } = Dimensions.get('window');

interface ExplorePanelProps {
  thumbnail: ImageSourcePropType;  // Updated type to handle local images
  id: string;
  onPress: (id: string) => void;
}

export const ExplorePanel: React.FC<ExplorePanelProps> = ({ 
  thumbnail, 
  id, 
  onPress 
}) => (
  <TouchableOpacity
    style={styles.panel}
    onPress={() => onPress(id)}
    activeOpacity={0.7}
  >
    <Image
      source={thumbnail}  // Now directly using the required image
      style={styles.thumbnail}
      resizeMode="cover"
    />
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  panel: {
    width: width * 0.9,
    height: height * 0.6,
    marginVertical: 8,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#2A2A2A',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    alignSelf: 'center',
  },
  thumbnail: {
    width: '100%',
    height: '100%',
  },
});

export default ExplorePanel;