import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User as FirebaseUser,
  UserCredential
} from 'firebase/auth';
import api from '../lib/api';

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase if API key is available
let firebaseApp: any;
let auth: ReturnType<typeof getAuth> | undefined;

try {
  if (firebaseConfig.apiKey) {
    firebaseApp = initializeApp(firebaseConfig);
    auth = getAuth(firebaseApp);
  }
} catch (error) {
  console.error('Firebase initialization error:', error);
}

// Auth context types
interface AuthContextType {
  user: FirebaseUser | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<UserCredential>;
  signUp: (email: string, password: string, displayName?: string) => Promise<UserCredential>;
  signOut: () => Promise<void>;
  clearError: () => void;
}

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  error: null,
  signIn: async () => {
    throw new Error('AuthContext not initialized');
  },
  signUp: async () => {
    throw new Error('AuthContext not initialized');
  },
  signOut: async () => {
    throw new Error('AuthContext not initialized');
  },
  clearError: () => {},
});

// Auth provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Auth provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state
  useEffect(() => {
    // If Firebase is not initialized, simulate auth state for development
    if (!auth) {
      console.warn('Firebase auth not initialized, using development mode');
      setLoading(false);
      return () => {};
    }

    // Listen for auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // Get ID token for backend verification
        const token = await firebaseUser.getIdToken();
        
        // Store token in localStorage
        localStorage.setItem('auth_token', token);
        
        // Verify token with backend
        try {
          await api.endpoints.auth.verifyToken(token);
        } catch (err) {
          console.error('Error verifying token with backend:', err);
        }
        
        setUser(firebaseUser);
      } else {
        // Clear token from localStorage
        localStorage.removeItem('auth_token');
        setUser(null);
      }
      
      setLoading(false);
    });

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  // Sign in with email and password
  const signIn = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // If Firebase is not initialized, simulate sign in for development
      if (!auth) {
        console.warn('Firebase auth not initialized, simulating sign in');
        setLoading(false);
        return {} as UserCredential;
      }
      
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to sign in');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Sign up with email and password
  const signUp = async (email: string, password: string, displayName?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // If Firebase is not initialized, simulate sign up for development
      if (!auth) {
        console.warn('Firebase auth not initialized, simulating sign up');
        
        // Register with backend
        await api.endpoints.auth.register({ email, password, displayName });
        
        setLoading(false);
        return {} as UserCredential;
      }
      
      // Create user in Firebase
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Register with backend
      await api.endpoints.auth.register({ email, password, displayName });
      
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to sign up');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Sign out
  const signOut = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // If Firebase is not initialized, simulate sign out for development
      if (!auth) {
        console.warn('Firebase auth not initialized, simulating sign out');
        setUser(null);
        localStorage.removeItem('auth_token');
        setLoading(false);
        return;
      }
      
      await firebaseSignOut(auth);
      localStorage.removeItem('auth_token');
    } catch (err: any) {
      setError(err.message || 'Failed to sign out');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Clear error
  const clearError = () => setError(null);

  // Context value
  const value = {
    user,
    loading,
    error,
    signIn,
    signUp,
    signOut,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;
