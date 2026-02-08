import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { 
  Home, 
  Activity, 
  Users, 
  Settings 
} from 'lucide-react-native';

import HomeScreen from './src/screens/HomeScreen';
import WorkflowsScreen from './src/screens/WorkflowsScreen';
import AgentsScreen from './src/screens/AgentsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();
const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer>
        <StatusBar style="light" />
        <Tab.Navigator
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1e1b4b',
            },
            headerTintColor: '#fff',
            tabBarStyle: {
              backgroundColor: '#1e1b4b',
              borderTopColor: '#4c1d95',
            },
            tabBarActiveTintColor: '#a855f7',
            tabBarInactiveTintColor: '#9ca3af',
          }}
        >
          <Tab.Screen
            name="Home"
            component={HomeScreen}
            options={{
              tabBarIcon: ({ color, size }) => (
                <Home color={color} size={size} />
              ),
            }}
          />
          <Tab.Screen
            name="Workflows"
            component={WorkflowsScreen}
            options={{
              tabBarIcon: ({ color, size }) => (
                <Activity color={color} size={size} />
              ),
            }}
          />
          <Tab.Screen
            name="Agents"
            component={AgentsScreen}
            options={{
              tabBarIcon: ({ color, size }) => (
                <Users color={color} size={size} />
              ),
            }}
          />
          <Tab.Screen
            name="Settings"
            component={SettingsScreen}
            options={{
              tabBarIcon: ({ color, size }) => (
                <Settings color={color} size={size} />
              ),
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </QueryClientProvider>
  );
}
