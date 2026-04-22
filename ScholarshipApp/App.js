import React, { useRef, useState } from 'react';
import { StyleSheet, SafeAreaView, BackHandler, Platform, ActivityIndicator, View } from 'react-native';
import { WebView } from 'react-native-webview';
import { StatusBar } from 'expo-status-bar';
import Constants from 'expo-constants';

// Extract development IP directly from the Metro bundler connection
const debuggerHost = Constants.expoConfig?.hostUri;

// If we're in Dev Mode and connected to Metro, we dynamically form the IP.
// Otherwise (For Production builds), use this production domain string.
const PRODUCTION_DOMAIN = 'https://myscholarshipapp.com'; // Change this later

const WEBVIEW_URL = __DEV__ && debuggerHost
  ? `http://${debuggerHost.split(':')[0]}` // Connects to Port 80
  : PRODUCTION_DOMAIN;

export default function App() {
  const webViewRef = useRef(null);
  const [canGoBack, setCanGoBack] = useState(false);

  // Handle hardware back button for Android
  React.useEffect(() => {
    if (Platform.OS === 'android') {
      const backAction = () => {
        if (canGoBack && webViewRef.current) {
          webViewRef.current.goBack();
          return true; // prevent default behavior (exit app)
        }
        return false;
      };

      const backHandler = BackHandler.addEventListener(
        'hardwareBackPress',
        backAction
      );

      return () => backHandler.remove();
    }
  }, [canGoBack]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />
      <WebView
        ref={webViewRef}
        source={{ uri: WEBVIEW_URL }}
        style={styles.webview}
        onNavigationStateChange={(navState) => {
          setCanGoBack(navState.canGoBack);
        }}
        startInLoadingState={true}
        renderLoading={() => (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#0000ff" />
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  webview: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    height: '100%',
    width: '100%',
    backgroundColor: 'white',
  }
});
