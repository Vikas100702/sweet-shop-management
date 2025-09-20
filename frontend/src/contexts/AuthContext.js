// /**
//  * Authentication Context for managing user state
//  * Provides authentication functionality throughout the app
//  */
// import React, {createContext, useContext, useState, useEffect} from "react";
// import apiService from "../services/api";

// // Create authentication context
// const AuthContext = createContext();

// /**
//  * Custom hook to use authentication context
//  * @returns {Object} Authentication context value
//  */
// export const useAuth = () => {
//     const context = useContext(AuthContext);

//     if (!context) {
//         throw new Error('useAuth must be used within an AuthProvider');
//     }
//     return context;
// };

// /**
//  * Authentication Provider Component
//  * Manages authentication state and provides auth methods to children
//  */
// export const AuthProvider = ({children}) => {
//     const [user, setUser] = useState(null);
//     const [loading, setLoading] = useState(true);

//     /**
//    * Initialize authentication state on app load
//    * Check if user is already logged in from localStorage
//    */

//     useEffect(() => {
//         initializeAuth();
//     }, []);

//     /**
//    * Initialize authentication state
//    * Verify stored token is still valid
//    */

//     const initializeAuth = async () => {
//         try {
//             // Check if we have stored auth data
//             if (apiService.isAuthenticated()) {
//                 const storedUser = apiService.getStoredUser();
//                 if (storedUser) {
//                     // Verify token is still valid by fetching current user
//                     const currentUser = await apiService.getCurrentUser();
//                     setUser(currentUser);

//                     // Update stored user data in case it changed
//                     localStorage.setItem('user', JSON.stringify(currentUser));
//                 }
//             }
//         } catch (error) {
//             console.error('Auth initialization failed:', error);

//             // Clear invalid auth data
//             apiService.clearAuthData();
//         } finally {
//             setLoading(false);
//         }
//     };

//     /**
//    * Register a new user account
//    * @param {Object} registerData - Registration form data
//    * @returns {Object} Success status and message
//    */
//   const register = async (registerData) => {
//     try {
//         setLoading(true);
        
//         // Register user
//         await apiService.register(registerData);

//         // Auto-login after successful registration
//         const loginResult = await login({
//             username: registerData.username,
//             password: registerData.password,
//         });

//         if (loginResult.success) {
//             return {
//                 success: true,
//                 message: 'Account created successfully.',
//             };
//         }

//         return loginResult;
//     } catch (error) {
//         const errorMessage = apiService.getErrorMessage(error);
//       return { 
//         success: false, 
//         message: errorMessage 
//       };
//     } finally {
//         setLoading(false);
//     }
//   };

//   /**
//    * Logout current user
//    * Clear authentication data and reset state
//    */
//    const logout = () => {
//     apiService.clearAuthData();
//     setUser(null);
//   };

//   /**
//    * Refresh current user data
//    * Useful after profile updates or role changes
//    */
//   const refreshUser = async () => {
//     try {
//       if (apiService.isAuthenticated()) {
//         const currentUser = await apiService.getCurrentUser();
//         setUser(currentUser);
//         localStorage.setItem('user', JSON.stringify(currentUser));
//       }
//     } catch (error) {
//       console.error('Failed to refresh user:', error);
//       logout();
//     }
//   };

//   // Context value with all auth methods and state
//   const value = {
//     user,                                    // Current user object
//     loading,                                 // Loading state for auth operations
//     login,                                   // Login method
//     register,                               // Registration method
//     logout,                                 // Logout method
//     refreshUser,                            // Refresh user data method
//     isAdmin: user?.is_admin || false,       // Check if current user is admin
//     isAuthenticated: !!user,                // Check if user is logged in
//   };

//   return (
//     <AuthContext.Provider value={value}>
//       {children}
//     </AuthContext.Provider>
//   );
// };

/**
 * AuthContext.js
 * Manages authentication state and provides login, logout, and registration methods
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import apiService from "../services/api"; // wrapper for axios/fetch
import { showSuccess, showError } from "../components/Toast";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  /**
   * Load user from localStorage on startup
   */
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");

    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  /**
   * Login user with API
   * @param {Object} credentials { username, password }
   */
  const login = async ({ username, password }) => {
    try {
      const response = await apiService.login({
        username,
        password,
      });

      if (response.access_token) {
        const userData = { username, token: response.access_token };

        // Save to state + localStorage
        setUser(userData);
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", response.access_token);

        return { success: true, message: "Login successful" };
      }

      return { success: false, message: "Invalid credentials" };
    } catch (error) {
      return { success: false, message: apiService.getErrorMessage(error) };
    }
  };

  /**
   * Register new user
   * @param {Object} data { username, email, password }
   */
  const register = async (data) => {
    try {
      await apiService.register(data);
      showSuccess("Registration successful! Please log in.");
      return { success: true };
    } catch (error) {
      showError(apiService.getErrorMessage(error));
      return { success: false };
    }
  };

  /**
   * Logout user
   */
  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    showSuccess("Logged out successfully");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        register,
        loading,
        isAuthenticated: !!user,
        isAdmin: user?.username === "admin", // quick check
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
